from flask import Blueprint
from controllers import user_controller

user_bp = Blueprint('user_bp', __name__)

# Map URLs to Controller Functions
user_bp.add_url_rule('/', view_func=user_controller.home)
user_bp.add_url_rule('/product/<int:product_id>', view_func=user_controller.product_detail)
user_bp.add_url_rule('/checkout/<int:product_id>', view_func=user_controller.checkout, methods=['GET', 'POST'])
user_bp.add_url_rule('/profile', view_func=user_controller.profile)
user_bp.add_url_rule('/order/<int:order_id>', view_func=user_controller.order_detail)   