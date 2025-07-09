import os # Importa el módulo os para trabajar con rutas de archivos
from flask import Flask # Importa la clase principal de Flask para crear la aplicación web.
from config import Config # Importa la clase Config de tu archivo config.py para la configuración.
from models import db # Importa la instancia 'db' de SQLAlchemy que creaste en models.py.
from routes import main as main_blueprint # Importa el Blueprint 'main' de routes.py para organizar las rutas.

def create_app():
    app = Flask(__name__) # Crea una instancia de la aplicación Flask.
    app.config.from_object(Config) # Carga la configuración desde el objeto Config (config.py).

    # Configuración para la carga de imágenes
    # Define la carpeta donde se guardarán las imágenes subidas
    # os.path.abspath(os.path.dirname(__file__)) obtiene la ruta absoluta del directorio actual del archivo app.py
    # 'static/uploads' es la subcarpeta dentro de 'static'
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Añade la ruta de la carpeta de subidas a la configuración de Flask

    # Asegúrate de que la carpeta de subidas exista. Si no existe, la crea.
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"DEBUG: Carpeta de subidas creada: {UPLOAD_FOLDER}") # DEBUG

    db.init_app(app) # Inicializa la extensión SQLAlchemy con la aplicación Flask.


    with app.app_context():
        # Dentro del contexto de la aplicación, crea todas las tablas en la base de datos
        # basándose en los modelos definidos en models.py.
        # Esto solo crea las tablas si no existen.
        db.create_all()


    # Registra el Blueprint 'main' para que la aplicación conozca las rutas definidas en routes.py.
    app.register_blueprint(main_blueprint)

    return app # Devuelve la instancia de la aplicación Flask configurada.

if __name__ == '__main__':
    # Este bloque se ejecuta solo si el script app.py se corre directamente (no importado).
    app = create_app() # Crea la aplicación.
    app.run(debug=True) # Inicia el servidor de desarrollo de Flask.
                        # debug=True permite recarga automática y depuración.