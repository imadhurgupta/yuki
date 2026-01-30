from flask import Blueprint
from controllers import user_controller

# Create Blueprint for User/Public routes
user_bp = Blueprint('user_bp', __name__)

# ==========================================
# 1. PUBLIC PAGES (Home, Shop, Static)
# ==========================================
# Home Page
user_bp.add_url_rule('/', view_func=user_controller.home, methods=['GET'])

# Shop Page (Browsing & Filtering)
user_bp.add_url_rule('/shop', view_func=user_controller.shop, methods=['GET'])

# Static Pages
user_bp.add_url_rule('/about', view_func=user_controller.about, methods=['GET'])
user_bp.add_url_rule('/contact', view_func=user_controller.contact, methods=['GET', 'POST'])

# ==========================================
# 2. PRODUCT DETAILS
# ==========================================
# View Single Product
user_bp.add_url_rule('/product/<int:product_id>', view_func=user_controller.product_detail, methods=['GET'])

# ==========================================
# 3. SHOPPING CART SYSTEM
# ==========================================
# View Cart
user_bp.add_url_rule('/cart', view_func=user_controller.cart, methods=['GET'])

# Add Item to Cart
user_bp.add_url_rule('/cart/add/<int:product_id>', view_func=user_controller.add_to_cart, methods=['POST'])

# Remove Item from Cart
user_bp.add_url_rule('/cart/remove/<int:cart_id>', view_func=user_controller.remove_from_cart, methods=['GET'])

# ==========================================
# 4. CHECKOUT & ORDERS
# ==========================================
# Direct Checkout (Buy Now - Single Item)
user_bp.add_url_rule('/checkout/<int:product_id>', view_func=user_controller.checkout, methods=['GET', 'POST'])

# Cart Checkout (Bulk Order - All Items)
user_bp.add_url_rule('/cart/checkout', view_func=user_controller.checkout_cart, methods=['GET', 'POST'])

# Payment Gateway Mockup
user_bp.add_url_rule('/payment/<int:order_id>', view_func=user_controller.payment_page, methods=['GET'])
user_bp.add_url_rule('/process-payment/<int:order_id>', view_func=user_controller.process_payment, methods=['POST'])

# ==========================================
# 5. USER PROFILE & HISTORY
# ==========================================
# User Dashboard / Order History
user_bp.add_url_rule('/profile', view_func=user_controller.profile, methods=['GET'])

# View Specific Order Details (Legacy View)
# IMPORTANT: This must match the function we just added to user_controller.py
user_bp.add_url_rule('/order/<int:order_id>', view_func=user_controller.order_detail, methods=['GET'])

# View Printable Invoice (New Route)
user_bp.add_url_rule('/invoice/<int:order_id>', view_func=user_controller.generate_invoice, methods=['GET'])