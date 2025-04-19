from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

class User(UserMixin, db.Model):
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('companies', lazy=True))

class TODOO(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(25), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('todos', lazy=True))

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