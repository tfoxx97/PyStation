from flask import render_template, request, Blueprint
from PyStation.models import Post

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    # display the 9 most recent posts
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=9)
    return render_template('home.html', posts=posts)