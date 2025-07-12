from extensions import db # Importa db desde extensions.py
from datetime import datetime
from flask_login import UserMixin # Importa UserMixin aquí para la clase User
from werkzeug.security import generate_password_hash, check_password_hash # ¡AÑADIR ESTA LÍNEA!

class Propiedad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False) # Ej: Casa, Departamento, Terreno
    estado_propiedad = db.Column(db.String(50), nullable=False) # Ej: Venta, Renta
    num_habitaciones = db.Column(db.Integer, nullable=True)
    num_banos = db.Column(db.Integer, nullable=True)
    num_medios_banos = db.Column(db.Integer, default=0)
    num_estacionamientos = db.Column(db.Integer, default=0)
    area_construccion_metros_cuadrados = db.Column(db.Float, nullable=True)
    area_terreno_metros_cuadrados = db.Column(db.Float, nullable=True)
    antiguedad = db.Column(db.Integer, nullable=True) # En años
    cuota_mantenimiento = db.Column(db.Float, default=0.0)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con las imágenes
    imagenes = db.relationship('Imagen', backref='propiedad', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Propiedad('{self.titulo}', '{self.direccion}', '{self.precio}')"

class Imagen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(100), nullable=False)
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedad.id'), nullable=False)
    es_principal = db.Column(db.Boolean, default=False) # Para identificar la imagen principal

    def __repr__(self):
        return f"Imagen('{self.nombre_archivo}', Propiedad ID: {self.propiedad_id})"

# ##################################################################
# INICIO: Modelo de Usuario (MOVIDO DESDE app.py)
# ##################################################################
class User(db.Model, UserMixin): # User debe heredar de UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.username}>'
# ##################################################################
# FIN: Modelo de Usuario
# ##################################################################
