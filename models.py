from extensions import db, mail
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# =========================================================
# 1. USER MODEL (Admin & Customers)
# =========================================================
class User(UserMixin, db.Model):
    """Stores user login details and admin status."""
    id = db.Column(db.Integer, primary_key=True)
    
    # Authenticate via Email, Display via Full Name
    # Note: full_name is NOT unique (multiple people can have the same name)
    full_name = db.Column(db.String(100), nullable=False) 
    email = db.Column(db.String(150), unique=True, nullable=False) # Unique Login ID
    
    password_hash = db.Column(db.String(200), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    # Optional Profile Fields
    mobile_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)

    # Relationships
    cart_items = db.relationship('Cart', backref='user', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Hashes password automatically when setting user.password"""
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
    section = db.Column(db.String(50), nullable=False)  # Main Type: T-Shirts, Hoodies
    section_icon = db.Column(db.String(50), default='fas fa-box-open') # Icon class for UI
    category = db.Column(db.String(50), nullable=False) # Subtype: Oversized, Ceramic
    
  # Description
    description = db.Column(db.Text, nullable=True)

    # Inventory details
    sizes = db.Column(db.String(100), default="S, M, L, XL") 
    image_file = db.Column(db.String(120), nullable=False, default='default.jpg')
    
    # Relationships
    # cascade="all, delete-orphan" ensures images are deleted if the product is deleted.
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade="all, delete-orphan")
    
    # Stock
    stock = db.Column(db.Integer, default=10)
    
    # Payment Policy
    advance_percentage = db.Column(db.Float, default=40.0)

    # Bulk Discounts
    bulk_min_qty = db.Column(db.Integer, default=0)
    bulk_discount_percentage = db.Column(db.Float, default=0.0)

    def get_price_for_quantity(self, quantity):
        """Returns the unit price after applying any bulk discounts."""
        if self.bulk_min_qty and self.bulk_min_qty > 0 and quantity >= self.bulk_min_qty:
            discount = self.bulk_discount_percentage / 100.0
            return self.base_price * (1 - discount)
        return self.base_price

# =========================================================
# 3. PRODUCT IMAGE MODEL (Gallery / Extra Photos)
# =========================================================
class ProductImage(db.Model):
    """Stores additional images for a specific product."""
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(120), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# =========================================================
# 4. ORDER MODEL (Transactions)
# =========================================================
class Order(db.Model):
    """Stores customer order details."""
    id = db.Column(db.Integer, primary_key=True)
    
    transaction_id = db.Column(db.String(50), nullable=False) 
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Customer Details (Snapshot at time of order)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    # Links
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True) 
    
    # Relationship to Product (Unidirectional)
    product = db.relationship('Product') 
    
    size = db.Column(db.String(10))
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    
    # Status & Payment
    status = db.Column(db.String(50), default='Pending') 
    payment_method = db.Column(db.String(50), default='COD')
    instructions = db.Column(db.Text, nullable=True)
    customization_file = db.Column(db.String(120), nullable=True)

    # Payment Verification
    payment_proof = db.Column(db.String(150), nullable=True)

    # Add discount
    discount_amount = db.Column(db.Float, default=0.0)

    # Advance Payment Fields (Product-Specific)
    advance_amount = db.Column(db.Float, default=0.0)
    amount_paid = db.Column(db.Float, default=0.0)

# =========================================================
# 5. CAROUSEL MODEL (Home Page Banners)
# =========================================================
class Carousel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100), nullable=True)
    image_file = db.Column(db.String(120), nullable=False)
    link = db.Column(db.String(200), default="#")

# =========================================================
# 6. CART MODEL (User's Shopping Cart)
# =========================================================
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    size = db.Column(db.String(10), default='Std')
    
    product = db.relationship('Product')
    # user relationship is defined in User model (backref)

# =========================================================
# 7. SITE SETTING MODEL (QR Code)
# =========================================================
class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qr_code_file = db.Column(db.String(150), nullable=True)
    upi_id = db.Column(db.String(100), default='shop@upi')

# =========================================================
# 8. REVIEW MODEL (Customer Reviews)
# =========================================================
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    media_file = db.Column(db.Text, nullable=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('reviews', cascade='all, delete-orphan', lazy=True))
    user = db.relationship('User')

# =========================================================
# 9. COUPON MODEL
# =========================================================
class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    applicable_category = db.Column(db.String(50), default='All')

# =========================================================
# 10. CATEGORY MODEL
# =========================================================
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    image_file = db.Column(db.String(150), nullable=True)