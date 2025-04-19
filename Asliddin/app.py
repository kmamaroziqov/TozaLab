from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from forms import LoginForm, SignupForm, ServiceForm, TodoForm
import os
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'log_in'

# Import models after db initialization to avoid circular imports
from models import User, Company, Service, Bookings, Comments, TODOO

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('log_in'))

@app.route('/SignUp/', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Check if username exists
        if User.query.filter_by(username=form.company.data).first():
            flash('Username already exists', 'error')
            return redirect(url_for('signup'))
        
        # Create user
        user = User(
            username=form.company.data,
            password=generate_password_hash(form.pwd.data)
        )
        db.session.add(user)
        db.session.commit()
        
        # Create company
        company = Company(
            phone=form.phone.data,
            location=form.loc.data,
            user_id=user.id
        )
        db.session.add(company)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('home'))
    
    return render_template('signup.html', form=form)

@app.route('/LogIn/', methods=['GET', 'POST'])
def log_in():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.fnm.data).first()
        if user and check_password_hash(user.password, form.pwd.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@app.route('/signout/')
@login_required
def signout():
    logout_user()
    return redirect(url_for('log_in'))

@app.route('/home/')
@login_required
def home():
    company = Company.query.filter_by(user_id=current_user.id).order_by(Company.date.desc()).first()
    services = Service.query.filter_by(company_id=company.id).all() if company else []
    
    # Calculate average rating
    if services:
        mean_rating = sum(service.rating for service in services if service.rating) / len(services)
        company.rating = mean_rating
        db.session.commit()
    
    return render_template('home.html', company=company, services=services)

@app.route('/todopage/', methods=['GET', 'POST'])
@login_required
def todo():
    form = TodoForm()
    if form.validate_on_submit():
        todo = TODOO(
            title=form.title.data,
            user_id=current_user.id
        )
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('todo'))
    
    todos = TODOO.query.filter_by(user_id=current_user.id).order_by(TODOO.date.desc()).all()
    return render_template('todo.html', form=form, res=todos)

@app.route('/edit_todo/<int:srno>', methods=['GET', 'POST'])
@login_required
def edit_todo(srno):
    todo = TODOO.query.get_or_404(srno)
    if todo.user_id != current_user.id:
        abort(403)
    
    form = TodoForm(obj=todo)
    if form.validate_on_submit():
        todo.title = form.title.data
        db.session.commit()
        return redirect(url_for('todo'))
    
    return render_template('edit_todo.html', form=form, obj=todo)

@app.route('/delete_todo/<int:srno>')
@login_required
def delete_todo(srno):
    todo = TODOO.query.get_or_404(srno)
    if todo.user_id != current_user.id:
        abort(403)
    
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('todo'))

@app.route('/bookings/')
@login_required
def bookings():
    company = Company.query.filter_by(user_id=current_user.id).order_by(Company.date.desc()).first()
    if not company:
        return redirect(url_for('home'))
    
    services = Service.query.filter_by(company_id=company.id).all()
    service_ids = [service.id for service in services]
    
    bookings_query = Bookings.query.filter(Bookings.service_id.in_(service_ids))
    
    # Search functionality
    search_query = request.args.get('search', '')
    if search_query:
        bookings_query = bookings_query.filter(
            Bookings.time.like(f'%{search_query}%') |
            Bookings.location.like(f'%{search_query}%') |
            Bookings.booker.like(f'%{search_query}%')
        )
    
    # Sorting
    sort_by = request.args.get('sort_by', 'time')
    if sort_by == 'service':
        bookings_query = bookings_query.join(Service).order_by(Service.name)
    elif sort_by == 'location':
        bookings_query = bookings_query.order_by(Bookings.location)
    elif sort_by == 'booker':
        bookings_query = bookings_query.order_by(Bookings.booker)
    else:
        bookings_query = bookings_query.order_by(Bookings.time)
    
    bookings = bookings_query.all()
    return render_template('bookings.html', bookings=bookings)

@app.route('/add_service/', methods=['GET', 'POST'])
@login_required
def add_service():
    form = ServiceForm()
    if form.validate_on_submit():
        company = Company.query.filter_by(user_id=current_user.id).first()
        if not company:
            flash('You need to create a company first', 'error')
            return redirect(url_for('home'))
        
        service = Service(
            name=form.name.data,
            description=form.desc.data,
            company_id=company.id
        )
        
        # Handle file upload
        if form.logo.data:
            filename = secure_filename(form.logo.data.filename)
            form.logo.data.save(os.path.join(app.config['UPLOAD_FOLDER'], 'logos', filename))
            service.logo = filename
        
        db.session.add(service)
        db.session.commit()
        
        return redirect(url_for('home'))
    
    return render_template('add_service.html', form=form)

@app.route('/comments/')
@login_required
def comments():
    company = Company.query.filter_by(user_id=current_user.id).order_by(Company.date.desc()).first()
    if not company:
        return redirect(url_for('home'))
    
    comments = Comments.query.filter_by(company_id=company.id).all()
    return render_template('comments.html', comments=comments)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)