from extensions import db
from datetime import datetime

db = SQLAlchemy()

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # Relationships
    addresses = db.relationship('Address', backref='user', lazy=True)
    payment_methods = db.relationship('PaymentMethod', backref='user', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

# Address Model
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# PaymentMethod Model
class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(16), nullable=False)
    expiration_date = db.Column(db.String(7), nullable=False)  # Format: MM/YYYY
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Service Model
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200))  # Optional image URL
    # Relationships
    bookings = db.relationship('Booking', backref='service', lazy=True)
    reviews = db.relationship('Review', backref='service', lazy=True)

# Booking Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    recurrence = db.Column(db.String(20))  # e.g., 'weekly'
    status = db.Column(db.String(20), default='confirmed')  # e.g., 'confirmed', 'paid'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    transactions = db.relationship('Transaction', backref='booking', lazy=True)
# Review Model
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # e.g., 1-5
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Notification Model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# SupportTicket Model
class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Optional (for guest users)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)