from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))

    company = db.relationship('Company', backref='user', uselist=False)
    todos = db.relationship('TODOO', backref='user', lazy=True)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    license_pdf = db.Column(db.String(255))
    logo = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer, default=5)
    available_time = db.Column(db.String(50))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    services = db.relationship('Service', backref='company', lazy=True)
    comments = db.relationship('Comments', backref='company', lazy=True)


class TODOO(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(25))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo = db.Column(db.String(255))
    name = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    description = db.Column(db.Text)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    bookings = db.relationship('Bookings', backref='service', lazy=True)


class Bookings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booker = db.Column(db.Text)
    time = db.Column(db.Time)
    location = db.Column(db.Text)
    usercomment = db.Column(db.Text)
    procomment = db.Column(db.Text)

    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    commenter = db.Column(db.Text, default="anonymous")

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)