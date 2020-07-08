from flask import Blueprint
from pagseguro import PagSeguro

from .extensions import render_template, url_for, redirect, request, flash, generate_password_hash, check_password_hash, login_user, logout_user, login_required, current_user
from .models import db, User, Order, Product

auth = Blueprint('auth', __name__)

@auth.route('/registrar')
def signup():
    return render_template('Register.html')


@auth.route('/registrar', methods=['POST'])
def signup_post():

    name = request.form.get('name')
    surname = request.form.get('surname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')

    remove_chars = ['(', ')', '-', ' ']

    for char in remove_chars:
        phone = phone.replace(char, '')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user:    # if a user is found the page reload
        flash('Este email já está sendo usado')
        return redirect(url_for('auth.signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(name=name, surname=surname, email=email, phone=phone, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Email ou senha incorretos. Tente Novamente')
            return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page

        login_user(user, remember=remember)
    return redirect(url_for('views.homepage'))
    


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.homepage'))


@auth.route('/pagamento/validacao/<int:order_id>')
@login_required
def paymentValidation(order_id):

    config = {
    'sandbox': True,
    'USE_SHIPPING': False
    }

    pg = PagSeguro(email="seuemail@dominio.com", token="ABCDEFGHIJKLMNO", config=config)

    pg.sender = {
    "name": current_user.name + current_user.surname,
    "area_code": current_user.phone[:2],
    "phone": current_user.phone[2:],
    "email": current_user.email,
    }

    pg.reference = order_id

    pg.extra_amount = 0

    order = Order.query.filter_by(id=order_id).first()
    itens = order.itens

    for item in itens:
        product = Product.query.filter_by(id=item.id)
        
        pg.items.append(
            {"id": product.id, "description": product.desc, "amount": product.price, "quantity": item.quantity, "weight": None},
            )
    
    pg.redirect_url = url_for('views.thanks')


    return