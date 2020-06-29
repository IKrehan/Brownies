from flask import render_template, url_for, redirect, request, flash, session

from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user


db = SQLAlchemy()
login_manager = LoginManager()