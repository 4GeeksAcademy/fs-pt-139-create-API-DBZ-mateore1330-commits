"""
Este módulo configura el panel de administración (Flask-Admin), desde donde
se pueden gestionar visualmente los modelos de la base de datos.
"""
import os
from flask_admin import Admin
from models import db, User, Character, Planet
from flask_admin.contrib.sqla import ModelView


def setup_admin(app):
    # Clave secreta necesaria para las sesiones del panel de administración
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    # Modelos disponibles en el panel de administración
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Character, db.session))
    admin.add_view(ModelView(Planet, db.session))

    # Puedes duplicar la línea de arriba para añadir nuevos modelos, por ejemplo:
    # admin.add_view(ModelView(NombreDeTuModelo, db.session))