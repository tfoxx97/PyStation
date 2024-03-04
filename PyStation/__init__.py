from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
from PyStation.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
ckeditor = CKEditor()
login = LoginManager()
login.login_view = 'users.login'
login.login_message_category = 'info'
mail = Mail()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    ckeditor.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    from PyStation.users.routes import users 
    from PyStation.posts.routes import posts 
    from PyStation.main.routes import main
    from PyStation.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
