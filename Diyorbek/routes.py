from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Service, Booking, Review, Notification
from app.forms import SearchForm, BookingForm, ReviewForm, ContactForm

# Create a Blueprint for routes
main = Blueprint('main', __name__)

# Home Route
@main.route('/')
def home():
    return render_template('home.html')

# Service Search Route
@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    services = Service.query.filter(Service.name.contains(query)).all()
    return render_template('search.html', services=services)

# Service Detail Route
@main.route('/service/<int:service_id>', methods=['GET'])
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)
    reviews = Review.query.filter_by(service_id=service_id).all()
    return render_template('service_detail.html', service=service, reviews=reviews)

# Booking Route
@main.route('/booking/<int:service_id>', methods=['GET', 'POST'])
@login_required
def booking(service_id):
    service = Service.query.get_or_404(service_id)
    form = BookingForm()
    if form.validate_on_submit():
        # Save booking to the database
        booking = Booking(
            user_id=current_user.id,
            service_id=service.id,
            date=form.date.data,
            time=form.time.data,
            recurrence=form.recurring.data
        )
        db.session.add(booking)
        db.session.commit()
        flash('Booking confirmed!', 'success')
        return redirect(url_for('main.checkout', booking_id=booking.id))
    return render_template('booking.html', service=service, form=form)

# Checkout Route
@main.route('/checkout/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def checkout(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    service = booking.service
    if request.method == 'POST':
        # Mock payment processing
        booking.status = 'paid'
        db.session.commit()
        flash('Payment successful!', 'success')
        return redirect(url_for('main.orders'))
    return render_template('checkout.html', service=service, booking=booking)

# Order History Route
@main.route('/orders', methods=['GET'])
@login_required
def orders():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('orders.html', bookings=bookings)

# Leave Review Route
@main.route('/review/<int:service_id>', methods=['GET', 'POST'])
@login_required
def leave_review(service_id):
    service = Service.query.get_or_404(service_id)
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            user_id=current_user.id,
            service_id=service.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Review submitted!', 'success')
        return redirect(url_for('main.service_detail', service_id=service.id))
    return render_template('reviews.html', service=service, form=form)

# Notifications Route
@main.route('/notifications', methods=['GET'])
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).all()
    return render_template('notifications.html', notifications=notifications)

# Customer Support Route
@main.route('/support', methods=['GET', 'POST'])
def support():
    form = ContactForm()
    if form.validate_on_submit():
        # Save support ticket to the database
        ticket = SupportTicket(message=form.message.data, user_id=current_user.id if current_user.is_authenticated else None)
        db.session.add(ticket)
        db.session.commit()
        flash('Your message has been sent!', 'success')
        return redirect(url_for('main.support'))
    return render_template('support.html', form=form)