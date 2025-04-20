from flask import render_template, request, redirect, url_for, session, flash, jsonify, make_response
from application import db
from models import Admin, Service, Category, Transaction, Review, User
from config import stripe
from auth import hash_password, verify_password, create_jwt_token, role_required
from firebase_setup import broadcast_to_topic
from flask import Blueprint
import logging

routes = Blueprint("routes", __name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@routes.route('/')
def home():
    return render_template('home.html')

#--------------------- Register endpoint
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not all([full_name, email, phone_number, password, confirm_password]):
            flash("All fields are required.", "danger")
            return redirect(url_for('routes.register'))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('routes.register'))

        # Check for existing user by full name
        existing_user = User.query.filter_by(full_name=full_name).first()
        if existing_user:
            flash("A user with this name already exists.", "danger")
            return redirect(url_for('routes.register'))

        # Create new user
        hashed_password = hash_password(password)
        new_user = User(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password_hash=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('routes.login'))

    # GET request: Render registration form
    return render_template('user/user_register.html')

# Service Search Route
@routes.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    services = Service.query.filter(Service.name.contains(query)).all()
    return render_template('user/search.html', services=services)


# Service Detail Route
@routes.route('/service/<int:service_id>', methods=['GET'])
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)
    reviews = Review.query.filter_by(service_id=service_id).all()
    return render_template('service_detail.html', service=service, reviews=reviews)

# Add this to app.py
@routes.route('/admin/Admins/create', methods=['GET', 'POST'])
def create_Admin():
    if request.method == 'POST':
        Adminname = request.form.get('Adminname')
        password = request.form.get('password')
        role = request.form.get('role', 'Admin')

        if Admin.query.filter_by(Adminname=Adminname).first():
            flash('Adminname already exists.', 'danger')
            return redirect(url_for('create_Admin'))

        Admin = Admin(Adminname=Adminname, password_hash=hash_password(password), role=role)
        db.session.add(Admin)
        db.session.commit()
        flash('Admin created successfully!', 'success')
        return redirect(url_for('admin_manage_Admins'))

    return render_template('create_Admin.html')  # Create a new template

@routes.route('/Admins/<int:Admin_id>/edit', methods=['GET', 'POST'])
def edit_Admin(Admin_id):
    Admin = Admin.query.get(Admin_id)
    if not Admin:
        flash('Admin not found.', 'danger')
        return redirect(url_for('admin_manage_Admins'))

    if request.method == 'POST':
        Adminname = request.form.get('Adminname')
        role = request.form.get('role')
        
        Admin.Adminname = Adminname if Adminname else Admin.Adminname
        Admin.role = role if role else Admin.role
        db.session.commit()
        flash('Admin updated successfully!', 'success')
        return redirect(url_for('admin_manage_Admins'))
    
    return render_template('edit_Admin.html', Admin=Admin)

#--------------------- Login endpoint
# Enhanced Login Route with Error Logging
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for('routes.login'))

        user = User.query.filter_by(email=email).first()

        if user and verify_password(password, user.password_hash):
            # Successful login – store user info in session
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(url_for('routes.home'))

        flash("Invalid email or password.", "danger")
        return redirect(url_for('routes.login'))

    return render_template('user/user_login.html')

#--------------------- Admin endpoints
@routes.route('/Admins', methods=['GET'])
def get_Admins():
    Admins = db.session.query(Admin).all()
    Admin_list = [
        {
            "id": Admin.id,
            "Adminname": Admin.Adminname,
            "role": Admin.role,
        }
        for Admin in Admins
    ]
    return jsonify(Admin_list), 200


# Get a single Admin by ID (Admin only)
@routes.route('/Admins/<int:Admin_id>', methods=['GET'])
def get_Admin(Admin_id):
    Admin = db.session.query(Admin).get(Admin_id)
    if not Admin:
        return jsonify({"message": "Admin not found"}), 404
    return jsonify({
        "id": Admin.id,
        "Adminname": Admin.Adminname,
        "role": Admin.role
    }), 200

# Update a Admin (Admin only)
@routes.route('/Admins/<int:Admin_id>', methods=['PUT'])
def update_Admin(Admin_id):
    data = request.get_json()
    Admin = db.session.query(Admin).get(Admin_id)
    if not Admin:
        return jsonify({"message": "Admin not found"}), 404

    # Update fields if provided
    Admin.role = data.get('role', Admin.role)
    db.session.commit()
    return jsonify({"message": "Admin updated successfully"}), 200

# Delete a Admin (Admin only)
@routes.route('/Admins/<int:Admin_id>', methods=['POST'])
def delete_Admin(Admin_id):
    if request.form.get('_method') == 'DELETE':
        Admin = db.session.query(Admin).get(Admin_id)
        if not Admin:
            return jsonify({"message": "Admin not found"}), 404
        db.session.delete(Admin)
        db.session.commit()
        flash('Admin deleted successfully', 'success')
        return redirect(url_for('admin_manage_Admins'))
    return jsonify({"message": "Invalid request"}), 400

# Search Admins (Admin only)
@routes.route('/Admins/search', methods=['GET'])
def search_Admins():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"message": "Search query is required"}), 400

    Admins = db.session.query(Admin).filter(Admin.Adminname.ilike(f'%{query}%')).all()
    Admin_list = [
        {
            "id": Admin.id,
            "Adminname": Admin.Adminname,
            "role": Admin.role
        }
        for Admin in Admins
    ]
    return jsonify(Admin_list), 200

#--------------------- Service endpoints
@routes.route('/services', methods=['POST'])
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
@routes.route('/services', methods=['GET'])
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
@routes.route('/services/<int:service_id>', methods=['GET'])
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
@routes.route('/services/<int:service_id>', methods=['PUT'])
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
@routes.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    service = db.session.query(Service).filter_by(id=service_id).first()
    if not service:
        return jsonify({"message": "Service not found"}), 404
    db.session.delete(service)
    db.session.commit()
    return jsonify({"message": "Service deleted successfully"}), 200

#--------------------- Category endpoints
@routes.route('/categories', methods=['POST'])
 # Only Admins 
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
@routes.route('/categories', methods=['GET'])
def list_categories():
    categories = db.session.query(Category).all()
    category_list = [{"id": category.id, "name": category.name} for category in categories]
    return jsonify(category_list), 200

# Delete a category (Admin only)
@routes.route('/categories/<int:category_id>', methods=['DELETE'])
 # Only Admins 
def delete_category(category_id):
    category = db.session.query(Category).get(category_id)
    if not category:
        return jsonify({"message": "Category not found"}), 404
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted successfully"}), 200

#--------------------- Payment endpoint
@routes.route('/payment', methods=['POST'])
def process_payment():
    try:
        # Get payment details from the request body
        data = request.json
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        token = data.get('token')
        Admin_id = data.get('Admin_id')
        service_id = data.get('service_id')

        if not amount or not token or not Admin_id or not service_id:
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
            Admin_id=Admin_id,
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
        routes.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the payment'}), 500

#--------------------- Review endpoints
@routes.route('/reviews', methods=['GET'])
 # Only admins 
def get_reviews():
    reviews = db.session.query(Review).all()
    review_list = [
        {
            "id": review.id,
            "Admin_id": review.Admin_id,
            "service_id": review.service_id,
            "content": review.content,
            "status": review.status
        }
        for review in reviews
    ]
    return jsonify(review_list), 200

# Get a single review by ID (Admin only)
@routes.route('/reviews/<int:review_id>', methods=['GET'])
 # Only admins 
def get_review(review_id):
    review = db.session.query(Review).get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404
    return jsonify({
        "id": review.id,
        "Admin_id": review.Admin_id,
        "service_id": review.service_id,
        "content": review.content,
        "status": review.status
    }), 200

# Create a new review
@routes.route('/reviews', methods=['POST'])
def create_review():
    data = request.get_json()
    Admin_id = data.get('Admin_id')
    service_id = data.get('service_id')
    content = data.get('content')

    if not Admin_id or not service_id or not content:
        return jsonify({"message": "Admin ID, Service ID, and Content are required"}), 400

    new_review = Review(
        Admin_id=Admin_id,
        service_id=service_id,
        content=content,
        status='pending'  # Default status is "pending"
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({"message": "Review created successfully", "review_id": new_review.id}), 201

# Approve a review (Admin only)
@routes.route('/reviews/<int:review_id>/approve', methods=['POST'])
 # Only admins 
def approve_review(review_id):
    review = db.session.query(Review).get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404
    review.status = 'approved'
    db.session.commit()
    return jsonify({"message": "Review approved successfully"}), 200

# Reject a review (Admin only)
@routes.route('/reviews/<int:review_id>/reject', methods=['POST'])
 # Only admins 
def reject_review(review_id):
    review = db.session.query(Review).get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404
    review.status = 'rejected'
    db.session.commit()
    return jsonify({"message": "Review rejected successfully"}), 200

# Delete a review (Admin only)
@routes.route('/reviews/<int:review_id>', methods=['DELETE'])
 # Only admins 
def delete_review(review_id):
    review = db.session.query(Review).get(review_id)
    if not review:
        return jsonify({"message": "Review not found"}), 404
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted successfully"}), 200

#------------------ Admin endpoints

@routes.route('/admin/dashboard', methods=['GET'])
 # Only Admins and Super Admins 
def admin_dashboard():
    return render_template('admin_dashboard.html', logout_url=url_for('admin_logout'))


# Task 1: Show HTML Admin Login Page (GET request)
@routes.route('/admin/login', methods=['GET'])
def admin_login_page():
    return render_template('admin/admin_login.html')

# Task 2: Handle Admin Login (POST request)
@routes.route('/admin/login', methods=['POST'])
def admin_login():
    Adminname = request.form.get('Adminname')
    password = request.form.get('password')

    Admin = Admin.query.filter(Admin.Adminname == Adminname, Admin.role.in_(['Admin', 'Super Admin'])).first()
    
    if not Admin or not verify_password(password, Admin.password_hash):
        logger.warning(f"Failed admin login attempt for Adminname: {Adminname}")
        flash('Invalid credentials', 'danger')
        return redirect(url_for('admin_login_page'))
    
    logger.info(f"Successful admin login for Adminname: {Adminname}")
    token = create_jwt_token(Admin)
    response = make_response(redirect(url_for('admin_dashboard')))
    response.set_cookie('admin_token', token, httponly=True, secure=True, samesite='Strict')
    session['Admin_role'] = Admin.role
    session['Admin_id'] = Admin.id
    flash('Welcome to Admin Panel!', 'success')
    return response


# --------admin logout    
# ✅ Admin Logout Route (Updated)
@routes.route('/admin/logout', methods=['GET', 'POST'])
def admin_logout():
    if request.method == 'POST' or request.method == 'GET':
        response = make_response(redirect(url_for('admin_login_page')))
        response.delete_cookie('admin_token')  # Clear token
        session.clear()  # Clear session
        flash('Logged out successfully', 'success')
        return response
    
    return jsonify({'message': 'Method Not Allowed'}), 405

# ✅ Add Routes for Admin Panel Buttons
@routes.route('/admin/Admins', methods=['GET'])
def admin_manage_Admins():
    Admins = Admin.query.all()
    return render_template('admin_Admins.html', Admins=Admins)

@routes.route('/admin/services', methods=['GET'])
def admin_manage_services():
    services = Service.query.all()
    return render_template('admin_services.html', services=services)

@routes.route('/admin/reviews', methods=['GET'])
def admin_manage_reviews():
    reviews = Review.query.all()
    return render_template('admin_reviews.html', reviews=reviews)


#----------Broadcast Notification
@routes.route('/admin/broadcast', methods=['POST'])
def broadcast_notification():
    title = request.form.get('title')
    body = request.form.get('body')
    broadcast_to_topic(title, body)
    flash('Announcement sent to all Admins!', 'success')
    return redirect(url_for('admin_dashboard'))

@routes.errorhandler(Exception)
def handle_api_error(error):
    logger.error(f"API error: {error}")
    if request.path.startswith('/api') or request.is_json:
        response = jsonify({"message": "An internal error occurred."})
        response.status_code = 500
        return response
    else:
        return render_template("error.html", error=error), 500

logger.info("Logging configuration complete.")

if __name__ == '__main__':
    routes.run(debug=True)
