# models.py

from extensions import db # Importa db desde extensions.py
from datetime import datetime
from flask_login import UserMixin # Importa UserMixin aquí para la clase User
from werkzeug.security import generate_password_hash, check_password_hash

# Renombrado de Propiedad a Property
class Property(db.Model):
    __tablename__ = 'property' # Añadido nombre de tabla explícito para consistencia
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    # CAMBIO: 'direccion' a 'ubicacion' para consistencia con formularios
    ubicacion = db.Column(db.String(200), nullable=False) 
    municipio = db.Column(db.String(100), nullable=False)
    # CAMBIO: 'estado' a 'state' si te refieres al estado de la república,
    # si es el estado de la propiedad (Venta/Renta) ya tienes 'estado_propiedad'
    # Por ahora lo dejo como 'estado' si es el estado de la república.
    # Si esta columna no es necesaria, se puede eliminar.
    property_options = db.Column(db.String(100), nullable=False) 
    # CAMBIO: 'tipo' a 'property_type' para consistencia con formularios
    tipo_propiedad = db.Column(db.String(50), nullable=False) # Ej: Casa, Departamento, Terreno
    num_habitaciones = db.Column(db.Integer, nullable=True)
    num_banos = db.Column(db.Integer, nullable=True)
    num_medios_banos = db.Column(db.Integer, default=0)
    num_estacionamientos = db.Column(db.Integer, default=0)
    area_construccion_metros_cuadrados = db.Column(db.Float, nullable=True)
    area_terreno_metros_cuadrados = db.Column(db.Float, nullable=True)
    antiguedad = db.Column(db.Integer, nullable=True) # En años
    cuota_mantenimiento = db.Column(db.Float, default=0.0)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con las imágenes, renombrado de 'imagenes' a 'images' y 'propiedad' a 'property'
    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade="all, delete-orphan")

    # Añadida relación con User para saber qué agente la publicó
    agente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agente = db.relationship('User', backref='properties') # Relación inversa para acceder a las propiedades de un usuario

    def __repr__(self):
        return f"Property('{self.titulo}', '{self.ubicacion}', '{self.precio}')"

# Renombrado de Imagen a PropertyImage
class PropertyImage(db.Model):
    __tablename__ = 'property_image' # Añadido nombre de tabla explícito
    id = db.Column(db.Integer, primary_key=True)
    # CAMBIO: nombre_archivo a filename
    filename = db.Column(db.String(100), nullable=False) 
    # CAMBIO: propiedad_id a property_id para consistencia
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    # CAMBIO: es_principal a is_main
    is_main = db.Column(db.Boolean, default=False) # Para identificar la imagen principal

    def __repr__(self):
        return f"PropertyImage('{self.filename}', Property ID: {self.property_id})"

# ##################################################################
# INICIO: Modelo de Usuario
# ##################################################################
class User(db.Model, UserMixin):
    __tablename__ = 'user' # Añadido nombre de tabla explícito
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # CAMBIO: Añadir la columna email
    email = db.Column(db.String(120), unique=True, nullable=False) 
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
