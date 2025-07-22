# app.py

# 1. Importaciones
# ==============================================================================
# Aquí se importan todas las librerías y módulos que tu aplicación va a necesitar.
# Es lo primero porque el resto del código usará elementos de estos módulos.
from flask import Flask, render_template, url_for, flash, redirect, request, Blueprint, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta # 'timedelta' es útil para duraciones de sesión
import os # Para interactuar con el sistema de archivos y variables de entorno
from werkzeug.utils import secure_filename # Para nombres de archivo seguros al subir
from sqlalchemy import or_ # Para consultas de base de datos complejas
from config import config_by_name # Tu módulo de configuración de entornos
from forms import LoginForm, PropertyForm, EditPropertyForm # Tus formularios definidos en forms.py

# 2. Funciones Auxiliares
# ==============================================================================
# Se definen funciones que son útiles globalmente en tu aplicación, pero que
# no dependen directamente de la instancia de 'app' o 'db' para ser definidas.
# Deben estar disponibles antes de que se llamen en las rutas.
def allowed_file(filename):
    """
    Verifica si la extensión de un archivo es permitida para la subida.
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 3. Inicialización de la Aplicación Flask
# ==============================================================================
# Se crea la instancia principal de tu aplicación Flask.
# Es lo primero que necesita existir para que las extensiones se puedan enlazar a ella.
app = Flask(__name__)

# 4. Carga de Configuración de Entornos
# ==============================================================================
# Se carga la configuración de tu archivo 'config.py' en la aplicación.
# Esto debe hacerse después de que 'app' se inicialice, pero antes de que
# las extensiones que dependen de la configuración (como SQLAlchemy para la DB URI)
# sean inicializadas.
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config_by_name[config_name])

app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=365) # Tiempo para "Recordarme"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) # Tiempo para sesiones normales (CSRF)
# Puedes ajustar 'minutes=30' a más si lo necesitas, pero 30 suele ser suficiente
# --- FIN DE LÍNEAS A AÑADIR ---

# Asegura que la carpeta de subidas de archivos exista.
# Esto usa app.config['UPLOAD_FOLDER'], por lo que debe ir después de cargar la config.
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 5. Inicialización de Extensiones Principales (Orden Importante)
# ==============================================================================
# Las extensiones deben inicializarse después de que 'app' exista.
# El orden entre ellas puede importar:
# - SQLAlchemy (db): Generalmente va primero porque los modelos dependen de él.
# - Flask-Login (login_manager): Necesita la instancia 'app'.
db = SQLAlchemy(app) # SQLAlchemy necesita la instancia 'app'

login_manager = LoginManager(app) # Flask-Login necesita la instancia 'app'
login_manager.login_view = 'main.login' # Ruta a la que redirigir si el usuario no está logueado
login_manager.login_message_category = 'info' # Categoría de los mensajes flash para login

# 6. Definición de Modelos de Base de Datos
# ==============================================================================
# Las clases de tus modelos (User, Property, PropertyImage) deben definirse AQUÍ.
# Esto es CRÍTICO: Deben ir DESPUÉS de que 'db = SQLAlchemy(app)' haya sido ejecutado,
# ya que heredan de 'db.Model'.
# Si tus modelos estuvieran en un archivo 'models.py' separado, aquí importarías:
# from models import User, Property, PropertyImage
# Pero como los tienes en app.py, se definen directamente.

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) # Añadido de nuevo el campo email
    password = db.Column(db.String(60), nullable=False)
    properties = db.relationship('Property', backref='agente', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False) # Usar Numeric para precios
    ubicacion = db.Column(db.String(100), nullable=False)
    municipio = db.Column(db.String(50), nullable=False)
    estado_propiedad = db.Column(db.String(50), nullable=False) # 'Venta' o 'Renta'
    tipo_propiedad = db.Column(db.String(50), nullable=False)
    num_habitaciones = db.Column(db.Integer)
    num_banos = db.Column(db.Integer)
    num_medios_banos = db.Column(db.Integer)
    num_estacionamientos = db.Column(db.Integer)
    area_terreno_metros_cuadrados = db.Column(db.Numeric(10, 2))
    area_construccion_metros_cuadrados = db.Column(db.Numeric(10, 2))
    cuota_mantenimiento = db.Column(db.Numeric(10, 2))
    fecha_publicacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    agente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Clave foránea a User
    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade="all, delete-orphan") # Cambiado 'imagenes' a 'images' para consistencia con el código de rutas

    def __repr__(self):
        return f"Property('{self.titulo}', '{self.ubicacion}', '{self.precio}')"

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False) # Cambiado 'nombre_archivo' a 'filename'
    es_principal = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"PropertyImage('{self.filename}', principal={self.es_principal})"

# 7. Inicialización de Flask-Migrate
# ==============================================================================
# Flask-Migrate (Alembic) necesita conocer tanto la instancia de 'app' como la de 'db',
# Y lo más importante, necesita que TODOS tus modelos de 'db.Model' ya estén definidos
# para poder detectar cualquier cambio en la estructura de la base de datos.
# Por eso, esta línea DEBE ir DESPUÉS de la definición de tus modelos.
migrate = Migrate(app, db)

# 8. Función de Carga de Usuario para Flask-Login
# ==============================================================================
# Esta función es requerida por Flask-Login para cargar un usuario dado su ID de sesión.
# Depende de que 'login_manager' esté inicializado y que el modelo 'User' esté definido.
@login_manager.user_loader
def load_user(user_id):
    """
    Carga un usuario dado su ID para Flask-Login.
    """
    # Usar db.session.get() es el método recomendado para SQLAlchemy 2.0
    return db.session.get(User, int(user_id))

# 9. Definición y Registro de Blueprints
# ==============================================================================
# Los Blueprints agrupan rutas y lógica relacionada. Se definen y luego se registran
# con la instancia principal de la aplicación 'app'.
# Las rutas dentro de un Blueprint a menudo dependen de 'db', 'current_user',
# 'forms', etc., por lo que el Blueprint debe definirse y registrarse después de todo eso.
main = Blueprint('main', __name__)

# --- RUTAS ---
# Las rutas deben ir dentro del Blueprint o ser definidas después de la inicialización de la app.

@main.route("/")
@main.route("/home")
def home():
    """
    Ruta para la página de inicio, muestra las propiedades disponibles.
    """
    operation = request.args.get('operation')
    property_type = request.args.get('property_type')
    location = request.args.get('location')
    min_bedrooms = request.args.get('min_bedrooms', type=int)
    max_bedrooms = request.args.get('max_bedrooms', type=int)
    price_range = request.args.get('price_range')
    page = request.args.get('page', 1, type=int)

    query = Property.query

    if operation:
        if operation.lower() == 'comprar':
            query = query.filter_by(estado_propiedad='Venta')
        elif operation.lower() == 'rentar':
            query = query.filter_by(estado_propiedad='Renta')
    
    if property_type:
        query = query.filter_by(tipo_propiedad=property_type.capitalize())
    
    if location:
        query = query.filter(Property.municipio.ilike(f'%{location}%'))
    
    if min_bedrooms is not None:
        query = query.filter(Property.num_habitaciones >= min_bedrooms)
    
    if max_bedrooms is not None:
        query = query.filter(Property.num_habitaciones <= max_bedrooms)
    
    if price_range:
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
            '10000000-max': (10000000, float('inf'))
        }
        
        if price_range in price_ranges:
            min_price, max_price = price_ranges[price_range]
            query = query.filter(Property.precio >= min_price)
            if max_price != float('inf'):
                query = query.filter(Property.precio <= max_price)

    pagination = query.order_by(Property.fecha_publicacion.desc()).paginate(page=page, per_page=app.config['PROPERTIES_PER_PAGE'], error_out=False)
    
    return render_template('home.html', pagination=pagination, properties=pagination.items) # Cambiado 'propiedades' a 'properties' para consistencia

@main.route("/login", methods=['GET', 'POST'])
def login():
    """
    Ruta para el inicio de sesión de usuarios.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Inicio de sesión fallido. Por favor, verifica tu nombre de usuario y contraseña.', 'danger')
    return render_template('login.html', title='Iniciar Sesión', form=form)

@main.route("/logout")
@login_required
def logout():
    """
    Ruta para cerrar la sesión del usuario.
    """
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('main.home'))

@main.route("/dashboard")
@login_required
def dashboard():
    """
    Ruta para el panel de control del agente, mostrando sus propiedades.
    """
    user_properties = Property.query.filter_by(agente_id=current_user.id).order_by(Property.fecha_publicacion.desc()).all()
    return render_template('dashboard.html', title='Mi Panel', properties=user_properties)

# app.py

@main.route("/add_property", methods=['GET', 'POST'])
@login_required
def add_property():
    form = PropertyForm()
    print(f"DEBUG: Método de la solicitud: {request.method}")
    print(f"DEBUG: ¿Formulario enviado? {form.is_submitted()}")

    if form.validate_on_submit():
        print("DEBUG: form.validate_on_submit() es TRUE - ¡Formulario válido y enviado!")
        imagenes_subidas = []
        if 'imagenes' in request.files:
            for file in request.files.getlist('imagenes'):
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    imagenes_subidas.append(filename)

        new_property = Property(
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            precio=form.precio.data,
            ubicacion=form.ubicacion.data,
            municipio=form.municipio.data,
            estado_propiedad=form.estado_propiedad.data,
            tipo_propiedad=form.tipo_propiedad.data,
            num_habitaciones=form.num_habitaciones.data,
            num_banos=form.num_banos.data,
            num_medios_banos=form.num_medios_banos.data,
            num_estacionamientos=form.num_estacionamientos.data,
            area_terreno_metros_cuadrados=form.area_terreno_metros_cuadrados.data,
            area_construccion_metros_cuadrados=form.area_construccion_metros_cuadrados.data,
            cuota_mantenimiento=form.cuota_mantenimiento.data,
            fecha_publicacion=datetime.utcnow(),
            agente_id=current_user.id
        )
        db.session.add(new_property)
        db.session.commit()

        for img_filename in imagenes_subidas:
            new_image = PropertyImage(property_id=new_property.id, filename=img_filename)
            db.session.add(new_image)
        db.session.commit()

        flash('¡Propiedad añadida exitosamente!', 'success')
        return redirect(url_for('main.dashboard'))
    else:
        # ESTE ES EL BLOQUE CRÍTICO QUE NECESITAMOS VER EN LA TERMINAL
        print("DEBUG: form.validate_on_submit() es FALSE - Formulario inválido o no enviado.")
        print(f"DEBUG: Errores del formulario (form.errors): {form.errors}")
        # También imprime errores de campo específicos si los hay
        for field_name, errors in form.errors.items():
            for error in errors:
                print(f"DEBUG: Error en campo '{field_name}': {error}")
        # Y errores no asociados a un campo específico (como CSRF)
        if form.csrf_token.errors:
            print(f"DEBUG: Errores de CSRF (form.csrf_token.errors): {form.csrf_token.errors}")


    return render_template('add_property.html', title='Añadir Nueva Propiedad', form=form)


@main.route("/property/<int:property_id>")
def property_detail(property_id):
    """
    Ruta para mostrar los detalles de una propiedad específica.
    """
    property_detail = db.session.get(Property, property_id) # Usar db.session.get()
    if not property_detail:
        flash('La propiedad solicitada no existe.', 'danger')
        return redirect(url_for('main.home'))
    return render_template('property_detail.html', title=property_detail.titulo, property=property_detail) # Cambiado 'propiedad' a 'property' para consistencia

@main.route("/edit_property/<int:property_id>", methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    """
    Ruta para editar una propiedad existente.
    """
    property_to_edit = db.session.get(Property, property_id) # Usar db.session.get()

    if not property_to_edit: # Manejar caso donde la propiedad no existe
        flash('La propiedad solicitada para editar no existe.', 'danger')
        return redirect(url_for('main.dashboard'))

    if property_to_edit.agente_id != current_user.id:
        flash('No tienes permiso para editar esta propiedad.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = EditPropertyForm()

    if form.validate_on_submit():
        property_to_edit.titulo = form.titulo.data
        property_to_edit.descripcion = form.descripcion.data
        property_to_edit.precio = form.precio.data
        property_to_edit.ubicacion = form.ubicacion.data
        property_to_edit.municipio = form.municipio.data
        property_to_edit.estado_propiedad = form.estado_propiedad.data
        property_to_edit.tipo_propiedad = form.tipo_propiedad.data
        property_to_edit.num_habitaciones = form.num_habitaciones.data
        property_to_edit.num_banos = form.num_banos.data
        property_to_edit.num_medios_banos = form.num_medios_banos.data
        property_to_edit.num_estacionamientos = form.num_estacionamientos.data
        property_to_edit.area_terreno_metros_cuadrados = form.area_terreno_metros_cuadrados.data
        property_to_edit.area_construccion_metros_cuadrados = form.area_construccion_metros_cuadrados.data
        property_to_edit.cuota_mantenimiento = form.cuota_mantenimiento.data

        imagenes_subidas = []
        if 'imagenes' in request.files:
            for file in request.files.getlist('imagenes'):
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    imagenes_subidas.append(filename)

        for img_filename in imagenes_subidas:
            new_image = PropertyImage(property_id=property_to_edit.id, filename=img_filename) # Usar 'filename'
            db.session.add(new_image)
        db.session.commit()

        flash('¡Propiedad actualizada exitosamente!', 'success')
        return redirect(url_for('main.property_detail', property_id=property_to_edit.id))

    elif request.method == 'GET':
        form.titulo.data = property_to_edit.titulo
        form.descripcion.data = property_to_edit.descripcion
        form.precio.data = property_to_edit.precio
        form.ubicacion.data = property_to_edit.ubicacion
        form.municipio.data = property_to_edit.municipio
        form.estado_propiedad.data = property_to_edit.estado_propiedad
        form.tipo_propiedad.data = property_to_edit.tipo_propiedad
        form.num_habitaciones.data = property_to_edit.num_habitaciones
        form.num_banos.data = property_to_edit.num_banos
        form.num_medios_banos.data = property_to_edit.num_medios_banos
        form.num_estacionamientos.data = property_to_edit.num_estacionamientos
        form.area_terreno_metros_cuadrados.data = property_to_edit.area_terreno_metros_cuadrados
        form.area_construccion_metros_cuadrados.data = property_to_edit.area_construccion_metros_cuadrados
        form.cuota_mantenimiento.data = property_to_edit.cuota_mantenimiento

    return render_template('edit_property.html', title='Editar Propiedad', form=form, property=property_to_edit)

@main.route("/delete_property/<int:property_id>", methods=['POST'])
@login_required
def delete_property(property_id):
    """
    Ruta para eliminar una propiedad.
    Esta ruta debe ser llamada por un formulario POST para seguridad CSRF.
    """
    property_to_delete = db.session.get(Property, property_id) # Usar db.session.get()
    if not property_to_delete:
        flash('La propiedad solicitada para eliminar no existe.', 'danger')
        return redirect(url_for('main.dashboard')) # Redirigir al dashboard si no existe

    if property_to_delete.agente_id != current_user.id:
        flash('No tienes permiso para eliminar esta propiedad.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Eliminar imágenes asociadas del sistema de archivos
    for image in property_to_delete.images: # Usar 'images'
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename) # Usar 'filename'
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError as e:
                print(f"Error al eliminar archivo de imagen: {e}")
        db.session.delete(image)

    db.session.delete(property_to_delete)
    db.session.commit()
    flash('Propiedad eliminada exitosamente.', 'success')
    return redirect(url_for('main.dashboard')) # Redirigir al dashboard después de eliminar

# Registra el Blueprint 'main' con la aplicación
app.register_blueprint(main)

# 10. Bloque de Ejecución Principal
# ==============================================================================
# Este bloque solo se ejecuta cuando el script se corre directamente (ej. python app.py).
# Es el punto de entrada para iniciar el servidor de desarrollo y realizar tareas de inicialización.
if __name__ == '__main__':
    with app.app_context():
        # db.create_all() # Esta línea solo se usa para la primera vez que creas las tablas.
                         # Una vez que usas Flask-Migrate, las migraciones se encargan de esto.
                         # Si la descomentas, asegúrate de que no cause conflictos con las migraciones.

        # Creación de un usuario 'admin' si no existe
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('adminpassword', method='pbkdf2:sha256')
            admin_user = User(username='admin', email='admin@example.com', password=hashed_password) # Añadido email
            db.session.add(admin_user)
            db.session.commit()
            print("Usuario 'admin' creado.")
    app.run() # Inicia el servidor de desarrollo. El modo debug se controla por FLASK_ENV.
