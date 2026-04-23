from flask import Blueprint
from controllers import admin_controller

# Create the Blueprint for Admin URLs
# All routes here will start with '/admin' (e.g., /admin/dashboard)
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# ==========================================
# 1. DASHBOARD
# ==========================================
# The main admin homepage containing stats and tables
admin_bp.add_url_rule('/dashboard', view_func=admin_controller.dashboard, methods=['GET'])

# ==========================================
# 2. CAROUSEL (HOME BANNERS)
# ==========================================
# Add a new slide to the homepage carousel
admin_bp.add_url_rule('/carousel/add', view_func=admin_controller.add_banner, methods=['POST'])

# Delete an existing slide
admin_bp.add_url_rule('/carousel/delete/<int:banner_id>', view_func=admin_controller.delete_banner, methods=['GET'])

# Edit an existing slide
admin_bp.add_url_rule('/carousel/edit/<int:banner_id>', view_func=admin_controller.edit_banner, methods=['POST'])

# ==========================================
# 3. PRODUCT INVENTORY
# ==========================================
# Add a new product to the database
admin_bp.add_url_rule('/products/add', view_func=admin_controller.add_product, methods=['POST'])

# Edit an existing product (Update price, name, etc.)
admin_bp.add_url_rule('/products/edit/<int:product_id>', view_func=admin_controller.edit_product, methods=['POST'])

# Delete a product
admin_bp.add_url_rule('/products/delete/<int:product_id>', view_func=admin_controller.delete_product, methods=['GET'])

# ==========================================
# 4. ORDER MANAGEMENT
# ==========================================
# Update status (Pending -> Shipped -> Delivered)
admin_bp.add_url_rule('/orders/update/<int:order_id>', view_func=admin_controller.update_order, methods=['POST'])

# View the printable Receipt/Invoice page
admin_bp.add_url_rule('/orders/<txn_id>', view_func=admin_controller.view_order, methods=['GET'])

# Delete a product image
admin_bp.add_url_rule('/product/image/delete/<int:image_id>', view_func=admin_controller.delete_product_image, methods=['GET'])

# QR Code Management
admin_bp.add_url_rule('/upload_qr', view_func=admin_controller.upload_qr, methods=['POST'])

# Delete QR Code
admin_bp.add_url_rule('/delete_qr', view_func=admin_controller.delete_qr, methods=['GET', 'POST'])

# ==========================================
# 5. COUPONS MANAGEMENT
# ==========================================
admin_bp.add_url_rule('/coupons/add', view_func=admin_controller.add_coupon, methods=['POST'])
admin_bp.add_url_rule('/coupons/toggle/<int:coupon_id>', view_func=admin_controller.toggle_coupon_status, methods=['POST'])
admin_bp.add_url_rule('/coupons/delete/<int:coupon_id>', view_func=admin_controller.delete_coupon, methods=['POST'])

# ==========================================
# 6. CATEGORY MANAGEMENT
# ==========================================
admin_bp.add_url_rule('/categories/add', view_func=admin_controller.add_category, methods=['POST'])
admin_bp.add_url_rule('/categories/delete/<int:category_id>', view_func=admin_controller.delete_category, methods=['POST', 'GET'])

# ==========================================
# 7. REVIEW MANAGEMENT
# ==========================================
admin_bp.add_url_rule('/review/delete/<int:review_id>', view_func=admin_controller.delete_review, methods=['GET', 'POST'])