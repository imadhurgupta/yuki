from flask import Blueprint
from controllers import admin_controller

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# Dashboard
admin_bp.add_url_rule('/dashboard', view_func=admin_controller.dashboard, methods=['GET'])

# Carousel
admin_bp.add_url_rule('/carousel/add', view_func=admin_controller.add_banner, methods=['POST'])
admin_bp.add_url_rule('/carousel/delete/<int:banner_id>', view_func=admin_controller.delete_banner, methods=['GET'])

# Products
admin_bp.add_url_rule('/products/add', view_func=admin_controller.add_product, methods=['POST'])
admin_bp.add_url_rule('/products/delete/<int:product_id>', view_func=admin_controller.delete_product, methods=['GET', 'POST'])

# --- NEW ROUTES TO FIX ERROR ---
admin_bp.add_url_rule('/products/edit/<int:product_id>', view_func=admin_controller.edit_product, methods=['POST'])
admin_bp.add_url_rule('/orders/update/<int:order_id>', view_func=admin_controller.update_order, methods=['POST'])