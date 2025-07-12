import os
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash # Necesario para create-admin

# Importar las instancias de extensiones desde extensions.py
from extensions import db, migrate, login_manager

# Importa los modelos de la base de datos (Propiedad, Imagen, User)
# User ahora se importa desde models.py
from models import Propiedad, Imagen, User

# Función de carga de usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # db ya estará inicializado con la app en este punto
    return User.query.get(int(user_id))


# Función para crear y configurar la aplicación Flask
def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'propiedades.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'una_clave_secreta_muy_segura_y_larga_para_tu_app' # ¡CAMBIA ESTO EN PRODUCCIÓN!

    # Inicializar las extensiones con la aplicación
    # Esto DEBE ocurrir después de configurar la app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login' # Ruta a la que se redirigirá si se requiere login

    # Importa y registra el blueprint 'main' de las rutas
    # Esto DEBE ocurrir después de que la app y las extensiones están inicializadas
    from routes import main_bp
    app.register_blueprint(main_bp)

    return app

# Crea la instancia de la aplicación para el CLI (flask commands) y para el servidor de desarrollo
app = create_app()

# Comando para crear un usuario administrador (solo para desarrollo)
@app.cli.command("create-admin")
def create_admin():
    """Crea un usuario administrador."""
    username = input("Introduce el nombre de usuario para el administrador: ")
    password = input("Introduce la contraseña para el administrador: ")

    # Asegúrate de que las operaciones de DB se realicen en el contexto de la aplicación
    with app.app_context():
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"El usuario '{username}' ya existe.")
            return

        admin_user = User(username=username)
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Usuario administrador '{username}' creado exitosamente.")

if __name__ == '__main__':
    app.run(debug=True)
