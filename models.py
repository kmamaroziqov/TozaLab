# models.py
from sqlalchemy import Column, Integer, String, LargeBinary, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(LargeBinary(128), nullable=False)  # Increase size to 128 
    role = Column(String(20), default="Admin")  # Default role is "Admin"

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), default="Pending")  # Pending, Approved, Rejected

class Dispute(Base):
    __tablename__ = 'disputes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="Open")  # Open, Resolved