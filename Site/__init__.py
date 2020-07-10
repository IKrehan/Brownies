from flask import Flask

from .extensions import db, login_manager, generate_password_hash
from .models import Product, User, Order


def create_app(config_file='config.py'):
    app = Flask(__name__)

    app.config.from_pyfile(config_file)

    db.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)


    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    from .models import models
    app.register_blueprint(models)

    from .views import views
    app.register_blueprint(views)   

    from .auth import auth
    app.register_blueprint(auth)

    return app