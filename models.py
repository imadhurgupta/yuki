from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# --- USER MODEL ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationship: One user has many orders
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- PRODUCT MODEL ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(100), nullable=True)
    
    # FIX: Added 'sizes' so create_db.py doesn't crash
    sizes = db.Column(db.String(50), nullable=True)
    
    orders = db.relationship('Order', backref='product', lazy=True)

# --- ORDER MODEL ---
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # FIX: Explicit foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    address = db.Column(db.Text, nullable=False)
    full_name = db.Column(db.Text, nullable=False)
    mobile_number = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(10), nullable=True)
    customization_file = db.Column(db.String(100), nullable=True)
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Pending")