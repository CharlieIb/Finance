from flask import Flask
from config import Config
from jinja2 import StrictUndefined
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from app.utils.helpers import usd


# Configure application
app = Flask(__name__)
# Custom filter
app.jinja_env.filters["usd"] = usd

app.jinja_env.undefined = StrictUndefined
app.config.from_object(Config)

db = SQLAlchemy(app)

login = LoginManager(app)
login.login_view = 'login'

from app import views
from app.utils.debug_utils import reset_db

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, generate_password_hash=generate_password_hash, reset_db=reset_db)



