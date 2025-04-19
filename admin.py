# admin.py (Fixed)
from flask_admin.contrib.sqla import ModelView
from extensions import db, admin
from models import User, Service, Category, Review, Transaction
from flask import redirect, url_for, flash, session, render_template, request, jsonify
from auth import role_required, decode_jwt_token
from application import app

# ✅ Custom ModelView with token check
class AdminModelView(ModelView):
    def is_accessible(self):
        token = request.cookies.get('admin_token')  # ✅ Check for cookie token
        if not token:
            flash('Missing admin token', 'danger')
            return False
        try:
            payload = decode_jwt_token(token)
            return payload.get('role') in ['Admin', 'SuperAdmin']
        except Exception as e:
            flash(f'Invalid token: {str(e)}', 'danger')
            return False

# ✅ Register Admin Views
admin.add_view(AdminModelView(User, db.session, endpoint='users_admin'))
admin.add_view(AdminModelView(Service, db.session, endpoint='services_admin'))
admin.add_view(AdminModelView(Category, db.session, endpoint='categories_admin'))
admin.add_view(AdminModelView(Review, db.session, endpoint='reviews_admin'))
admin.add_view(AdminModelView(Transaction, db.session, endpoint='transactions_admin'))
