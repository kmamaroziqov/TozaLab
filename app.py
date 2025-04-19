from flask import render_template, request, redirect, url_for, session, flash, jsonify, make_response
from extensions import db, admin
from models import User, Service, Category, Transaction, Review
from config import stripe
from flask_migrate import Migrate
from auth import hash_password, verify_password, create_jwt_token, role_required
from application import app
from firebase_setup import broadcast_to_topic
import logging

logging.basicConfig(
    level=logging.INFO,  # Log only INFO-level messages and above
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Write logs to a file
        logging.StreamHandler()         # Also print logs to the console
    ]
)
logger = logging.getLogger(__name__)

migrate = Migrate(app, db)


# Home route
@app.route('/')
def home():
    return "Welcome to the API! Available endpoints: /register, /login, /admin/dashboard"

#--------------------- Register endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'Admin')  # Default role is "Admin"

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

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

# Add this to app.py
@app.route('/admin/users/create', methods=['GET', 'POST'])
@role_required(['Admin', 'Super Admin'])
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'Admin')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('create_user'))

        user = User(username=username, password_hash=hash_password(password), role=role)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_manage_users'))

    return render_template('create_user.html')  # Create a new template

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@role_required(['Admin', 'Super Admin'])
def edit_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin_manage_users'))

    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role')
        
        user.username = username if username else user.username
        user.role = role if role else user.role
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_manage_users'))
    
    return render_template('edit_user.html', user=user)

#--------------------- Login endpoint
# Enhanced Login Route with Error Logging
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            logger.warning("Login attempt with missing credentials")
            return jsonify({"message": "Username and password are required"}), 400

        user = User.query.filter_by(username=username).first()
        if not user or not verify_password(password, user.password_hash):
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({"message": "Invalid credentials"}), 401

        token = create_jwt_token(user.id, user.role)
        logger.info(f"User {username} logged in successfully")
        return jsonify({"token": token}), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"message": "An error occurred during login"}), 500

#--------------------- User endpoints
@app.route('/users', methods=['GET'])
@role_required(['Super Admin'])  # Only Super Admins can access this route
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


# Get a single user by ID (Admin only)
@app.route('/users/<int:user_id>', methods=['GET'])
@role_required(['Super Admin'])  # Only Super Admins can access this route
def get_user(user_id):
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role
    }), 200

# Update a user (Admin only)
@app.route('/users/<int:user_id>', methods=['PUT'])
@role_required(['Super Admin'])  # Only Super Admins can access this route
def update_user(user_id):
    data = request.get_json()
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Update fields if provided
    user.role = data.get('role', user.role)
    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200

# Delete a user (Admin only)
@app.route('/users/<int:user_id>', methods=['POST'])
@role_required(['Super Admin', 'Admin'])
def delete_user(user_id):
    if request.form.get('_method') == 'DELETE':
        user = db.session.query(User).get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
        return redirect(url_for('admin_manage_users'))
    return jsonify({"message": "Invalid request"}), 400

# Search users (Admin only)
@app.route('/users/search', methods=['GET'])
@role_required(['Super Admin'])  # Only Super Admins can access this route
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

#--------------------- Service endpoints
@app.route('/services', methods=['POST'])
def create_service():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    category_id = data.get('category_id')  # ✅ Use category_id instead of category name
    description = data.get('description')

    if not name or not price or not category_id:
        return jsonify({"message": "Name, price, and category_id are required"}), 400

    new_service = Service(name=name, price=price, category_id=category_id, description=description)
    db.session.add(new_service)
    db.session.commit()
    return jsonify({"message": "Service created successfully", "service_id": new_service.id}), 201

# List all services
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

# Get a single service by ID
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

# Update a service
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

# Delete a service
@app.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    service = db.session.query(Service).filter_by(id=service_id).first()
    if not service:
        return jsonify({"message": "Service not found"}), 404
    db.session.delete(service)
    db.session.commit()
    return jsonify({"message": "Service deleted successfully"}), 200

#--------------------- Category endpoints
@app.route('/categories', methods=['POST'])
@role_required(['Admin', 'Super Admin'])  # Only Admins can access this route
def create_category():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"message": "Category name is required"}), 400

    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message": "Category created successfully", "category_id": new_category.id}), 201

# List all categories
@app.route('/categories', methods=['GET'])
def list_categories():
    categories = db.session.query(Category).all()
    category_list = [{"id": category.id, "name": category.name} for category in categories]
    return jsonify(category_list), 200

# Delete a category (Admin only)
@app.route('/categories/<int:category_id>', methods=['DELETE'])
@role_required(['Admin', 'Super Admin'])  # Only Admins can access this route
def delete_category(category_id):
    category = db.session.query(Category).get(category_id)
    if not category:
        return jsonify({"message": "Category not found"}), 404
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted successfully"}), 200

#--------------------- Payment endpoint
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

#--------------------- Review endpoints
@app.route('/reviews', methods=['GET'])
@role_required(['Admin', 'Super Admin'])  # Only admins can access this route
def get_reviews():
    reviews = db.session.query(Review).all()
    review_list = [
        {
            "id": review.id,
            "user_id": review.user_id,
            "service_id": review.service_id,
            "content": review.content,
            "status": review.status
        }
        for review in reviews
    ]
    return jsonify(review_list), 200

# Get a single review by ID (Admin only)
@app.route('/reviews/<int:review_id>', methods=['GET'])
@role_required(['Admin', 'Super Admin'])  # Only admins can access this route
def get_review(review_id):
    review = db.session.query(Review).get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404
    return jsonify({
        "id": review.id,
        "user_id": review.user_id,
        "service_id": review.service_id,
        "content": review.content,
        "status": review.status
    }), 200

# Create a new review
@app.route('/reviews', methods=['POST'])
def create_review():
    data = request.get_json()
    user_id = data.get('user_id')
    service_id = data.get('service_id')
    content = data.get('content')

    if not user_id or not service_id or not content:
        return jsonify({"message": "User ID, Service ID, and Content are required"}), 400

    new_review = Review(
        user_id=user_id,
        service_id=service_id,
        content=content,
        status='pending'  # Default status is "pending"
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({"message": "Review created successfully", "review_id": new_review.id}), 201

# Approve a review (Admin only)
@app.route('/reviews/<int:review_id>/approve', methods=['POST'])
@role_required(['Admin', 'Super Admin'])  # Only admins can access this route
def approve_review(review_id):
    review = db.session.query(Review).get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404
    review.status = 'approved'
    db.session.commit()
    return jsonify({"message": "Review approved successfully"}), 200

# Reject a review (Admin only)
@app.route('/reviews/<int:review_id>/reject', methods=['POST'])
@role_required(['Admin', 'Super Admin'])  # Only admins can access this route
def reject_review(review_id):
    review = db.session.query(Review).get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404
    review.status = 'rejected'
    db.session.commit()
    return jsonify({"message": "Review rejected successfully"}), 200

# Delete a review (Admin only)
@app.route('/reviews/<int:review_id>', methods=['DELETE'])
@role_required(['Admin', 'Super Admin'])  # Only admins can access this route
def delete_review(review_id):
    review = db.session.query(Review).get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted successfully"}), 200

#------------------ Admin endpoints

@app.route('/admin/dashboard', methods=['GET'])
@role_required(['Admin', 'Super Admin'])  # Only Admins and Super Admins can access this route
def admin_dashboard():
    return render_template('admin_dashboard.html', logout_url=url_for('admin_logout'))


# Task 1: Show HTML Admin Login Page (GET request)
@app.route('/admin/login', methods=['GET'])
def admin_login_page():
    return render_template('admin_login.html')

# Task 2: Handle Admin Login (POST request)
@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter(User.username == username, User.role.in_(['Admin', 'Super Admin'])).first()
    
    if not user or not verify_password(password, user.password_hash):
        logger.warning(f"Failed admin login attempt for username: {username}")
        flash('Invalid credentials', 'danger')
        return redirect(url_for('admin_login_page'))
    
    logger.info(f"Successful admin login for username: {username}")
    token = create_jwt_token(user.id, user.role)
    response = make_response(redirect(url_for('admin_dashboard')))
    response.set_cookie('admin_token', token, httponly=True, secure=True, samesite='Strict')
    session['user_role'] = user.role
    session['user_id'] = user.id
    flash('Welcome to Admin Panel!', 'success')
    return response


# --------admin logout    
# ✅ Admin Logout Route (Updated)
@app.route('/admin/logout', methods=['GET', 'POST'])
@role_required(['Admin', 'Super Admin'])
def admin_logout():
    if request.method == 'POST' or request.method == 'GET':
        response = make_response(redirect(url_for('admin_login_page')))
        response.delete_cookie('admin_token')  # Clear token
        session.clear()  # Clear session
        flash('Logged out successfully', 'success')
        return response
    
    return jsonify({'message': 'Method Not Allowed'}), 405

# ✅ Add Routes for Admin Panel Buttons
@app.route('/admin/users', methods=['GET'])
@role_required(['Admin', 'Super Admin'])
def admin_manage_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/services', methods=['GET'])
@role_required(['Admin', 'Super Admin'])
def admin_manage_services():
    services = Service.query.all()
    return render_template('admin_services.html', services=services)

@app.route('/admin/reviews', methods=['GET'])
@role_required(['Admin', 'Super Admin'])
def admin_manage_reviews():
    reviews = Review.query.all()
    return render_template('admin_reviews.html', reviews=reviews)


#----------Broadcast Notification
@app.route('/admin/broadcast', methods=['POST'])
@role_required(['Admin', 'Super Admin'])
def broadcast_notification():
    title = request.form.get('title')
    body = request.form.get('body')
    broadcast_to_topic(title, body)
    flash('Announcement sent to all users!', 'success')
    return redirect(url_for('admin_dashboard'))

# API Error Logging Middleware
@app.errorhandler(Exception)
def handle_api_error(error):
    logger.error(f"API error: {error}")
    response = jsonify({"message": "An internal error occurred."})
    response.status_code = 500
    return response

logger.info("Logging configuration complete.")

if __name__ == '__main__':
    app.run(debug=True)