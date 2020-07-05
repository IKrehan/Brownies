from flask import Blueprint

from .extensions import render_template, url_for, redirect, request, flash, login_required, current_user, session
from .models import db, Product, User, Order, ItemOrder

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
    if request.method == 'POST':
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
        orders = {}
        prices = {}
        for x in products_query:
            if request.form.get(f'brownie-type{i}') and request.form.get(f'quantity{i}'):
                orders[request.form.get(f'brownie-type{i}')] = request.form.get(f'quantity{i}')
                prices[request.form.get(f'brownie-type{i}')] = x.price
            i += 1

        if not orders:
            flash('Você precisa escolher algum brownie.')
            return redirect(url_for('views.order'))

        else:
            session['orders'] = orders
            session['prices'] = prices

            return redirect(url_for('views.payment'))



@views.route('/pagamento')
@login_required
def payment():
    if 'orders' in session and 'prices' in session and 'street' in session and 'number' in session and 'district' in session and 'city' in session and 'cep' in session:
        orders = session['orders']
        prices = session['prices']
        
        street = session['street']
        number = session['number']
        district = session['district']
        city = session['city']
        cep = session['cep']

        subtotal = 0
        for product, quantity in orders.items():
            subtotal += float(prices[product]) * float(quantity)

        return render_template('payment.html', orders=orders, prices=prices, 
        subtotal=subtotal, street=street, number=number, district=district, city=city, cep=cep)
        


@views.route('/pagamento', methods=['POST'])
def payment_post():
    if request.method == 'POST':

        orders = session['orders']
        street = session['street']
        number = session['number']
        district = session['district']
        city = session['city']
        cep = session['cep']

        new_order = Order(client_id=current_user.id, street=street, address_number=number, 
        district=district, city=city, cep=cep, status='ordered')
        db.session.add(new_order)
        db.session.flush()

        itens= []
        # É possivel adicionar um record ao db usando uma lista ao invés de instanciar um objeto como feito anteriormente
        for product, quantity in orders.items():  # cria uma lista de dicionários, dicionários esses que representam um objeto da tabela
            item = {}

            item['product_id'] = Product.query.filter_by(title=product).first().id 
            item['quantity'] = quantity
            item['order_id'] = new_order.id

            itens.append(item)
                
        for item in itens:                      #Passa pela lista de dicionarios e adiciona cada um ao banco de dados
            new_order_item = ItemOrder(**item)
            db.session.add(new_order_item)

        db.session.commit()
        print('adicionado')


        return redirect(url_for('views.homepage'))
    

@views.route('/admin')
@login_required
def admin():
    if current_user.role == 'admin':
        orders = Order.query.all()
        ordered = Order.query.filter_by(status="ordered")
        paid = Order.query.filter_by(status="paid")
        sent = Order.query.filter_by(status="sent")

        products = Product.query.all()
        users = User.query.all()

        return render_template('admin/index.html', orders=orders, products=products, users=users, ordered=ordered, paid=paid, sent=sent)

    else:
        return redirect(url_for('views.homepage'))

@views.route('/admin/pedidos')
@login_required
def admin_orders():
    if current_user.role == 'admin':
        orders = Order.query.all()
        itens = ItemOrder.query.all()
        users = User.query.all()
        products = Product.query.all()
        
        return render_template('admin/orders.html', orders=orders, itens=itens, products=products, users=users)

    else:
        return redirect(url_for('views.homepage'))

@views.route('/admin/produtos')
@login_required
def admin_products():
    if current_user.role == 'admin':
        products = Product.query.all()

        return render_template('admin/products.html', products=products)

    else:
        return redirect(url_for('views.homepage'))

@views.route('/admin/usuarios')
@login_required
def admin_users():
    if current_user.role == 'admin':
        users = User.query.all()

        return render_template('admin/users.html', users=users)

    else:
        return redirect(url_for('views.homepage'))

