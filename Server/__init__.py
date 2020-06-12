from flask import Flask

from .extensions import db, migrate

#Blueprints Imports
from .models import models
from .views import views
from .auth import auth

#remove
from .models import Agenda


def create_app(config_file='config.py'):
    app = Flask(__name__)

    app.config.from_pyfile(config_file)

    db.init_app(app)
    migrate.init_app(app, db)

    #Blueprints Registration
    app.register_blueprint(models)
    app.register_blueprint(views)    
    app.register_blueprint(auth)

    # with app.app_context():
        # db.create_all()

        # clientName='Irvig Moreira Krehan'
        # clientPhone = '85996858000'
        # serviceType = 'troca-de-oleo'
        # serviceDate = '2020-04-27'
        # a = Agenda(clientName=clientName, clientPhone=clientPhone, serviceDate=serviceDate, serviceType=serviceType)
        # db.session.add(a)
        # db.session.commit()

        # print('Exec complete')


    return app