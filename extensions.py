# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

# Shared Extensions
db = SQLAlchemy()

# ✅ Single Flask-Admin instance shared across modules
admin = Admin(name='Admin Panel', template_mode='bootstrap3', url='/admin_dashboard')