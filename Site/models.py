from flask import Blueprint

from .extensions import db, UserMixin

models = Blueprint('models', __name__)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(5), nullable=False)  # Role of the user, limits the access to certain pages
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    orders = db.relationship('Order', backref='order')

    def __repr__(self):
        return f'{self.name} {self.surname}'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    img = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return self.title
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    street = db.Column(db.String(200), nullable=False)
    address_number = db.Column(db.String(10), nullable=False)
    district = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(10)) # ordered, paid, sent
    itens = db.relationship('ItemOrder', backref='itens')


class ItemOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

    def __repr__(self):
        return f'{Product.query.filter_by(self.product).first().title} : {self.quantity}'