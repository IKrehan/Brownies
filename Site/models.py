from flask import Blueprint

from .extensions import db, UserMixin

models = Blueprint('models', __name__)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Enum("user", "admin"), nullable=False, default='user')  # Role of the user, limits the access to certain pages
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
    client_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    street = db.Column(db.String(200), nullable=False)
    address_number = db.Column(db.String(10), nullable=False)
    district = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    complement = db.Column(db.String(300), nullable=False)
    status = db.Column(db.Enum("aguardando-pagamento", "pago", "enviado", "finalizado", name="status de pedido"), default='aguardando-pagamento')
    itens = db.relationship('ItemOrder', backref='itens')
    price = db.Column(db.Float, nullable=False)


class ItemOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'))
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'))

    def __repr__(self):
        return f'{self.quantity}x{Product.query.filter_by(id=self.product_id).first().title}'


class PagSeguroResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    payment_url = db.Column(db.String(500), nullable=False)
    errors = db.Column(db.String(500), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'))
    