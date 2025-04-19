from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from models import Review
from extensions import db
from flask_admin import BaseView, expose
from models import User, Service, Transaction

class ReviewView(ModelView):
    column_list = ('id', 'user_id', 'service_id', 'content', 'status')

    @action('approve', 'Approve', 'Are you sure you want to approve selected reviews?')
    def action_approve(self, ids):
        for review_id in ids:
            review = db.session.query(Review).filter_by(id=review_id).first()
            if review:
                review.status = 'approved'
        db.session.commit()
        return self.notify_success(f'{len(ids)} reviews were successfully approved.')

    @action('reject', 'Reject', 'Are you sure you want to reject selected reviews?')
    def action_reject(self, ids):
        for review_id in ids:
            review = db.session.query(Review).filter_by(id=review_id).first()
            if review:
                review.status = 'rejected'
        db.session.commit()
        return self.notify_success(f'{len(ids)} reviews were successfully rejected.')
    
class DashboardView(BaseView):
    @expose('/')
    def index(self):
        # Fetch data from the database
        total_users = db.session.query(User).count()
        active_users = db.session.query(User).filter_by(role='user').count()
        total_services = db.session.query(Service).count()
        total_revenue = sum(t.amount for t in db.session.query(Transaction).filter_by(status='success'))

        # Render the dashboard with metrics
        return self.render('admin/dashboard.html',
                           total_users=total_users,
                           active_users=active_users,
                           total_services=total_services,
                           total_revenue=total_revenue)