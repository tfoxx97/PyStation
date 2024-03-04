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

@main.route("/search", methods=["GET", "POST"])
def search():
    q = request.form.get('q')
    print(q)
    if q:
        results = Post.query.filter(Post.content.contains(q) | Post.title.contains(q)).limit(10)
    else:
        results = []
    return render_template("search.html", results=results)
        
        
