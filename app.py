# app.py
from flask import Flask, request, jsonify
from extensions import db  # Import db from extensions.py
from models import User, Service, Category, Transaction, DashboardView  # Import your models
from config import stripe  # Import Stripe configuration
from flask_migrate import Migrate 
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from auth import hash_password, verify_password, create_jwt_token, role_required  # Import authentication utilities
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
 # Import Flask-Migrate

# Initialize Flask app
app = Flask(__name__)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-SQLAlchemy
db.init_app(app)

admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Service, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Transaction, db.session))
admin.add_view(DashboardView(name='Dashboard', endpoint='dashboard'))

# Initialize Flask-Migrate
migrate = Migrate(app, db)



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
    existing_user = db.session.query(User).filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    # Hash the password and create a new user
    password_hash = hash_password(password)
    new_user = User(username=username, password_hash=password_hash, role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Find the user in the database
    user = db.session.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({"message": "Invalid credentials"}), 401

    # Generate JWT token
    token = create_jwt_token(user.id, user.role)
    return jsonify({"token": token}), 200

@app.route('/users', methods=['GET'])
@role_required(['Super Admin'])  # Only admins can access this route
def get_users():
    users = db.session.query(User).all()
    user_list = [
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        }
        for user in users
    ]
    return jsonify(user_list), 200

@app.route('/users/<int:user_id>', methods=['GET'])
@role_required(['Super Admin'])  # Only admins can access this route
def get_user(user_id):
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role
    }), 200

@app.route('/users/<int:user_id>', methods=['PUT'])
@role_required(['Super Admin'])  # Only admins can access this route
def update_user(user_id):
    data = request.get_json()
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Update fields if provided
    user.role = data.get('role', user.role)
    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
@role_required(['Super Admin', 'Admin'])  # Only admins can access this route
def delete_user(user_id):
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

@app.route('/users/search', methods=['GET'])
@role_required(['Super Admin'])  # Only admins can access this route
def search_users():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"message": "Search query is required"}), 400
    users = db.session.query(User).filter(User.username.ilike(f'%{query}%')).all()
    user_list = [
        {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
        for user in users
    ]
    return jsonify(user_list), 200

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
    db.session.add(new_service)
    db.session.commit()
    return jsonify({"message": "Service created successfully", "service_id": new_service.id}), 201

@app.route('/services', methods=['GET'])
def list_services():
    services = db.session.query(Service).all()
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
    service = db.session.query(Service).filter_by(id=service_id).first()
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
    service = db.session.query(Service).filter_by(id=service_id).first()
    if not service:
        return jsonify({"message": "Service not found"}), 404
    service.name = data.get('name', service.name)
    service.price = data.get('price', service.price)
    service.category = data.get('category', service.category)
    service.description = data.get('description', service.description)
    db.session.commit()
    return jsonify({"message": "Service updated successfully"}), 200

@app.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    service = db.session.query(Service).filter_by(id=service_id).first()
    if not service:
        return jsonify({"message": "Service not found"}), 404
    db.session.delete(service)
    db.session.commit()
    return jsonify({"message": "Service deleted successfully"}), 200

@app.route('/categories', methods=['POST'])
@role_required(['Admin', 'Super Admin'])  # Only admins can access this route
def create_category():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"message": "Category name is required"}), 400
    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message": "Category created successfully", "category_id": new_category.id}), 201

@app.route('/categories', methods=['GET'])
def list_categories():
    categories = db.session.query(Category).all()
    category_list = [{"id": category.id, "name": category.name} for category in categories]
    return jsonify(category_list), 200

@app.route('/categories/<int:category_id>', methods=['DELETE'])
@role_required(['Admin', 'Super Admin'])  # Only admins can access this route
def delete_category(category_id):
    category = db.session.query(Category).get(category_id)
    if not category:
        return jsonify({"message": "Category not found"}), 404
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted successfully"}), 200

@app.route('/payment', methods=['POST'])
def process_payment():
    try:
        # Get payment details from the request body
        data = request.json
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        token = data.get('token')
        user_id = data.get('user_id')
        service_id = data.get('service_id')

        if not amount or not token or not user_id or not service_id:
            return jsonify({'error': 'Missing required fields'}), 400

        # Create a charge using Stripe's API
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            source=token,
            description='Payment for service'
        )

        # Log the transaction in the database
        transaction = Transaction(
            user_id=user_id,
            service_id=service_id,
            amount=amount,
            currency=currency,
            status='success'
        )
        db.session.add(transaction)
        db.session.commit()

        # Return success response
        return jsonify({
            'message': 'Payment successful',
            'charge_id': charge.id,
            'transaction_id': transaction.id
        }), 200

    except stripe.error.CardError as e:
        # Handle card errors (e.g., insufficient funds)
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # Log the full error for debugging
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the payment'}), 500

if __name__ == '__main__':
    app.run(debug=True)