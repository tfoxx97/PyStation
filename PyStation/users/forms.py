import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from PyStation.models import User

# add additional validators to password to check that password contains letters[aAzZ], numbers[0-9+], and special characters[!@#$%^&*]
def char_limit(form, password):
    message = 'Password must be at least 8 characters long.'
    pattern = r"[a-zA-Z0-9]"
    if len(re.findall(pattern, password.data)) < 8:
        raise ValidationError(message)
    
def find_special_char(form, password):
    message = 'Password must contain at least one special character: !, @, #, $, %, &, or +'
    pattern = r"[!@#$%&+]"
    if len(re.findall(pattern, password.data)) == 0:
        raise ValidationError(message)

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), char_limit, find_special_char])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please try another one.')
        
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email is already taken. Please try another one.')

class LoginForm(FlaskForm):
    # in future build, first variable can be email or username
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    signout = BooleanField('Keep Me Logged In')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=8, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class UpdatePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), char_limit, find_special_char])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    submit = SubmitField('Update')
    
class UpdateProfileForm(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[FileRequired('Missing something? -----^'), FileAllowed(['jpg', 'png', 'jpeg'])]) # gifs don't actually work; not animated yet
    submit = SubmitField('Upload')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no user with that email. Please try again after registering")
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), char_limit, find_special_char])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    submit = SubmitField('Reset Password')