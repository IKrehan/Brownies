from flask import Flask

from .extensions import db, login_manager
from .models import Product


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


    # with app.app_context():
    #     db.create_all()

    #     a = Product(title='petit gateu', img='img/petitGateu.png', desc='teste', price=12)
    #     db.session.add(a)
    #     db.session.commit()
    #     print('Comandos Executados')

    return app