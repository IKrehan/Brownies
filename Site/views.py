from flask import Blueprint

from .extensions import render_template, url_for, login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
def homepage():
    return render_template('index.html')

@views.route('/encomenda')
@login_required
def encomenda():
    return 'área logada'