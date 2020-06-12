from flask import Blueprint
from .extensions import db


models = Blueprint('models', __name__)

class Agenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clientName = db.Column(db.String(100))
    clientPhone = db.Column(db.String(11))
    serviceDate = db.Column(db.String(8))
    serviceType = db.Column(db.String(30))