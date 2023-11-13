from flask import (render_template, url_for, flash, current_app,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from PyStation import db
from PyStation.models import Post
from PyStation.posts.forms import PostForm
from PyStation.posts.utils import save_picture
import os

posts = Blueprint('posts', __name__)

@posts.route("/posts", methods=['GET', 'POST'])
def get_posts():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('posts.html', posts=posts)

@posts.route("/post/<int:post_id>")
def post_by_post_id(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        if form.cover_photo.data:
            cover_photo = save_picture(form.cover_photo.data)
            post.thumbnail = cover_photo
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.get_posts', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.cover_photo.data = post.thumbnail
    return render_template('update_post.html', username=current_user.username, post=post, form=form, legend='Update Post')

@posts.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

@posts.route("/account/new-post", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit() and request.method == 'POST':
        post = Post(
                title=form.title.data,
                content=form.content.data, 
                author=current_user
        )
        if form.cover_photo.data:
            cover_photo = save_picture(form.cover_photo.data)
            post.thumbnail = cover_photo
        db.session.add(post)
        db.session.commit()
        flash('Post has been successfully created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', form=form, legend='New Post')