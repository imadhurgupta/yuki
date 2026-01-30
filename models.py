from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()
mail = Mail()

# =========================================================
# 1. USER MODEL (Admin & Customers)
# =========================================================
class User(UserMixin, db.Model):
    """Stores user login details and admin status."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        """Hashes password for security."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if entered password matches hash."""
        return check_password_hash(self.password_hash, password)

# =========================================================
# 2. PRODUCT MODEL (Main Item Info)
# =========================================================
class Product(db.Model):
    """Stores the main details of a product."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    shipping_charge = db.Column(db.Float, default=0.0)
    
    # Categorization
    section = db.Column(db.String(50), nullable=False)  # Main Type: T-Shirts, Hoodies, Mugs
    category = db.Column(db.String(50), nullable=False) # Subtype: Oversized, Ceramic, etc.
    
    # Inventory details
    sizes = db.Column(db.String(100), default="S, M, L, XL") # Comma-separated string
    image_file = db.Column(db.String(120), nullable=False, default='default.jpg') # Main Thumbnail
    
    # RELATIONSHIP: One Product can have Many Gallery Images
    # cascade="all, delete-orphan" ensures images are deleted if the product is deleted.
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade="all, delete-orphan")
    
    # Stock
    stock = db.Column(db.Integer, default=10)

# =========================================================
# 3. PRODUCT IMAGE MODEL (Gallery / Extra Photos)
# =========================================================
class ProductImage(db.Model):
    """Stores additional images for a specific product."""
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(120), nullable=False)
    
    # Link to the main Product
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# =========================================================
# 4. ORDER MODEL (Transactions)
# =========================================================
class Order(db.Model):
    """Stores customer order details."""
    id = db.Column(db.Integer, primary_key=True)
    
    # CRITICAL FIX: Removed 'unique=True' so multiple items can share one Transaction ID
    transaction_id = db.Column(db.String(50), nullable=False) 
    
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Customer Details
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    # Order Specifics
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # nullable=True allows the order to exist even if the product is deleted
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True) 
    
    # Relationship to access product details (e.g., order.product.name)
    product = db.relationship('Product', backref='orders')
    
    size = db.Column(db.String(10))
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    
    # Status & Payment
    status = db.Column(db.String(50), default='Pending') # Pending, Shipped, Delivered
    payment_method = db.Column(db.String(50), default='COD')
    instructions = db.Column(db.Text, nullable=True) # Optional user note
    customization_file = db.Column(db.String(120), nullable=True)

# =========================================================
# 5. CAROUSEL MODEL (Home Page Banners)
# =========================================================
class Carousel(db.Model):
    """Stores slides for the homepage banner."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100), nullable=True)
    image_file = db.Column(db.String(120), nullable=False)
    link = db.Column(db.String(200), default="#")

# =========================================================
# 6. CART MODEL (User's Shopping Cart)
# =========================================================
class Cart(db.Model):
    """Stores items in the user's shopping cart."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    size = db.Column(db.String(10), default='Std')
    
    # Relationships
    product = db.relationship('Product')
    user = db.relationship('User', backref='cart_items')