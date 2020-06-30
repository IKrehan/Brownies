from flask import Flask

from .extensions import db, login_manager, generate_password_hash
from .models import Product, User


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
        # db.create_all()
        # print('Comandos Executados')

    # with app.app_context():
        # a = Product(title='Brownie Padrão', img='img/browniePadrão.jpg', desc='Um brownie', price=7)
        # b = Product(title='Brownie 40g', img='img/brownie40g.jpg', desc='teste', price=4.5)
        # c = Product(title='Brownie na Latinha', img='img/brownieLatinha.jpg', desc='Um latinha com mini-brownies', price=28)
        # d = Product(title='Brownie na forminha de brigadeiro', img='img/brownieBrigadeiro.jpg', desc='Brownies em formato de brigadeiro', price=2.5)
        # db.session.add(a)
        # db.session.add(b)
        # db.session.add(c)
        # db.session.add(d)
        # db.session.commit()
        # print('Comandos Executados')

    # with app.app_context():
        # new_user = User(role='admin', name='adm', surname='in', email='adm@ph.com', phone='992467222', password=generate_password_hash('123', method='sha256'))
        # db.session.add(new_user)
        # db.session.commit()
        # print('Comandos Executados')

    return app