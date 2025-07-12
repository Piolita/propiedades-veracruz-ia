from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Inicializar las extensiones aquí, sin pasar la app.
# La app se pasará más tarde usando el patrón init_app()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
