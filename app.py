# app.py

# 1. Importaciones
# ==============================================================================
from flask import Flask, render_template, url_for, flash, redirect, request, Blueprint, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from config import config_by_name
from forms import RegisterForm, LoginForm, PropertyForm, EditPropertyForm
from extensions import db, login_manager, migrate
from models import User, Property, PropertyImage


# 2. Funciones Auxiliares
# ==============================================================================
def allowed_file(filename):
    """
    Verifica si la extensión de un archivo es permitida para la subida.
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 3. Inicialización de la Aplicación Flask
# ==============================================================================
app = Flask(__name__)

# 4. Carga de Configuración de Entornos
# ==============================================================================
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config_by_name[config_name])

app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=365)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Asegura que la carpeta de subidas de archivos exista.
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 5. Inicialización de Extensiones Principales (Orden Importante)
# ==============================================================================
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

# 6. Definición de Modelos de Base de Datos (Importados desde models.py)
# No hay cambios aquí, solo confirmación de que están importados

# 7. Inicialización de Flask-Migrate
# ==============================================================================
migrate.init_app(app, db)

# 8. Función de Carga de Usuario para Flask-Login
# ==============================================================================
@login_manager.user_loader
def load_user(user_id):
    """
    Carga un usuario dado su ID para Flask-Login.
    """
    return db.session.get(User, int(user_id))

# 9. Definición y Registro de Blueprints
# ==============================================================================
main = Blueprint('main', __name__)

# --- RUTAS ---


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
            query = query.filter_by(property_options='Venta')
        elif operation.lower() == 'rentar':
            query = query.filter_by(property_options='Renta')
    
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
    
    properties = pagination.items # Obtener las propiedades para la página actual

    # --- INICIO DE CAMBIO: ORDENAR LAS IMÁGENES PARA CADA PROPIEDAD ---
    # Asegurar que la imagen principal (is_main=True) vaya primero en cada conjunto de imágenes
    for prop in properties: # Iterar sobre cada objeto Property en la lista
        if prop.images: # Si la propiedad tiene imágenes
            # Ordenar: principal (is_main=True) primero, luego por id
            prop.images = sorted(prop.images, key=lambda img: (not img.is_main, img.id))
    # --- FIN DE CAMBIO ---
    
    # Pasamos el objeto pagination completo a la plantilla
    return render_template('home.html', pagination=pagination, properties=properties) # 'properties' ya está ordenado
    
    

@main.route("/about_us")
def about_us():
    """
    Ruta para la página "Nosotros".
    """
    return render_template('about_us.html', title='Nosotros')


@main.route("/contact")
def contact():
    """
    Ruta para la página de Contacto.
    """
    return render_template('contact.html', title='Contacto')


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
        if user and check_password_hash(user.password_hash, form.password.data): 
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Inicio de sesión fallido. Por favor, verifica tu nombre de usuario y contraseña.', 'danger')
    return render_template('login.html', title='Iniciar Sesión', form=form)


@main.route("/register", methods=['GET', 'POST'])
def register():
    # Si el usuario ya está autenticado, redirigirlo para que no se registre de nuevo
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Tu cuenta ha sido creada exitosamente. ¡Ya puedes iniciar sesión!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Registrarse', form=form)


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
    Ruta para el panel de control del agente, mostrando sus propiedades con paginación.
    """
    page = request.args.get('page', 1, type=int)
    user_properties_query = Property.query.filter_by(agente_id=current_user.id).order_by(Property.fecha_publicacion.desc())
    pagination = user_properties_query.paginate(page=page, per_page=current_app.config['PROPERTIES_PER_PAGE'], error_out=False)
    properties = pagination.items

    return render_template('dashboard.html', 
                           properties=properties, 
                           pagination=pagination, 
                           title='Mi Panel de Administración')


@main.route("/add_property", methods=['GET', 'POST'])
@login_required
def add_property():
    # --- INICIO: Lógica para limitar a un agente a una propiedad ---
    if current_user.is_admin:
        # Los administradores pueden añadir propiedades sin límite aquí.
        pass
    else: # Si el usuario no es un administrador (es un agente o usuario regular)
        # Cuenta cuántas propiedades tiene publicadas el usuario actual.
        num_properties = len(current_user.managed_properties) 

        if num_properties >= 1: # Si ya tiene una o más propiedades
            flash('Lo sentimos, como agente solo puedes publicar una propiedad.', 'warning')
            return redirect(url_for('main.dashboard')) # Redirige al dashboard
    # --- FIN: Lógica para limitar a un agente a una propiedad ---

    form = PropertyForm()
    print(f"DEBUG: Método de la solicitud: {request.method}")
    print(f"DEBUG: ¿Formulario enviado? {form.is_submitted()}")

    if form.validate_on_submit():
        print("DEBUG: form.validate_on_submit() es TRUE - ¡Formulario válido y enviado!")
        
        try:
            new_property = Property(
                titulo=form.titulo.data,
                descripcion=form.descripcion.data,
                precio=form.precio.data,
                ubicacion=form.ubicacion.data,
                municipio=form.municipio.data,
                property_options=form.property_options.data,
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

            print(f"DEBUG: Propiedad guardada en DB con ID: {new_property.id}")

            imagenes_subidas = []
            if 'imagenes' in request.files:
                for file in request.files.getlist('imagenes'):
                    if file.filename != '' and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        imagenes_subidas.append(filename)
                        print(f"DEBUG: Archivo guardado físicamente: {filename}")
                    elif file.filename == '':
                        print("DEBUG: Archivo de imagen vacío (Ignorado).")
                    else:
                        print(f"DEBUG: Archivo {file.filename} no permitido o inválido.")

            for img_filename in imagenes_subidas:
                new_image = PropertyImage(property_id=new_property.id, filename=img_filename, is_main=False)
                db.session.add(new_image)
            db.session.commit()

            print("DEBUG: Imágenes de propiedad guardadas en DB.")

            flash('¡Propiedad añadida exitosamente!', 'success')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Fallo al añadir propiedad o imágenes: {e}")
            flash(f'Error al añadir la propiedad: {e}', 'danger')
    else:
        print("DEBUG: form.validate_on_submit() es FALSE - Formulario inválido o no enviado.")
        print(f"DEBUG: Errores del formulario (form.errors): {form.errors}")
        for field_name, errors in form.errors.items():
            for error in errors:
                print(f"DEBUG: Error en campo '{field_name}': {error}")
        if form.csrf_token.errors:
            print(f"DEBUG: Errores de CSRF (form.csrf_token.errors): {form.csrf_token.errors}")

    return render_template('add_property.html', title='Añadir Nueva Propiedad', form=form)


@main.route("/property/<int:property_id>")
def property_detail(property_id):
    """
    Ruta para mostrar los detalles de una propiedad específica.
    """
    property_data = db.session.get(Property, property_id) # Usar db.session.get() para la propiedad

    if not property_data:
        flash('La propiedad solicitada no existe.', 'danger')
        return redirect(url_for('main.home'))
    
    # --- INICIO DE CAMBIO: ORDENAR LAS IMÁGENES PARA ASEGURAR QUE LA PRINCIPAL VAYA PRIMERO ---
    if property_data.images:
        # Crea una lista temporal ordenada: principal primero, luego el resto
        # img.is_main es True o False. (img.is_main is not False) evalúa a (True) si is_main es True,
        # y a (False) si is_main es False. Ordenando por esto pondrá True primero.
        # Luego, si varias tienen el mismo is_main (ej. todas False), las ordena por ID para consistencia.
        sorted_images = sorted(property_data.images, key=lambda img: (not img.is_main, img.id))
        property_data.images = sorted_images # Asigna la lista ordenada de vuelta al atributo images
    # --- FIN DE CAMBIO ---

    return render_template('property_detail.html', title=property_data.titulo, property=property_data)




@main.route("/edit_property/<int:property_id>", methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    """
    Ruta para editar una propiedad existente.
    """
    property_to_edit = Property.query.get_or_404(property_id)

    if property_to_edit.agente_id != current_user.id and not current_user.is_admin:
        flash('No tienes permiso para editar esta propiedad.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = EditPropertyForm()

    if form.validate_on_submit():
        property_to_edit.titulo = form.titulo.data
        property_to_edit.descripcion = form.descripcion.data
        property_to_edit.precio = form.precio.data
        property_to_edit.ubicacion = form.ubicacion.data
        property_to_edit.municipio = form.municipio.data
        property_to_edit.property_options = form.property_options.data
        property_to_edit.tipo_propiedad = form.tipo_propiedad.data
        property_to_edit.num_habitaciones = form.num_habitaciones.data
        property_to_edit.num_banos = form.num_banos.data
        property_to_edit.num_medios_banos = form.num_medios_banos.data
        property_to_edit.num_estacionamientos = form.num_estacionamientos.data
        property_to_edit.area_terreno_metros_cuadrados = form.area_terreno_metros_cuadrados.data
        property_to_edit.area_construccion_metros_cuadrados = form.area_construccion_metros_cuadrados.data
        property_to_edit.cuota_mantenimiento = form.cuota_mantenimiento.data

        delete_images_ids = request.form.getlist('delete_images')
        for img_id in delete_images_ids:
            image_to_delete = PropertyImage.query.get(int(img_id))
            if image_to_delete and image_to_delete.property_id == property_to_edit.id:
                try:
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], image_to_delete.filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"DEBUG: Archivo {image_to_delete.filename} eliminado físicamente.")
                    else:
                        print(f"DEBUG: Archivo {image_to_delete.filename} no encontrado en disco, eliminando solo de DB.")
                except OSError as e:
                    print(f"ERROR: No se pudo eliminar el archivo {image_to_delete.filename}: {e}")
                db.session.delete(image_to_delete)
                print(f"DEBUG: Imagen {img_id} marcada para eliminación de DB.")
            else:
                print(f"ADVERTENCIA: Intento de eliminar imagen ID {img_id} no encontrada o no pertenece a esta propiedad.")

        principal_image_id = request.form.get('principal_image', type=int)
        if principal_image_id:
            for img in property_to_edit.images:
                img.is_main = False
            new_principal_image = PropertyImage.query.get(principal_image_id)
            if new_principal_image and new_principal_image.property_id == property_to_edit.id:
                new_principal_image.is_main = True
                print(f"DEBUG: Imagen {new_principal_image.filename} marcada como principal.")
            else:
                print(f"ADVERTENCIA: Imagen principal ID {principal_image_id} no encontrada o no pertenece a esta propiedad.")
        else:
            db.session.flush()
            if property_to_edit.images and not any(img.is_main for img in property_to_edit.images):
                property_to_edit.images[0].is_main = True
                print(f"DEBUG: Ninguna principal seleccionada, primera imagen {property_to_edit.images[0].filename} establecida como principal por defecto.")

        new_image_files = request.files.getlist('imagenes')
        if new_image_files:
            for file in new_image_files:
                if file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    is_main = False
                    db.session.flush()
                    if not property_to_edit.images or not any(img.is_main for img in property_to_edit.images):
                        is_main = True
                        print(f"DEBUG: Nueva imagen {filename} marcada como principal (primera).")

                    new_image = PropertyImage(property_id=property_to_edit.id, filename=filename, is_main=is_main)
                    db.session.add(new_image)
                    print(f"DEBUG: Nueva imagen {filename} añadida a DB.")
                elif file.filename == '':
                    print("DEBUG: Archivo de imagen vacío ignorado.")
                else:
                    print(f"ADVERTENCIA: Archivo {file.filename} no permitido o con nombre inválido.")

        db.session.commit()
        print("DEBUG: Commit final de la sesión de DB.")
        flash('¡Propiedad actualizada exitosamente!', 'success')
        return redirect(url_for('main.property_detail', property_id=property_to_edit.id))

    elif request.method == 'GET':
        form.titulo.data = property_to_edit.titulo
        form.descripcion.data = property_to_edit.descripcion
        form.precio.data = property_to_edit.precio
        form.ubicacion.data = property_to_edit.ubicacion
        form.municipio.data = property_to_edit.municipio
        form.property_options.data = property_to_edit.property_options
        form.tipo_propiedad.data = property_to_edit.tipo_propiedad
        form.num_habitaciones.data = property_to_edit.num_habitaciones
        form.num_banos.data = property_to_edit.num_banos
        form.num_medios_banos.data = property_to_edit.num_medios_banos
        form.num_estacionamientos.data = property_to_edit.num_estacionamientos
        form.area_terreno_metros_cuadrados.data = property_to_edit.area_terreno_metros_cuadrados
        form.area_construccion_metros_cuadrados.data = property_to_edit.area_construccion_metros_cuadrados
        form.cuota_mantenimiento.data = property_to_edit.cuota_mantenimiento
    
    return render_template('edit_property.html', title='Editar Propiedad', form=form, property=property_to_edit)


@main.route('/delete_property/<int:property_id>', methods=['POST'])
@login_required
def delete_property(property_id):
    property_to_delete = Property.query.get_or_404(property_id)

    if property_to_delete.agente_id != current_user.id and not current_user.is_admin:
        flash('No tienes permiso para eliminar esta propiedad.', 'danger')
        return redirect(url_for('main.dashboard'))

    try:
        # Eliminar archivos de imágenes físicos antes de eliminar de la DB
        for image in property_to_delete.images:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    print(f"DEBUG: Archivo de imagen '{image.filename}' eliminado físicamente.")
                except OSError as e:
                    print(f"ERROR: No se pudo eliminar el archivo '{image.filename}': {e}")
            else:
                print(f"DEBUG: Archivo de imagen '{image.filename}' no encontrado en disco.")
        
        db.session.delete(property_to_delete)
        db.session.commit()
        flash('Propiedad eliminada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la propiedad: {e}', 'danger')
    return redirect(url_for('main.dashboard'))


# Registra el Blueprint 'main' con la aplicación
app.register_blueprint(main)

# 10. Bloque de Ejecución Principal
# ==============================================================================
if __name__ == '__main__':
    with app.app_context():
        # **NOTA IMPORTANTE:**
        # Para la gestión de la base de datos con Flask-Migrate, la forma preferida
        # para crear y actualizar el esquema es usando los comandos de migración:
        #
        # 1. flask db init (solo la primera vez para crear la carpeta migrations)
        # 2. flask db migrate -m "Initial migration" (cada vez que cambies modelos)
        # 3. flask db upgrade (para aplicar las migraciones a la DB)
        #
        # `db.create_all()` puede ser útil en desarrollo si no usas migraciones o
        # para asegurarte de que las tablas existen para un inicio rápido,
        # pero para un control completo y entornos de producción, confía en `flask db upgrade`.
        # Si tienes migraciones pendientes, `db.create_all()` no las aplicará.
        #
        # Si decides mantenerlo, asegúrate de entender su implicación.
        db.create_all()

        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            hashed_password = generate_password_hash('adminpassword', method='pbkdf2:sha256')
            admin_user = User(username='admin', email='admin@example.com', password_hash=hashed_password, is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            print("Usuario 'admin' creado con privilegios de administrador.")
        else:
            if not admin_user.is_admin:
                admin_user.is_admin = True
                db.session.commit()
                print("Usuario 'admin' actualizado a administrador (is_admin=True).")

    app.run()