# models.py
from extensions import db  # Import db from extensions.py
from datetime import datetime
from flask_admin import BaseView, expose

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary(128), nullable=False)  # Increase size to 128
    role = db.Column(db.String(20), default="Admin")  # Default role is "Admin"

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Link to the user
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)  # Link to the service
    amount = db.Column(db.Integer, nullable=False)  # Amount in cents (e.g., $10.00 = 1000)
    currency = db.Column(db.String(3), nullable=False)  # Currency code (e.g., "usd")
    status = db.Column(db.String(20), nullable=False)  # Status: "success", "failed", etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp

    def __repr__(self):
        return f"<Transaction {self.id} - User {self.user_id} - Service {self.service_id}>"

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Pending")  # Pending, Approved, Rejected

class Dispute(db.Model):
    __tablename__ = 'disputes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Open")  # Open, Resolved
class DashboardView(BaseView):
    @expose('/')
    def index(self):
        # Fetch data from the database
        total_users = db.session.query(User).count()
        active_users = db.session.query(User).filter_by(role='user').count()
        total_services = db.session.query(Service).count()
        total_revenue = sum(t.amount for t in db.session.query(Transaction).filter_by(status='success'))

        # Render the dashboard with metrics
        return self.render('admin/dashboard.html',
                           total_users=total_users,
                           active_users=active_users,
                           total_services=total_services,
                           total_revenue=total_revenue)