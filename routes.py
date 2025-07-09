import os # Importa el módulo os para trabajar con rutas de archivos
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app # Importa módulos necesarios de Flask. current_app para acceder a la configuración de la app.
from werkzeug.utils import secure_filename # Importa secure_filename para limpiar nombres de archivo y evitar ataques.
from models import db, Propiedad, Imagen # Importa la instancia de DB y los modelos Propiedad e Imagen.

main = Blueprint('main', __name__) # Crea un Blueprint llamado 'main' para agrupar las rutas principales.

# Extensiones de archivo permitidas para las imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Función para verificar si la extensión de un archivo es permitida
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/') # Decorador que asocia la URL raíz ('/') con la función 'home'.
def home():
    # Esta función se ejecuta cuando alguien visita la URL raíz.
    # Obtiene todas las propiedades de la base de datos.
    propiedades = Propiedad.query.all() # Consulta todas las filas de la tabla Propiedad

    # Devuelve el contenido de la plantilla HTML 'index.html', pasando las propiedades.
    return render_template('index.html', propiedades=propiedades) # Pasa la lista de propiedades a la plantilla

@main.route('/add_property', methods=['GET', 'POST']) # Define la ruta /add_property, acepta peticiones GET y POST.
def add_property():
    # print("DEBUG: Entrando a la función add_property.") # DEBUG
    if request.method == 'POST': # Si la petición es POST (el formulario se ha enviado)...
        # print("DEBUG: Método de petición es POST.") # DEBUG
        # Recoge los datos de los campos obligatorios. request.form accede a los datos enviados.
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio']) # Convierte a número flotante
        direccion = request.form['direccion']
        municipio = request.form['municipio']
        estado = request.form['estado']
        num_habitaciones = int(request.form['num_habitaciones']) # Convierte a número entero
        num_banos = int(request.form['num_banos']) # Convierte a número entero
        area_construccion_metros_cuadrados = float(request.form['area_construccion_metros_cuadrados']) # Convierte a flotante
        tipo = request.form['tipo']
        estado_propiedad = request.form['estado_propiedad']

        # Campos opcionales: verifica si tienen valor antes de convertir y asignar None si están vacíos.

        # Campo opcional: código postal
        codigo_postal = request.form.get('codigo_postal')
        if not codigo_postal: # Si está vacío, asigna None
            codigo_postal = None

        # Campo opcional: número de medios baños
        num_medios_banos = request.form.get('num_medios_banos')
        if num_medios_banos:
            num_medios_banos = int(num_medios_banos)
        else:
            num_medios_banos = None

        # Campo opcional: número de estacionamientos
        num_estacionamientos = request.form.get('num_estacionamientos')
        if num_estacionamientos:
            num_estacionamientos = int(num_estacionamientos)
        else:
            num_estacionamientos = None

        # Campo opcional: antigüedad
        antiguedad = request.form.get('antiguedad')
        if antiguedad:
            antiguedad = int(antiguedad)
        else:
            antiguedad = None

        # Campo opcional: área de terreno
        area_terreno_metros_cuadrados = request.form.get('area_terreno_metros_cuadrados')
        if area_terreno_metros_cuadrados:
            area_terreno_metros_cuadrados = float(area_terreno_metros_cuadrados)
        else:
            area_terreno_metros_cuadrados = None

        # Campo opcional: cuota de mantenimiento
        cuota_mantenimiento = request.form.get('cuota_mantenimiento')
        if cuota_mantenimiento:
            cuota_mantenimiento = float(cuota_mantenimiento)
        else:
            cuota_mantenimiento = None

        # Crea una nueva instancia del modelo Propiedad con los datos del formulario.
        nueva_propiedad = Propiedad(
            titulo=titulo,
            descripcion=descripcion,
            precio=precio,
            direccion=direccion,
            municipio=municipio,
            estado=estado,
            codigo_postal=codigo_postal, # Asigna el valor (string o None)
            num_habitaciones=num_habitaciones,
            num_banos=num_banos,
            num_medios_banos=num_medios_banos,
            num_estacionamientos=num_estacionamientos,
            antiguedad=antiguedad,
            area_terreno_metros_cuadrados=area_terreno_metros_cuadrados, # Asigna el valor (flotante o None)
            area_construccion_metros_cuadrados=area_construccion_metros_cuadrados,
            tipo=tipo,
            cuota_mantenimiento=cuota_mantenimiento,
            estado_propiedad=estado_propiedad
        )
        # print(f"DEBUG: Propiedad creada en memoria: {nueva_propiedad.titulo}") # DEBUG

        try:
            # print("DEBUG: Intentando añadir a la sesión y commit.") # DEBUG
            db.session.add(nueva_propiedad) # Añade la nueva propiedad a la sesión de la base de datos.
            db.session.commit() # Confirma los cambios y guarda la propiedad en la base de datos.
            # print("DEBUG: Propiedad añadida y commit exitoso.") # DEBUG

            # --- Lógica para manejar la carga de imágenes ---
            # Verifica si el campo 'imagenes' existe en la petición de archivos
            if 'imagenes' in request.files:
                files = request.files.getlist('imagenes') # Obtiene la lista de archivos subidos
                is_first_image = True # Bandera para marcar la primera imagen como principal

                for file in files:
                    # Si el usuario no selecciona un archivo para el campo 'imagenes'
                    # el navegador puede enviar un archivo vacío sin nombre. Lo ignoramos.
                    if file.filename == '':
                        flash('No se seleccionó ningún archivo para una de las imágenes.', 'warning')
                        continue # Pasa al siguiente archivo en el bucle

                    # Si el archivo existe y tiene una extensión permitida
                    if file and allowed_file(file.filename):
                        # secure_filename limpia el nombre del archivo para evitar problemas de seguridad
                        filename = secure_filename(file.filename)
                        # Combina la ruta de la carpeta de subidas con el nombre del archivo
                        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath) # Guarda el archivo en el sistema de archivos

                        # Crea una nueva instancia del modelo Imagen y la asocia a la propiedad
                        nueva_imagen = Imagen(
                            nombre_archivo=filename,
                            propiedad_id=nueva_propiedad.id, # Asocia la imagen con la propiedad recién creada
                            es_principal=is_first_image # Marca la primera imagen como principal
                        )
                        db.session.add(nueva_imagen) # Añade la imagen a la sesión de la base de datos
                        is_first_image = False # Después de la primera imagen, las demás no son principales
                    else:
                        flash(f'Tipo de archivo no permitido para {file.filename}. Solo se permiten PNG, JPG, JPEG, GIF.', 'danger')

                db.session.commit() # Confirma los cambios de las imágenes en la base de datos
            # --- Fin de la lógica de imágenes ---

            flash('¡Propiedad añadida con éxito!', 'success') # Muestra un mensaje de éxito al usuario.
            return redirect(url_for('main.home')) # Redirige al usuario a la página de inicio.
        except Exception as e:
            db.session.rollback() # Si hay un error, revierte los cambios en la base de datos.
            flash(f'Error al añadir propiedad: {e}', 'danger') # Muestra un mensaje de error.
            # Opcional: Podrías volver a renderizar el formulario con los datos pre-rellenados y el error.

    # Si la petición es GET (se accede a la página por primera vez), simplemente renderiza el formulario.
    return render_template('add_property.html')

@main.route('/property/<int:property_id>') # Nueva ruta para ver detalles de una propiedad. <int:property_id> captura un número entero de la URL.
def property_detail(property_id):
    # Busca la propiedad en la base de datos usando su ID.
    # .get_or_404() es una forma conveniente de obtener un objeto por su PK o devolver un error 404 si no se encuentra.
    propiedad = Propiedad.query.get_or_404(property_id)

    # Renderiza la plantilla property_detail.html y le pasa el objeto propiedad encontrado.
    return render_template('property_detail.html', propiedad=propiedad)