from flask import Blueprint

from .extensions import render_template, url_for, login_required, current_user
from .models import Product

views = Blueprint('views', __name__)

@views.route('/')
def homepage():
    products = Product.query.all()

    return render_template('index.html', products=products)

@views.route('/encomenda')
@login_required
def order():
    products = Product.query.all()
    
    return render_template('order.html', products=products)