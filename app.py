# app.py
from flask import Flask, request, jsonify
from models import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import hash_password, verify_password, create_jwt_token
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Create tables (run this once to initialize the database)
Base.metadata.create_all(engine)

# Register endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'Admin')  # Default role is "Admin"

    # Check if the user already exists
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    # Hash the password and create a new user
    password_hash = hash_password(password)
    new_user = User(username=username, password_hash=password_hash, role=role)
    session.add(new_user)
    session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Find the user in the database
    user = session.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({"message": "Invalid credentials"}), 401

    # Generate JWT token
    token = create_jwt_token(user.id, user.role)
    return jsonify({"token": token}), 200

if __name__ == '__main__':
    app.run(debug=True)