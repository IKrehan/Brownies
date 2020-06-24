from flask import Blueprint

from .extensions import db, UserMixin

models = Blueprint('models', __name__)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    img = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    
