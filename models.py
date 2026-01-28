from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# --- CAROUSEL MODEL (New for Homepage) ---
class Carousel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(200))
    image_file = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(200)) # Optional link button

# --- USER MODEL ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) # Increased length for safety
    is_admin = db.Column(db.Boolean, default=False)
    
    # Backref for easy access to user's orders
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- PRODUCT MODEL (Updated for Hierarchy) ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    shipping_charge = db.Column(db.Float, default=0.0)
    
    # Hierarchy: Section (Parent) -> Category (Subcategory)
    section = db.Column(db.String(50), nullable=False) # e.g. "Men", "Women"
    category = db.Column(db.String(50), nullable=False) # e.g. "T-Shirts", "Hoodies"
    
    sizes = db.Column(db.String(100), nullable=True)
    materials = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(100), nullable=True, default='default.jpg')

    orders = db.relationship('Order', backref='product', lazy=True)

# --- ORDER MODEL (Updated for Bulk Orders) ---
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # IMPORTANT: unique=False because multiple items can share one Transaction ID
    transaction_id = db.Column(db.String(20), unique=False, nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Customer Details
    full_name = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    
    # Address Details
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    
    # Order Specifics
    payment_method = db.Column(db.String(20), default="Online")
    instructions = db.Column(db.Text, nullable=True)
    size = db.Column(db.String(10), nullable=True)
    customization_file = db.Column(db.String(100), nullable=True)
    
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Pending")