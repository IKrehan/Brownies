import os

SECRET_KEY = "c32^B2D>ZZ%9R=$Y<egy2g4r@.EJe(erKVu6DZPJ)52}%{5x5bFgk.-t(66GSKsCkE:j.b3#%$mfBfohgÇ~vBy-pc`%3Rt3(TKh>4T>zqCp?]kCv-ZkS]cbr{`=;VXhK9"

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

UPLOAD_FOLDER = basedir + '/static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}