import os 
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from PyStation import app, db, bcrypt, mail
from PyStation.forms import (RegistrationForm, LoginForm, UpdatePasswordForm, 
                             UpdateProfileForm, PostForm, RequestResetForm, ResetPasswordForm)
from PyStation.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from werkzeug.utils import secure_filename

@app.route("/")
@app.route("/home")
def home():
    # display the 9 most recent posts
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.signout.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Incorrect email or password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account/<username>", methods=['GET', 'POST'])
@login_required
def account(username):
    form = UpdateProfileForm()
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('account.html', user=user, form=form)

def save_picture(form_picture):
    '''Save the profile picutre to a given path with unique filename
    
    Parameters: 
    -----------
    form_picture: FileStorage

    Secrets module used to generate random sequence of chars for new filename pre-extension.

    Image is then resized to fit into tiny circle

    Returns: 
    --------
    picture_fn: str
    '''
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account/<username>/upload-image", methods=['GET', 'POST'])
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

@app.route("/account/<username>/changepassword")
@login_required
def account_password(username):
    form = UpdatePasswordForm()
    return render_template('account_password.html', form=form)

@app.route("/posts", methods=['GET', 'POST'])
def posts():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('posts.html', posts=posts)

@app.route("/user/<string:username>/posts")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('user_posts.html', posts=posts, user=user)

@app.route("/post/<int:post_id>")
def post_by_post_id(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', username=current_user.username, form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/account/new-post", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post has been successfully created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form, legend='New Post')

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                  sender='noreply@shreddit.com', 
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit: {url_for('reset_token', token=token, _external=True)} 

If you did not make this request, kindly disregard this email.

Thank you,

-Tyler
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent to your account to reset your password", 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title="Reset your password", form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated! You may now log in", 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title="Reset your password", form=form)