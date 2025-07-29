# models.py

# 1. Importaciones de la biblioteca estándar (Python built-in)
import re
from datetime import datetime, timezone # Añadido 'timezone' para datetime.now(timezone.utc)

# 2. Importaciones de terceros (Flask, SQLAlchemy, etc.)
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db # Asumo que 'db' se inicializa en 'extensions.py'

# ##################################################################
# INICIO: Modelo de Usuario (generalmente se define antes si otras clases dependen de él)
# ##################################################################
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=True) # nullable=True es redundante si hay default

    # Relación inversa para acceder a las propiedades gestionadas por este usuario
    # 'managed_properties' es el backref que usaste en Property
    properties = db.relationship('Property', backref='agente', lazy=True, cascade="all, delete-orphan")


    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
# ##################################################################
# FIN: Modelo de Usuario
# ##################################################################


class Property(db.Model):
    __tablename__ = 'property'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    # CAMBIO: Usar db.Numeric para precios y cuotas para evitar problemas de coma flotante
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    ubicacion = db.Column(db.String(200), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)
    property_options = db.Column(db.String(100), nullable=False) # Venta, Renta, etc.
    tipo_propiedad = db.Column(db.String(50), nullable=False) # Casa, Departamento, Terreno, etc.
    num_habitaciones = db.Column(db.Integer, nullable=True)
    num_banos = db.Column(db.Integer, nullable=True)
    num_medios_banos = db.Column(db.Integer, default=0)
    num_estacionamientos = db.Column(db.Integer, default=0)
    area_construccion_metros_cuadrados = db.Column(db.Numeric(10, 2), nullable=True) # CAMBIO: Numeric
    area_terreno_metros_cuadrados = db.Column(db.Numeric(10, 2), nullable=True) # CAMBIO: Numeric
    antiguedad_tipo = db.Column(db.String(50), nullable=True)
    antiguedad_anos = db.Column(db.Integer, nullable=True)
    cuota_mantenimiento = db.Column(db.Numeric(10, 2), default=0.0) # CAMBIO: Numeric
    # CAMBIO: Usar datetime.now(timezone.utc) en lugar de datetime.utcnow (deprecated)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    youtube_video_url = db.Column(db.String(255), nullable=True)

    # Añadida relación con User para saber qué agente la publicó
    agente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # CAMBIO: backref='agente' aquí para que la relación inversa en User sea 'properties'
    # agente = db.relationship('User', backref='managed_properties') # Ya definido en User

    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade="all, delete-orphan")



    # MÉTODO CORREGIDO: Extrae el ID único del video de YouTube de su URL (soporta videos y Shorts)
    def get_youtube_video_id(self):
        """
        Extrae el ID del video de YouTube de la URL almacenada en youtube_video_url.
        Soporta formatos de videos largos y URLs de YouTube Shorts.
        """
        if not self.youtube_video_url:
            return None
        
        # Importar re aquí para asegurar que siempre esté disponible,
        # aunque es mejor importarlo una vez al principio del archivo.
        import re 

        # Patrón para URLs de videos normales: watch?v=, /embed/, youtu.be/, m.youtube.com/watch?v=
        # re.search busca el patrón en cualquier parte de la cadena
        match_v = re.search(
            r'(?:v=|embed\/|youtu\.be\/|m\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            self.youtube_video_url
        )
        if match_v:
            return match_v.group(1) # El grupo 1 es el ID del video

        # Patrón para URLs de Shorts: shorts/
        match_shorts = re.search(r'shorts\/([a-zA-Z0-9_-]{11})', self.youtube_video_url)
        if match_shorts:
            return match_shorts.group(1) # El grupo 1 es el ID del Short

        return None # Si no encuentra ningún patrón válido

    # MÉTODO get_youtube_thumbnail_url (no necesita cambios si get_youtube_video_id funciona)
    def get_youtube_thumbnail_url(self):
        """
        Genera la URL de la miniatura de YouTube a partir del ID del video.
        Retorna la URL de una miniatura de alta calidad (480x360).
        """
        video_id = self.get_youtube_video_id()
        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        return None


    def __repr__(self):
        return f"Property('{self.titulo}', '{self.ubicacion}', '{self.precio}')"


# Renombrado de Imagen a PropertyImage
class PropertyImage(db.Model):
    __tablename__ = 'property_image' # Añadido nombre de tabla explícito
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(200), nullable=True) # Ruta relativa del archivo (ej. 'uploads/1/foto.jpg')
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    is_main = db.Column(db.Boolean, default=False) # Para identificar la imagen principal

    def __repr__(self):
        return f"PropertyImage('{self.filename}', Path: '{self.path}', Property ID: {self.property_id})"
