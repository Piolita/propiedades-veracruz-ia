from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Importa db y login_manager desde extensions.py
from extensions import db, login_manager
# Importa tus modelos de Propiedad, Imagen, y User (que ahora está en models.py)
from models import Propiedad, Imagen, User 

# Crea una instancia de Blueprint
main_bp = Blueprint('main', __name__)

# Ruta principal (Home)
@main_bp.route('/')
def home():
    # Envuelve la consulta de la base de datos en el contexto de la aplicación
    with current_app.app_context():
        propiedades = Propiedad.query.all()
    return render_template('index.html', propiedades=propiedades)

# Ruta para mostrar los detalles de una propiedad
@main_bp.route('/property/<int:property_id>')
def property_detail(property_id):
    # Envuelve la consulta de la base de datos en el contexto de la aplicación
    with current_app.app_context():
        propiedad = Propiedad.query.get_or_404(property_id)
    return render_template('property_detail.html', propiedad=propiedad)

# Ruta para añadir una nueva propiedad (requiere login)
@main_bp.route('/add_property', methods=['GET', 'POST'])
@login_required # Protege esta ruta, solo usuarios logueados pueden acceder
def add_property():
    # db ya está importado desde extensions.py
    if request.method == 'POST':
        # Recopila datos del formulario
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        direccion = request.form['direccion']
        municipio = request.form['municipio']
        estado = request.form['estado']
        tipo = request.form['tipo']
        estado_propiedad = request.form['estado_propiedad']
        num_habitaciones = int(request.form['num_habitaciones'])
        num_banos = int(request.form['num_banos'])
        num_medios_banos = int(request.form['num_medios_banos']) if request.form['num_medios_banos'] else 0
        num_estacionamientos = int(request.form['num_estacionamientos']) if request.form['num_estacionamientos'] else 0
        area_construccion_metros_cuadrados = float(request.form['area_construccion_metros_cuadrados'])
        area_terreno_metros_cuadrados = float(request.form['area_terreno_metros_cuadrados']) if request.form['area_terreno_metros_cuadrados'] else 0.0
        antiguedad = int(request.form['antiguedad']) if request.form['antiguedad'] else 0
        cuota_mantenimiento = float(request.form['cuota_mantenimiento']) if request.form['cuota_mantenimiento'] else 0.0

        # Crea una nueva instancia de Propiedad
        nueva_propiedad = Propiedad(
            titulo=titulo,
            descripcion=descripcion,
            precio=precio,
            direccion=direccion,
            municipio=municipio,
            estado=estado,
            tipo=tipo,
            estado_propiedad=estado_propiedad,
            num_habitaciones=num_habitaciones,
            num_banos=num_banos,
            num_medios_banos=num_medios_banos,
            num_estacionamientos=num_estacionamientos,
            area_construccion_metros_cuadrados=area_construccion_metros_cuadrados,
            area_terreno_metros_cuadrados=area_terreno_metros_cuadrados,
            antiguedad=antiguedad,
            cuota_mantenimiento=cuota_mantenimiento,
            fecha_publicacion=datetime.utcnow()
        )
        with current_app.app_context(): # Envuelve las operaciones de DB en el contexto
            db.session.add(nueva_propiedad)
            db.session.commit() # Guarda la propiedad para obtener su ID

        # Manejo de la subida de imágenes
        if 'imagenes' in request.files:
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)

            for archivo in request.files.getlist('imagenes'):
                if archivo.filename != '':
                    filename = secure_filename(archivo.filename)
                    filepath = os.path.join(uploads_dir, filename)
                    archivo.save(filepath)

                    # Determina si es la imagen principal (asumiendo la primera imagen como principal por simplicidad)
                    # En una aplicación real, podrías tener un checkbox en el formulario
                    es_principal = (request.files.getlist('imagenes').index(archivo) == 0)

                    nueva_imagen = Imagen(
                        nombre_archivo=filename,
                        propiedad_id=nueva_propiedad.id,
                        es_principal=es_principal
                    )
                    with current_app.app_context(): # Envuelve las operaciones de DB en el contexto
                        db.session.add(nueva_imagen)
            with current_app.app_context(): # Envuelve el commit final en el contexto
                db.session.commit()

        flash('Propiedad añadida exitosamente!', 'success')
        return redirect(url_for('main.home'))
    return render_template('add_property.html')

# Ruta para editar una propiedad (requiere login)
@main_bp.route('/edit_property/<int:property_id>', methods=['GET', 'POST'])
@login_required # Protege esta ruta
def edit_property(property_id):
    # db ya está importado desde extensions.py
    with current_app.app_context(): # Envuelve la consulta de la base de datos en el contexto
        propiedad = Propiedad.query.get_or_404(property_id)
    if request.method == 'POST':
        propiedad.titulo = request.form['titulo']
        propiedad.descripcion = request.form['descripcion']
        propiedad.precio = float(request.form['precio'])
        propiedad.direccion = request.form['direccion']
        propiedad.municipio = request.form['municipio']
        propiedad.estado = request.form['estado']
        propiedad.tipo = request.form['tipo']
        propiedad.estado_propiedad = request.form['estado_propiedad']
        propiedad.num_habitaciones = int(request.form['num_habitaciones'])
        propiedad.num_banos = int(request.form['num_banos'])
        propiedad.num_medios_banos = int(request.form['num_medios_banos']) if request.form['num_medios_banos'] else 0
        propiedad.num_estacionamientos = int(request.form['num_estacionamientos']) if request.form['num_estacionamientos'] else 0
        propiedad.area_construccion_metros_cuadrados = float(request.form['area_construccion_metros_cuadrados'])
        propiedad.area_terreno_metros_cuadrados = float(request.form['area_terreno_metros_cuadrados']) if request.form['area_terreno_metros_cuadrados'] else 0.0
        antiguedad = int(request.form['antiguedad']) if request.form['antiguedad'] else 0
        cuota_mantenimiento = float(request.form['cuota_mantenimiento']) if request.form['cuota_mantenimiento'] else 0.0

        # Manejo de la subida de nuevas imágenes
        if 'imagenes' in request.files:
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            for archivo in request.files.getlist('imagenes'):
                if archivo.filename != '':
                    filename = secure_filename(archivo.filename)
                    filepath = os.path.join(uploads_dir, filename)
                    archivo.save(filepath)
                    nueva_imagen = Imagen(nombre_archivo=filename, propiedad_id=propiedad.id, es_principal=False) # Nuevas imágenes no son principales por defecto
                    with current_app.app_context(): # Envuelve las operaciones de DB en el contexto
                        db.session.add(nueva_imagen)

        with current_app.app_context(): # Envuelve el commit final en el contexto
            db.session.commit()
        flash('Propiedad actualizada exitosamente!', 'success')
        return redirect(url_for('main.property_detail', property_id=propiedad.id))
    return render_template('edit_property.html', propiedad=propiedad)

# Ruta para eliminar una propiedad (requiere login)
@main_bp.route('/delete_property/<int:property_id>', methods=['GET', 'POST'])
@login_required # Protege esta ruta
def delete_property(property_id):
    # db ya está importado desde extensions.py
    with current_app.app_context(): # Envuelve la consulta de la base de datos en el contexto
        propiedad = Propiedad.query.get_or_404(property_id)
    if request.method == 'POST':
        # Opcional: Eliminar archivos de imagen asociados del sistema de archivos
        uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        with current_app.app_context(): # Envuelve las operaciones de DB en el contexto
            for imagen in propiedad.imagenes:
                filepath = os.path.join(uploads_dir, imagen.nombre_archivo)
                if os.path.exists(filepath):
                    os.remove(filepath)
                db.session.delete(imagen) # Elimina la referencia de la imagen de la base de datos

            db.session.delete(propiedad)
            db.session.commit()
        flash('Propiedad eliminada exitosamente!', 'success')
        return redirect(url_for('main.home'))
    return render_template('delete_property.html', propiedad=propiedad)


# ##################################################################
# INICIO: Rutas de Autenticación
# ##################################################################

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    # User ya está importado desde models.py
    if current_user.is_authenticated: # Si el usuario ya está logueado, redirige a home
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Envuelve la consulta de la base de datos en el contexto
        with current_app.app_context():
            user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user) # Inicia sesión del usuario
            flash('Inicio de sesión exitoso.', 'success')
            # Redirige al usuario a la página que intentaba acceder antes de ser redirigido al login
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Nombre de usuario o contraseña inválidos.', 'danger')
    return render_template('login.html')

@main_bp.route('/logout')
@login_required # Solo un usuario logueado puede cerrar sesión
def logout():
    logout_user() # Cierra la sesión del usuario
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('main.home'))

# ##################################################################
# FIN: Rutas de Autenticación
# ##################################################################
