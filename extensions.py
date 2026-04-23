from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()
oauth = OAuth()
