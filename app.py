from flask import Flask, render_template, url_for, flash, redirect, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos SQLite
# Asegúrate de que la ruta sea absoluta para evitar problemas
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here' # ¡Cambia esto por una clave secreta fuerte!

# Configuración para la carga de imágenes
UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite de 16MB para archivos

# Asegúrate de que la carpeta de subida exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Inicialización de SQLAlchemy
db = SQLAlchemy(app)

# Inicialización de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'main.login' # Ruta a la vista de login
login_manager.login_message_category = 'info'

# Definición del modelo de usuario para Flask-Login
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

# Función para cargar usuarios para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Usar Session.get() en lugar de Query.get() para SQLAlchemy 2.0
    return db.session.get(User, int(user_id)) # Corrección para LegacyAPIWarning

# Modelo de Propiedad
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False) # Calle y número
    municipio = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), default="Veracruz") # Por defecto Veracruz
    estado_propiedad = db.Column(db.String(20), nullable=False) # Venta, Renta
    tipo_propiedad = db.Column(db.String(50), nullable=False) # Casa, Departamento, Terreno, Local
    num_habitaciones = db.Column(db.Integer)
    num_banos = db.Column(db.Integer)
    num_medios_banos = db.Column(db.Integer)
    num_estacionamientos = db.Column(db.Integer)
    area_terreno_metros_cuadrados = db.Column(db.Float)
    area_construccion_metros_cuadrados = db.Column(db.Float)
    cuota_mantenimiento = db.Column(db.Float)
    fecha_publicacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relación con las imágenes
    imagenes = db.relationship('PropertyImage', backref='property', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Property('{self.titulo}', '{self.ubicacion}', '{self.precio}')"

# Modelo de Imagen de Propiedad
class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    nombre_archivo = db.Column(db.String(100), nullable=False)
    es_principal = db.Column(db.Boolean, default=False) # Para marcar una imagen como principal

    def __repr__(self):
        return f"PropertyImage('{self.nombre_archivo}', principal={self.es_principal})"

# Blueprint para las rutas principales
main = Blueprint('main', __name__)

# CONSTANTE PARA LA PAGINACIÓN
PROPERTIES_PER_PAGE = 9 # Mostrar 9 propiedades por página (3 filas de 3 cards)

# Ruta para la página de inicio (con filtros de búsqueda y paginación)
@main.route('/')
def home():
    # Obtener parámetros de búsqueda de la URL
    operation = request.args.get('operation')
    property_type = request.args.get('property_type')
    location = request.args.get('location') # Esto será el municipio/zona
    min_bedrooms = request.args.get('min_bedrooms', type=int)
    max_bedrooms = request.args.get('max_bedrooms', type=int)
    price_range = request.args.get('price_range')
    page = request.args.get('page', 1, type=int) # Obtener el número de página, por defecto 1

    # Construir la consulta base
    query = Property.query

    # DEBUG: Imprimir los parámetros recibidos
    print(f"DEBUG - Operation: {operation}, Property Type: {property_type}, Location: {location}, Min Beds: {min_bedrooms}, Max Beds: {max_bedrooms}, Price Range: {price_range}, Page: {page}")


    # Aplicar filtros si existen
    if operation:
        # Corrección: Asegurarse de que 'operation' se capitalice correctamente para la base de datos
        # 'comprar' -> 'Venta', 'rentar' -> 'Renta'
        if operation.lower() == 'comprar':
            query = query.filter_by(estado_propiedad='Venta')
            print("DEBUG - Filtrando por estado_propiedad='Venta'")
        elif operation.lower() == 'rentar':
            query = query.filter_by(estado_propiedad='Renta')
            print("DEBUG - Filtrando por estado_propiedad='Renta'")
    
    if property_type:
        query = query.filter_by(tipo_propiedad=property_type.capitalize())
        print(f"DEBUG - Filtrando por tipo_propiedad='{property_type.capitalize()}'")
    
    if location:
        # Filtrar por municipio (ya que la ubicación en el modal es el municipio)
        query = query.filter(Property.municipio.ilike(f'%{location}%'))
        print(f"DEBUG - Filtrando por municipio='{location}'")
    
    if min_bedrooms is not None:
        query = query.filter(Property.num_habitaciones >= min_bedrooms)
        print(f"DEBUG - Filtrando por min_habitaciones='{min_bedrooms}'")
    
    if max_bedrooms is not None:
        query = query.filter(Property.num_habitaciones <= max_bedrooms)
        print(f"DEBUG - Filtrando por max_habitaciones='{max_bedrooms}'")
    
    if price_range:
        # Definir los rangos de precios
        price_ranges = {
            '0-500000': (0, 500000),
            '500000-1000000': (500000, 1000000),
            '1000000-2000000': (1000000, 2000000),
            '2000000-3000000': (2000000, 3000000),
            '3000000-4000000': (3000000, 4000000),
            '4000000-5000000': (4000000, 5000000),
            '5000000-6000000': (5000000, 6000000),
            '6000000-7000000': (6000000, 7000000),
            '7000000-8000000': (7000000, 8000000),
            '8000000-9000000': (8000000, 9000000),
            '9000000-10000000': (9000000, 10000000),
            '10000000-max': (10000000, float('inf')) # Usar infinito para el límite superior
        }
        
        if price_range in price_ranges:
            min_price, max_price = price_ranges[price_range]
            query = query.filter(Property.precio >= min_price)
            if max_price != float('inf'):
                query = query.filter(Property.precio <= max_price)
            print(f"DEBUG - Filtrando por rango de precio: {min_price}-{max_price}")

    # Aplicar paginación
    # .paginate() es el método de paginación. Recibe el número de página, elementos por página y si debe generar un error 404 si la página está fuera de rango.
    # El objeto `pagination` tendrá atributos como `items` (las propiedades de la página actual), `pages` (número total de páginas), `page` (página actual), `has_next`, `has_prev`, etc.
    pagination = query.order_by(Property.fecha_publicacion.desc()).paginate(page=page, per_page=PROPERTIES_PER_PAGE, error_out=False)
    
    # Pasamos el objeto pagination completo a la plantilla
    return render_template('index.html', pagination=pagination, propiedades=pagination.items)

# Ruta para el login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Credenciales incorrectas. Por favor, inténtalo de nuevo.', 'danger')
    return render_template('login.html')

# Ruta para el logout
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('main.home'))

# Ruta para añadir una propiedad
@main.route('/add_property', methods=['GET', 'POST'])
@login_required
def add_property():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        ubicacion = request.form['ubicacion']
        municipio = request.form['municipio']
        estado_propiedad = request.form['estado_propiedad']
        tipo_propiedad = request.form['tipo_propiedad']
        
        # Obtener valores numéricos, si no están presentes, se guardan como None
        num_habitaciones = request.form.get('num_habitaciones', type=int)
        num_banos = request.form.get('num_banos', type=int)
        num_medios_banos = request.form.get('num_medios_banos', type=int)
        num_estacionamientos = request.form.get('num_estacionamientos', type=int)
        area_terreno_metros_cuadrados = request.form.get('area_terreno_metros_cuadrados', type=float)
        area_construccion_metros_cuadrados = request.form.get('area_construccion_metros_cuadrados', type=float)
        cuota_mantenimiento = request.form.get('cuota_mantenimiento', type=float)

        nueva_propiedad = Property(
            titulo=titulo,
            descripcion=descripcion,
            precio=precio,
            ubicacion=ubicacion,
            municipio=municipio,
            estado_propiedad=estado_propiedad,
            tipo_propiedad=tipo_propiedad,
            num_habitaciones=num_habitaciones,
            num_banos=num_banos,
            num_medios_banos=num_medios_banos,
            num_estacionamientos=num_estacionamientos,
            area_terreno_metros_cuadrados=area_terreno_metros_cuadrados,
            area_construccion_metros_cuadrados=area_construccion_metros_cuadrados,
            cuota_mantenimiento=cuota_mantenimiento
        )
        db.session.add(nueva_propiedad)
        db.session.commit()

        # Manejo de la carga de imágenes
        if 'imagenes' in request.files:
            files = request.files.getlist('imagenes')
            principal_set = False
            for file in files:
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    # Marcar la primera imagen subida como principal si no hay ninguna principal aún
                    is_principal = False
                    if not principal_set:
                        # Si es la primera imagen y no hay otras imágenes para esta propiedad marcadas como principal
                        existing_principal = PropertyImage.query.filter_by(property_id=nueva_propiedad.id, es_principal=True).first()
                        if not existing_principal:
                            is_principal = True
                            principal_set = True

                    nueva_imagen = PropertyImage(
                        property_id=nueva_propiedad.id,
                        nombre_archivo=filename,
                        es_principal=is_principal
                    )
                    db.session.add(nueva_imagen)
            db.session.commit()
        
        flash('Propiedad añadida exitosamente.', 'success')
        return redirect(url_for('main.home'))
    return render_template('add_property.html')

# Ruta para ver el detalle de una propiedad
@main.route('/property/<int:property_id>')
def property_detail(property_id):
    propiedad = db.session.get(Property, property_id)
    if not propiedad:
        # Si la propiedad no se encuentra, redirigir a la página de inicio con un mensaje
        flash('La propiedad solicitada no existe.', 'danger')
        return redirect(url_for('main.home'))
    return render_template('property_detail.html', propiedad=propiedad)

# Ruta para editar una propiedad
@main.route('/edit_property/<int:property_id>', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    propiedad = db.session.get(Property, property_id)
    if not propiedad:
        flash('La propiedad solicitada para editar no existe.', 'danger')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        propiedad.titulo = request.form['titulo']
        propiedad.descripcion = request.form['descripcion']
        propiedad.precio = float(request.form['precio'])
        propiedad.ubicacion = request.form['ubicacion']
        propiedad.municipio = request.form['municipio']
        propiedad.estado_propiedad = request.form['estado_propiedad']
        tipo_propiedad = request.form['tipo_propiedad']

        propiedad.num_habitaciones = request.form.get('num_habitaciones', type=int)
        propiedad.num_banos = request.form.get('num_banos', type=int)
        propiedad.num_medios_banos = request.form.get('num_medios_banos', type=int)
        propiedad.num_estacionamientos = request.form.get('num_estacionamientos', type=int)
        propiedad.area_terreno_metros_cuadrados = request.form.get('area_terreno_metros_cuadrados', type=float)
        propiedad.area_construccion_metros_cuadrados = request.form.get('area_construccion_metros_cuadrados', type=float)
        cuota_mantenimiento = request.form.get('cuota_mantenimiento', type=float)

        # Manejo de eliminación de imágenes existentes
        delete_images_ids = request.form.getlist('delete_images')
        for img_id in delete_images_ids:
            image_to_delete = PropertyImage.query.get(int(img_id))
            if image_to_delete:
                # Eliminar archivo físico
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete.nombre_archivo))
                except OSError as e:
                    print(f"Error al eliminar archivo: {e}")
                db.session.delete(image_to_delete)
        
        # Manejo de la imagen principal
        principal_image_id = request.form.get('principal_image', type=int)
        if principal_image_id:
            # Desmarcar todas las imágenes como principales para esta propiedad
            for img in propiedad.imagenes:
                img.es_principal = False
            # Marcar la nueva imagen principal
            new_principal_image = PropertyImage.query.get(principal_image_id)
            if new_principal_image:
                new_principal_image.es_principal = True
        else: # Si no se seleccionó ninguna, asegurarse de que al menos la primera sea principal
            if propiedad.imagenes:
                # Si no hay ninguna marcada como principal, marcar la primera
                if not any(img.es_principal for img in propiedad.imagenes):
                    propiedad.imagenes[0].es_principal = True


        # Manejo de nuevas imágenes
        if 'imagenes' in request.files:
            files = request.files.getlist('imagenes')
            for file in files:
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    # Determinar si la nueva imagen debe ser principal
                    is_principal = False
                    # Si no hay ninguna imagen principal aún para esta propiedad, la primera que se sube se hace principal
                    if not any(img.es_principal for img in propiedad.imagenes):
                        is_principal = True

                    nueva_imagen = PropertyImage(
                        property_id=propiedad.id,
                        nombre_archivo=filename,
                        es_principal=is_principal
                    )
                    db.session.add(nueva_imagen)

        db.session.commit()
        flash('Propiedad actualizada exitosamente.', 'success')
        return redirect(url_for('main.property_detail', property_id=propiedad.id))
    return render_template('edit_property.html', propiedad=propiedad)

# Ruta para eliminar una propiedad
@main.route('/delete_property/<int:property_id>', methods=['POST'])
@login_required
def delete_property(property_id):
    propiedad = db.session.get(Property, property_id)
    if not propiedad:
        flash('La propiedad solicitada para eliminar no existe.', 'danger')
        return redirect(url_for('main.home'))
    
    # Eliminar imágenes asociadas antes de eliminar la propiedad
    for imagen in propiedad.imagenes:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], imagen.nombre_archivo))
        except OSError as e:
            print(f"Error al eliminar archivo de imagen: {e}")
        db.session.delete(imagen) # Eliminar de la base de datos
    
    db.session.delete(propiedad)
    db.session.commit()
    flash('Propiedad eliminada exitosamente.', 'success')
    return redirect(url_for('main.home'))

# Registrar el Blueprint
app.register_blueprint(main)

# Creación de la base de datos y usuario admin al inicio
with app.app_context():
    db.create_all()
    # Crear usuario admin si no existe
    if not User.query.filter_by(username='admin').first():
        hashed_password = generate_password_hash('adminpassword', method='pbkdf2:sha256')
        admin_user = User(username='admin', password=hashed_password)
        db.session.add(admin_user)
        db.session.commit()
        print("Usuario 'admin' creado.")

if __name__ == '__main__':
    app.run(debug=True)