from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Propiedad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(100), nullable=False) # Se refiere al estado de Veracruz
    codigo_postal = db.Column(db.String(10), nullable=True)
    num_habitaciones = db.Column(db.Integer, nullable=False)
    num_banos = db.Column(db.Integer, nullable=False)
    num_medios_banos = db.Column(db.Integer, nullable=True) # Nuevo campo para el número de medios baños.
    num_estacionamientos = db.Column(db.Integer, nullable=True)
    antiguedad = db.Column(db.Integer, nullable=True) # Nuevo campo: Antigüedad de la propiedad en años.
    area_terreno_metros_cuadrados = db.Column(db.Numeric(10, 2), nullable=True)
    area_construccion_metros_cuadrados = db.Column(db.Numeric(10, 2), nullable=False)
    tipo = db.Column(db.String(50), nullable=False) # Ej. Casa, Departamento, Terreno
    cuota_mantenimiento = db.Column(db.Numeric(10, 2), nullable=True)
    estado_propiedad = db.Column(db.String(50), nullable=False) # Ej. Venta, Alquiler

    # Relación con las imágenes (una propiedad puede tener varias imágenes)
    imagenes = db.relationship('Imagen', backref='propiedad', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Propiedad {self.titulo} - {self.direccion}>'

class Imagen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(200), nullable=False)
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedad.id'), nullable=False)
    es_principal = db.Column(db.Boolean, default=False, nullable=False) # Nuevo campo

    def __repr__(self):
        return f'<Imagen {self.nombre_archivo}>'