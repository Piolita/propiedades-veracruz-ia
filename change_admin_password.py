import os
from werkzeug.security import generate_password_hash
from app import app, db, User # Importa la app y los modelos desde tu app.py

# Asegúrate de que la ruta de la base de datos sea la misma que en app.py
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')

def change_password():
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            # ¡IMPORTANTE! Reemplaza 'Mylord_1964/propiedades-veracruz' con la contraseña que quieres
            new_password_raw = 'Mylord_1964/propiedades-veracruz'
            hashed_password = generate_password_hash(new_password_raw, method='pbkdf2:sha256')
            admin_user.password = hashed_password
            db.session.commit()
            print(f"Contraseña del usuario 'admin' actualizada exitosamente a: {new_password_raw}")
        else:
            print("Error: Usuario 'admin' no encontrado en la base de datos.")

if __name__ == '__main__':
    change_password()
