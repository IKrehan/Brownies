from flask import Blueprint

from .extensions import render_template, url_for, redirect, request, flash, login_required, current_user
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

@views.route('/encomenda', methods=['POST'])
def order_post():
    products = Product.query.all()


    street = request.form.get('street')
    number = request.form.get('number')
    district = request.form.get('district')
    city = request.form.get('city')
    cep = request.form.get('cep')
    
    i = 1
    product = []
    quantity = []
    for x in products:
        if request.form.get(f'brownie-type{i}') and request.form.get(f'quantity{i}'):
            product.append(request.form.get(f'brownie-type{i}'))
            quantity.append(request.form.get(f'quantity{i}'))
        
        i += 1

    if product == '':
        flash('Você precisa escolher algum brownie.')
        return redirect(url_for('views.order'))

    elif quantity == '':
        flash('Você precisa escolher a quantidade de brownies.')
        return redirect(url_for('views.order'))

    else:
        return redirect(url_for('views.pagamento'))

