from extensions import db
from datetime import datetime

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary(128), nullable=False)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    services = db.relationship('Service', back_populates='category', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200)) #image url optional
    # Relationships
    category = db.relationship('Category', back_populates='services')
    transactions = db.relationship('Transaction', backref='service', lazy=True)
    reviews = db.relationship('Review', backref='service', lazy=True)
    disputes = db.relationship('Dispute', backref='service', lazy=True)
    bookings = db.relationship('Booking', backref='service', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.id} - User {self.user_id} - Service {self.service_id}>"

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


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    content = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', name='review_status'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    addresses = db.relationship('Address', backref='user', lazy=True)
    payment_methods = db.relationship('PaymentMethod', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    disputes = db.relationship('Dispute', backref='user', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

class Dispute(db.Model):
    __tablename__ = 'disputes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Open")

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


# Provider Model
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Provider(UserMixin, db.Model):  # Renamed from User to Provider
    __tablename__ = 'providers'  # Explicit table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    license_pdf = db.Column(db.String(255))  # Path to file
    logo = db.Column(db.String(255))  # Path to file
    date = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer, default=5)
    available_time = db.Column(db.String(50))
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)  # Changed from user_id
    provider = db.relationship('Provider', backref=db.backref('companies', lazy=True))  # Changed from User

class TODOO(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(25), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)  # Changed from user_id
    provider = db.relationship('Provider', backref=db.backref('todos', lazy=True))  # Changed from User

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo = db.Column(db.String(255))  # Path to file
    name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer)
    description = db.Column(db.Text, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    
    company = db.relationship('Company', backref=db.backref('services', lazy=True))

class Bookings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booker = db.Column(db.Text, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.Text, nullable=False)
    usercomment = db.Column(db.Text)
    procomment = db.Column(db.Text)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    
    service = db.relationship('Service', backref=db.backref('bookings', lazy=True))

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    commenter = db.Column(db.Text, default='anonymous')
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    
    company = db.relationship('Company', backref=db.backref('comments', lazy=True))