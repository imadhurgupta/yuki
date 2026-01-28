from flask import Blueprint
from controllers import user_controller

user_bp = Blueprint('user_bp', __name__)

# Map URLs to Controller Functions
user_bp.add_url_rule('/', view_func=user_controller.home)
user_bp.add_url_rule('/product/<int:product_id>', view_func=user_controller.product_detail)
user_bp.add_url_rule('/checkout/<int:product_id>', view_func=user_controller.checkout, methods=['GET', 'POST'])
user_bp.add_url_rule('/profile', view_func=user_controller.profile)
user_bp.add_url_rule('/order/<int:order_id>', view_func=user_controller.order_detail)   
# Payment Routes
user_bp.add_url_rule('/payment/<int:order_id>', view_func=user_controller.payment_page)
user_bp.add_url_rule('/process-payment/<int:order_id>', view_func=user_controller.process_payment, methods=['POST'])
user_bp.add_url_rule('/invoice/<int:order_id>', view_func=user_controller.generate_invoice)

# Add these lines to your route definitions
user_bp.add_url_rule('/cart', view_func=user_controller.cart, methods=['GET'])
user_bp.add_url_rule('/cart/add/<int:product_id>', view_func=user_controller.add_to_cart, methods=['POST'])
user_bp.add_url_rule('/cart/remove/<int:index>', view_func=user_controller.remove_from_cart, methods=['GET'])
user_bp.add_url_rule('/cart/checkout', view_func=user_controller.checkout_cart, methods=['GET', 'POST'])

user_bp.add_url_rule('/about', view_func=user_controller.about, methods=['GET'])
user_bp.add_url_rule('/contact', view_func=user_controller.contact, methods=['GET', 'POST'])
user_bp.add_url_rule('/shop', view_func=user_controller.shop, methods=['GET'])