from flask import Blueprint

from pagseguro import PagSeguro

from .extensions import render_template, url_for, redirect, request, flash, login_required, current_user, session
from .models import db, Product, User, Order, ItemOrder, PagSeguroResponse

import os

views = Blueprint('views', __name__)

@views.route('/')
def homepage():
    products = Product.query.all()

    return render_template('index.html', products=products)

# ------------------------------------------------------------------------------------------------

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

# ------------------------------------------------------------------------------------------------

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

        session['subtotal'] = subtotal

        return render_template('payment.html', orders=orders, prices=prices, 
        subtotal=subtotal, street=street, number=number, district=district, city=city, cep=cep)
        

# Nesta função estão ocorrendo 2 processos simultâneos,
# um relativo ao banco de dados do servidor e outro relativo ao pagamento pelo pagseguro.
# Tudo decorrente da instância pg é relativo ao  pagseguro
@views.route('/pagamento', methods=['POST'])
def payment_post():
    if request.method == 'POST':

        config = {
        'sandbox': True,
        'CURRENCY': 'BRL',
        'USE_SHIPPING': 'false',
        }

        pg = PagSeguro(email="irvigkrehan@hotmail.com", token="6B1E3EF957F84EF4913EFDA3B76D6D84", config=config)

        pg.sender = {
        "name": current_user.name + ' ' + current_user.surname,
        "area_code": current_user.phone[:2],
        "phone": current_user.phone[2:],
        "email": current_user.email,
        }

        orders = session['orders']
        street = session['street']
        number = session['number']
        district = session['district']
        city = session['city']
        cep = session['cep']


        pg.shipping = {
        "type": pg.SEDEX,
        "street": street,
        "number": number,
        "complement": "",
        "district": district,
        "postal_code": cep,
        "city": city,
        "state": "CE",
        "country": "BRA"
    }

        new_order = Order(client_id=current_user.id, street=street, address_number=number, 
        district=district, city=city, cep=cep, price=session['subtotal'])
        db.session.add(new_order)
        db.session.flush()

        pg.reference = new_order.id
        pg.extra_amount = 0

        itens = []
        i = 1
        # É possivel adicionar um record ao db usando uma lista ao invés de instanciar um objeto como feito anteriormente
        for product, quantity in orders.items():  # cria uma lista de dicionários, dicionários esses que representam um objeto da tabela
            item = {}

            new_quantity = request.form.get('quantity_payment'+str(i))
            if quantity != new_quantity:        
                item['quantity'] = new_quantity
            
            else:
                item['quantity'] = quantity

            item['product_id'] = Product.query.filter_by(title=product).first().id 
            item['order_id'] = new_order.id

            i+=1
            itens.append(item)
            
        for item in itens:                      #Passa pela lista de dicionarios e adiciona cada um ao banco de dados
            new_order_item = ItemOrder(**item)
            db.session.add(new_order_item)

            product = Product.query.filter_by(id=item['product_id']).first()
            pg.items.append(
            {"id": product.id, "description": product.desc, "amount": "{:.2f}".format(product.price), "quantity": item['quantity'], "weight": None},
            )
        pg.notification_url = request.url_root + "/notificacao"
        pg.redirect_url = request.url_root + "/obrigado"
        response = pg.checkout()
        new_response = PagSeguroResponse(code=response.code, date=response.date, payment_url=response.payment_url, errors=response.errors, order_id=new_order.id)
        db.session.add(new_response)

        db.session.commit()
    
        return redirect(response.payment_url)
    
@views.route('/pagamento/removeritem/<string:product>')
@login_required
def payment_remove_session(product):

    orders = session['orders']
    orders.pop(product)
    session['orders'] = orders

    return redirect(url_for('views.payment'))


@views.route('/obrigado')
def thanks():
    return 'Obrigado pela compra'

@views.route('/notificacao', methods=['POST'])
def notification_view(request):
    notification_code = request.data['notificationCode']
    pg = PagSeguro(email="irvigkrehan@hotmail.com", token="6B1E3EF957F84EF4913EFDA3B76D6D84")
    notification_data = pg.check_notification(notification_code)

    order = Order.query.filter_by(id=notification_data['reference'][3:]).first()

    if notification_data['status'] == 1:
        order.status = 'aguardado-pagamento'
    
    elif notification_data['status'] == 2:
        order.status = 'cancelado'

    elif notification_data['status'] == 3:
        order.status = 'pago'

    db.session.commit()

    return ''

# ------------------------------------------------------------------------------------------------

@views.route('/admin')
@login_required
def admin():
    if current_user.role == 'admin':
        orders = Order.query.all()
        ordered = Order.query.filter_by(status="aguardando-pagamento").all()
        paid = Order.query.filter_by(status="pago").all()
        sent = Order.query.filter_by(status="enviado").all()
        done = Order.query.filter_by(status="finalizado").all()

        products = Product.query.all()
        users = User.query.all()

        return render_template('admin/index.html', orders=orders, products=products, users=users, ordered=ordered, paid=paid, sent=sent, done=done)

    else:
        return redirect(url_for('views.homepage'))


@views.route('/admin/pedidos/<string:status>')
@login_required
def admin_orders_waiting_payment(status):
    if current_user.role == 'admin':
        orders = Order.query.filter_by(status=status).all()
        users = User.query.all()
        
        return render_template('admin/orders.html', orders=orders, users=users, status=status)

    else:
        return redirect(url_for('views.homepage'))

# ------------------------------------------------------------------------------------------------

@views.route('/admin/pedidos')
@login_required
def admin_orders():
    if current_user.role == 'admin':
        orders = Order.query.all()
        users = User.query.all()
        
        return render_template('admin/orders.html', orders=orders, users=users)

    else:
        return redirect(url_for('views.homepage'))


@views.route('/admin/pedidos/<int:id>')
@login_required
def admin_order_detail(id):
    if current_user.role == 'admin':
        order = Order.query.filter_by(id=id).first()
        itens = ItemOrder.query.filter_by(order_id=id).all()
        users = User.query.all()
        products = Product.query.all()
        
        return render_template('admin/order_details.html', order=order, itens=itens, products=products, users=users)

    else:
        return redirect(url_for('views.homepage'))


@views.route('/admin/pedidos/<int:id>/delete')
@login_required
def admin_order_delete(id):
    if current_user.role == 'admin':
        order = Order.query.filter_by(id=id).first()
        db.session.delete(order)
        db.session.commit()
        
        return redirect(url_for('views.admin_orders'))

    else:
        return redirect(url_for('views.homepage'))


@views.route('/admin/pedidos/<int:id>/changestatus')
@login_required
def admin_order_change_status(id):
    if current_user.role == 'admin':
        order = Order.query.filter_by(id=id).first()

        if order.status == 'aguardando-pagamento':
            order.status = 'pago'
        
        elif order.status == 'pago':
            order.status = 'enviado'

        elif order.status == 'enviado':
            order.status = 'finalizado'

        elif order.status == 'finalizado':
            order.status = 'aguardando-pagamento'

        db.session.commit()
        
        return redirect(url_for('views.admin_orders'))

    else:
        return redirect(url_for('views.homepage'))

# ------------------------------------------------------------------------------------------------

@views.route('/admin/produtos')
@login_required
def admin_products():
    if current_user.role == 'admin':
        products = Product.query.all()

        return render_template('admin/products.html', products=products)

    else:
        return redirect(url_for('views.homepage'))


@views.route('/admin/produtos/<int:id>')
@login_required
def admin_product_detail(id):
    if current_user.role == 'admin':
        product = Product.query.filter_by(id=id).first()
        
        return render_template('admin/product_details.html', product=product)

    else:
        return redirect(url_for('views.homepage'))


@views.route('/admin/produtos/<int:id>/editar', methods=['POST', 'GET'])
@login_required
def admin_product_edit(id):
    if current_user.role == 'admin':
        product = Product.query.filter_by(id=id).first()

        if request.method == "POST":
            title = request.form.get('title')
            price = request.form.get('price')
            desc = request.form.get('desc')

            img_file = request.files['image']

            path = os.path.abspath(os.path.dirname(__file__)) + '\\static\\img'
            img_url = 'img/' +  img_file.filename

            if product.title != title:
                product.title = title
            
            if product.price != price:
                product.price = price

            if product.desc != desc:
                product.desc = desc

            if product.img != img_url:
                img_file.save(os.path.join(path, img_file.filename))
                product.img = img_url
            
            db.session.commit()
            return redirect(url_for('views.admin_product_detail', id=product.id))
            
        return render_template('admin/product_edit.html', product=product)

    else:
        return redirect(url_for('views.homepage'))


@views.route('/admin/produtos/<int:id>/delete')
@login_required
def admin_product_delete(id):
    if current_user.role == 'admin':
        product = Product.query.filter_by(id=id).first()
        db.session.delete(product)
        db.session.commit()
        
        return redirect(url_for('views.admin_products'))

    else:
        return redirect(url_for('views.homepage'))


@views.route('/admin/produtos/add')
@login_required
def product_add():
    if current_user.role == 'admin':
        
        return render_template('admin/product_add.html')

    else:
        return redirect(url_for('views.homepage'))



@views.route('/admin/produtos/add', methods=['POST'])
def product_add_post():
    if request.method == 'POST':
        

        title = request.form.get('product_name')
        desc = request.form.get('product_desc')
        price = request.form.get('product_price')

        img_file = request.files['product_image']

        path = os.path.abspath(os.path.dirname(__file__)) + '\\static\\img'
        img_file.save(os.path.join(path, img_file.filename))
        img_url = 'img/' +  img_file.filename

        product_validation = Product.query.filter_by(title=title).first()
        
        if product_validation:
            flash('Um produto com este nome já existe.')
            return redirect(url_for('views.product_add'))


        new_product = Product(title=title, img=img_url, desc=desc, price=price)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('views.admin_products'))


    
# ------------------------------------------------------------------------------------------------

@views.route('/admin/usuarios')
@login_required
def admin_users():
    if current_user.role == 'admin':
        users = User.query.all()

        return render_template('admin/users.html', users=users)

    else:
        return redirect(url_for('views.homepage'))


@views.route('/admin/usuarios/<int:id>')
@login_required
def admin_user_detail(id):
    if current_user.role == 'admin':
        user = User.query.filter_by(id=id).first()
        
        return render_template('admin/user_details.html', user=user)

    else:
        return redirect(url_for('views.homepage'))


@views.route('/admin/usuarios/<int:id>/delete')
@login_required
def admin_user_delete(id):
    if current_user.role == 'admin':
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        
        return redirect(url_for('views.admin_users'))

    else:
        return redirect(url_for('views.homepage'))


@views.route('/admin/usuarios/<int:id>/editar', methods=['POST', 'GET'])
@login_required
def admin_usuario_edit(id):
    if current_user.role == 'admin':
        user = User.query.filter_by(id=id).first()

        if request.method == "POST":
            name = request.form.get('name')
            surname = request.form.get('surname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            role = request.form.get('role')

            if user.name != name:
                user.name = name
            
            if user.surname != surname:
                user.surname = surname

            if user.email != email:
                user.email = email
        
            if user.phone != phone:
                user.phone = phone

            if user.role != role:
                user.role = role
            
            db.session.commit()

            return redirect(url_for('views.admin_user_detail', id=user.id))
            
        return render_template('admin/user_edit.html', user=user)

    else:
        return redirect(url_for('views.homepage'))

# ------------------------------------------------------------------------------------------------
