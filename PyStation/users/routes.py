from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from PyStation import db, bcrypt
from PyStation.models import User, Post
from PyStation.users.forms import (RegistrationForm, LoginForm, RequestResetForm, 
                                   ResetPasswordForm, UpdateProfileForm, UpdatePasswordForm)
from PyStation.users.utils import save_picture, send_reset_email
from werkzeug.utils import secure_filename

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.signout.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Incorrect email or password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/account/<username>", methods=['GET', 'POST'])
@login_required
def account(username):
    form = UpdateProfileForm()
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('account.html', user=user, form=form)

@users.route("/account/<username>/upload-image", methods=['GET', 'POST'])
@login_required
def account_pic(username):
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            filename = secure_filename(picture_file)
            current_user.image_file = filename
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return render_template('account.html')
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account_pic.html', image_file=image_file, form=form)

@users.route("/account/<username>/changepassword", methods=['GET', 'POST'])
@login_required
def account_password(username):
    user = User.query.filter_by(username=username)
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Password changed!", 'success')
        return redirect(url_for('users.account', username=username))
    return render_template('account_password.html', form=form)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent to your account to reset your password", 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title="Reset your password", form=form)

@users.route("/user/<string:username>/posts")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('user_posts.html', posts=posts, user=user)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated! You may now log in", 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title="Reset your password", form=form)