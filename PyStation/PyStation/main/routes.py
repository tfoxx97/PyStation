from flask import render_template, Blueprint
from PyStation.models import Post

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    # display the 9 most recent posts
    return render_template('home.html')