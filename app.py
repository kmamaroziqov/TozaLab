# app.py
from flask import Flask, request, jsonify
from models import User, Base, Service
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import hash_password, verify_password, create_jwt_token, role_required
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
@app.route('/')
def home():
    return "Welcome to the API! Available endpoints: /register, /login, /admin/dashboard"

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

# Admin dashboard endpoint
@app.route('/admin/dashboard', methods=['GET'])
@role_required(['Admin', 'Super Admin'])  # Only Admins and Super Admins can access this route
def admin_dashboard():
    return jsonify({"message": "Welcome to the admin dashboard!"}), 200

@app.route('/services', methods=['POST'])
def create_service():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    category = data.get('category')
    description = data.get('description')

    if not name or not price or not category:
        return jsonify({"message": "Name, price, and category are required"}), 400

    new_service = Service(name=name, price=price, category=category, description=description)
    session.add(new_service)
    session.commit()

    return jsonify({"message": "Service created successfully", "service_id": new_service.id}), 201

@app.route('/services', methods=['GET'])
def list_services():
    services = session.query(Service).all()
    service_list = [
        {
            "id": service.id,
            "name": service.name,
            "price": service.price,
            "category": service.category,
            "description": service.description
        }
        for service in services
    ]
    return jsonify(service_list), 200

@app.route('/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    service = session.query(Service).filter_by(id=service_id).first()
    if not service:
        return jsonify({"message": "Service not found"}), 404

    return jsonify({
        "id": service.id,
        "name": service.name,
        "price": service.price,
        "category": service.category,
        "description": service.description
    }), 200

@app.route('/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    data = request.get_json()
    service = session.query(Service).filter_by(id=service_id).first()
    if not service:
        return jsonify({"message": "Service not found"}), 404

    service.name = data.get('name', service.name)
    service.price = data.get('price', service.price)
    service.category = data.get('category', service.category)
    service.description = data.get('description', service.description)

    session.commit()
    return jsonify({"message": "Service updated successfully"}), 200

@app.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    service = session.query(Service).filter_by(id=service_id).first()
    if not service:
        return jsonify({"message": "Service not found"}), 404

    session.delete(service)
    session.commit()
    return jsonify({"message": "Service deleted successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)