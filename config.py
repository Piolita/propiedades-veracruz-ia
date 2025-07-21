# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Clase base de configuración común a todos los entornos."""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', '4f50d3dda89b4b03c07de846ef3b5672ba6e840251ccdbd2') # Tu clave de fallback
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    PROPERTIES_PER_PAGE = 9
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

class DevelopmentConfig(Config):
    """Configuración para el entorno de desarrollo."""
    DEBUG = True # Activa el modo de depuración de Flask
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'site.db') # Usamos SQLite por defecto para desarrollo
    # Puedes añadir más configuraciones específicas de desarrollo aquí

class ProductionConfig(Config):
    """Configuración para el entorno de producción."""
    DEBUG = False # Desactiva el modo de depuración en producción
    TESTING = False # Desactiva el modo de prueba
    # IMPORTANTE: En producción, SIEMPRE debes usar una variable de entorno para la DB.
    # NO uses 'sqlite:///site.db' directamente en producción.
    # Idealmente, 'DATABASE_URL' será para PostgreSQL o similar en tu servidor.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'site_prod.db') # Una DB SQLite de PRODUCCIÓN diferente


class TestingConfig(Config):
    """Configuración para el entorno de pruebas."""
    TESTING = True # Activa el modo de prueba
    # Usar una base de datos separada para pruebas es una buena práctica
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'test.db')

# Diccionario para seleccionar la configuración basada en la variable de entorno FLASK_ENV
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig # Si FLASK_ENV no está definida, usa desarrollo
}