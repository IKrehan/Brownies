import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "GFBFhsBkZYv8jG9tNrFH6ywVjUHb8w5wsDg2czNWg676aMbNwuK8apSZmSDK6nXUr96NHKbwFnZyhaA3et8jyMy9qNAbrQb83jEQ4sk4R6ZWjXfM8Kv9Y3ce6QPGwyCgrHbctwZhLyavz8AjRdvWdrhCEhch9kCh2ZLPKDMgcnFhjgyT54BXtR7cSCWprzMrgDWeep47sMapYJ86XERjAUfWwvKYtEHYnRtxn5frPmeXgHptyzd5d3nAJjjDYxpU"

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'database.db')

SQLALCHEMY_TRACK_MODIFICATIONS = False