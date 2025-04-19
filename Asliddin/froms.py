from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    fnm = StringField('Username', validators=[DataRequired()])
    pwd = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    company = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=80)])
    pwd = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    loc = StringField('Location', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Sign Up')
    
    def validate_company(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists')

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired(), Length(max=100)])
    desc = TextAreaField('Description', validators=[DataRequired()])
    logo = FileField('Service Logo')
    submit = SubmitField('Add Service')

class TodoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=25)])
    submit = SubmitField('Add Todo')