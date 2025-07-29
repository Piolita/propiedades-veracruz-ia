# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, Optional, ValidationError, URL
from flask_wtf.file import FileField, FileAllowed
from markupsafe import Markup # Para permitir HTML seguro en las opciones de SelectField

# --- Formulario de Login ---
class LoginForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

# --- Formulario para Añadir Propiedad ---
class PropertyForm(FlaskForm):
    titulo = StringField('Título de la Propiedad', validators=[DataRequired(), Length(min=5, max=100)])
    descripcion = TextAreaField('Descripción Detallada', validators=[DataRequired(), Length(min=20)])
    precio = DecimalField('Precio de Venta/Renta', validators=[DataRequired(), NumberRange(min=0, message="El precio no puede ser negativo.")])
    ubicacion = StringField('Ubicación (Colonia, Fraccionamiento)', validators=[DataRequired(), Length(min=5, max=100)])

    # Opciones para municipio (puedes expandir esta lista)
    municipio = SelectField('Municipio', validators=[DataRequired()],
                            choices=[
                                ('Veracruz', 'Veracruz'),
                                ('Boca del Río', 'Boca del Río'),
                                ('Medellín', 'Medellín de Bravo'),
                                ('Alvarado', 'Alvarado Riviera Veracruzana'),
                                ('Otro', 'Otro'),
                            ],
                            render_kw={'class': 'form-control'}) # render_kw es para atributos HTML

    property_options = SelectField('Opción', choices=[('Venta', 'Venta'), ('Renta', 'Renta')], validators=[DataRequired()])
    tipo_propiedad = SelectField('Tipo de Propiedad', validators=[DataRequired()],
                                 choices=[
                                     ('Casa', 'Casa'),
                                     ('Departamento', 'Departamento'),
                                     ('Terreno', 'Terreno'),
                                     ('Local', 'Local Comercial'),
                                     ('Oficina', 'Oficina'),
                                     ('Bodega', 'Bodega')
                                 ])
    # CAMBIO: Transformación del campo Antigüedad
    antiguedad_option = SelectField('Antigüedad', choices=[
        ('', 'Selecciona una opción'), # Opción vacía por defecto
        ('new', 'Nueva'),
        ('years', 'Años')
    ], validators=[Optional()]) # Es opcional si no se selecciona nada (siempre puedes guardar NULL)
    antiguedad_years = IntegerField('¿Cuántos años?', validators=[Optional(), NumberRange(min=0)])
    # FIN CAMBIO
    
    num_habitaciones = IntegerField('Recamaras', validators=[Optional(), NumberRange(min=0)])
    num_banos = IntegerField('Baños Completos', validators=[Optional(), NumberRange(min=0)])
    num_medios_banos = IntegerField('Medios Baños', validators=[Optional(), NumberRange(min=0)])
    num_estacionamientos = IntegerField('Estacionamientos', validators=[Optional(), NumberRange(min=0)])
    area_terreno_metros_cuadrados = DecimalField('Área de Terreno (m²)', validators=[Optional(), NumberRange(min=0)])
    area_construccion_metros_cuadrados = DecimalField('Área de Construcción (m²)', validators=[Optional(), NumberRange(min=0)])
    cuota_mantenimiento = DecimalField('Cuota de Mantenimiento', validators=[Optional(), NumberRange(min=0)])

    youtube_video_url = StringField('URL de Video de YouTube (Opcional)', validators=[Optional(), URL(message='Por favor, introduce una URL de YouTube válida.')])
    
    # Campo para la subida de múltiples imágenes
    imagenes = FileField('Subir Imágenes', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo se permiten imágenes (JPG, JPEG, PNG, GIF, WEBP)!'),
        Optional() # Las imágenes no son obligatorias al añadir una propiedad
    ])

    submit = SubmitField('Añadir Propiedad')

# --- Formulario para Editar Propiedad 
class EditPropertyForm(PropertyForm):
    # Aquí podríamos añadir campos específicos para la edición de imágenes,
    # como checkboxes para eliminar imágenes existentes o un campo para cambiar la imagen principal.
    # Por ahora, simplemente heredamos y se manejará la subida de nuevas imágenes.

    # Para la eliminación de imágenes existentes (se manejará por ID en la vista)
    # y para la selección de imagen principal (también por ID en la vista)
    # No los definimos como campos WTForms aquí porque serán elementos HTML dinámicos.

    submit = SubmitField('Actualizar Propiedad')




# Formulario de Registro de Usuario
class RegisterForm(FlaskForm):
    username = StringField('Nombre de Usuario',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña',
                                     validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir.')])
    submit = SubmitField('Registrarse')

    # Validaciones personalizadas para username y email
    def validate_username(self, username):
        # CAMBIO: Importa User aquí para evitar importación circular. Asegúrate de que esta importación sea necesaria.
        # Si 'app' es donde se inicializa db, podrías necesitar un import local o manejar la importación en __init__.py
        from .models import User 
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ese nombre de usuario ya está en uso. Por favor, elige uno diferente.')

    def validate_email(self, email):
        # CAMBIO: Importa User aquí para evitar importación circular.
        from .models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ese email ya está registrado. Por favor, utiliza uno diferente.')
