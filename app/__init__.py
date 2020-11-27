from config import Config
from flask import Flask  # Import the Flask class
from flask_caching import Cache
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)  # Create an instance of the class for our use
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = "login"
cache = Cache(app)
