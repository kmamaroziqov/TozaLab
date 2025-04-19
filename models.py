from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary(128), nullable=False)
    role = db.Column(db.String(20), default="Admin")

    transactions = db.relationship('Transaction', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    disputes = db.relationship('Dispute', backref='user', lazy=True)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # ✅ Corrected Relationship
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

    # ✅ Use back_populates instead of conflicting backref
    category = db.relationship('Category', back_populates='services')
    transactions = db.relationship('Transaction', backref='service', lazy=True)
    reviews = db.relationship('Review', backref='service', lazy=True)
    disputes = db.relationship('Dispute', backref='service', lazy=True)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.id} - User {self.user_id} - Service {self.service_id}>"


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    content = db.Column(db.String, nullable=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', name='review_status'), default='pending')


class Dispute(db.Model):
    __tablename__ = 'disputes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Open")