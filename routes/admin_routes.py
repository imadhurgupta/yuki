from flask import Blueprint, redirect, url_for, flash
from flask_login import current_user
from controllers import admin_controller

# Create Blueprint
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# --- SECURITY: Protect all Admin Routes ---
@admin_bp.before_request
def restrict_access():
    # It is safer to check 'is_authenticated' first
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Access Denied. Admins only.', 'danger')
        return redirect(url_for('user_bp.home'))

# --- ROUTES MAP ---

# Dashboard (Default is GET, which is correct)
admin_bp.add_url_rule('/dashboard', view_func=admin_controller.dashboard)

# FIX: Add 'GET' so you can VIEW the form, not just submit it
admin_bp.add_url_rule('/add-product', view_func=admin_controller.add_product, methods=['GET', 'POST'])

# FIX: Add 'GET' here too for editing
admin_bp.add_url_rule('/product/edit/<int:product_id>', view_func=admin_controller.edit_product, methods=['GET', 'POST'])

# Delete and Update actions are typically POST-only (Security best practice)
admin_bp.add_url_rule('/product/delete/<int:product_id>', view_func=admin_controller.delete_product, methods=['POST'])
admin_bp.add_url_rule('/order/<int:order_id>/update', view_func=admin_controller.update_order, methods=['POST'])