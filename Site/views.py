from flask import Blueprint

from .extensions import render_template, url_for, redirect, request, flash, login_required, current_user, session
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
    products_query = Product.query.all()


    street = request.form.get('street')
    number = request.form.get('number')
    district = request.form.get('district')
    city = request.form.get('city')
    cep = request.form.get('cep')

    session['street'] = street
    session['number'] = number
    session['district'] = district
    session['city'] = city
    session['cep'] = cep

    i = 1
    products = []
    quantity = []
    prices = []
    for x in products_query:
        if request.form.get(f'brownie-type{i}') and request.form.get(f'quantity{i}'):
            products.append(request.form.get(f'brownie-type{i}'))
            quantity.append(request.form.get(f'quantity{i}'))
            prices.append(x.price)
        
        i += 1

    if products == '':
        flash('Você precisa escolher algum brownie.')
        return redirect(url_for('views.order'))

    elif quantity == '':
        flash('Você precisa escolher a quantidade de brownies.')
        return redirect(url_for('views.order'))

    else:
        session['products'] = products
        session['quantity'] = quantity
        session['prices'] = prices
        return redirect(url_for('views.payment'))



@views.route('/pagamento')
@login_required
def payment():
    if 'products' in session and 'quantity' in session and 'street' in session and 'number' in session and 'district' in session and 'city' in session and 'cep' in session and 'prices' in session:
        products = session['products']
        quantity = session['quantity']
        prices = session['prices']

        street = session['street']
        number = session['number']
        district = session['district']
        city = session['city']
        cep = session['cep']

        i = 0
        subtotal = 0
        for price in prices:
            subtotal += float(price) * float(quantity[i])
            i += 1

        return render_template('payment.html', products=products, quantity=quantity, prices=prices, 
        subtotal=subtotal, street=street, number=number, district=district, city=city, cep=cep)

    else:
        return redirect(url_for('views.order'))
        



