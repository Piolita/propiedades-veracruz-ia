import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_cadena_secreta_muy_dificil_de_adivinar'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://cmagna:0315@localhost:5432/propiedades_veracruz_ia_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False