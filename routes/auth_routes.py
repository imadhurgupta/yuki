from flask import Blueprint
from controllers import auth_controller

auth_bp = Blueprint('auth_bp', __name__)

# Map URLs to Controller Functions
auth_bp.add_url_rule('/register', view_func=auth_controller.register, methods=['GET', 'POST'])
auth_bp.add_url_rule('/login', view_func=auth_controller.login, methods=['GET', 'POST'])
auth_bp.add_url_rule('/logout', view_func=auth_controller.logout)
auth_bp.add_url_rule('/verify-otp/<action>', view_func=auth_controller.verify_otp, methods=['GET', 'POST'])

# Google OAuth Routes
auth_bp.add_url_rule('/login/google/login/', view_func=auth_controller.google_login)
auth_bp.add_url_rule('/login/google/callback/', view_func=auth_controller.google_callback)
# In routes/auth_routes.py

# ... existing routes ...

# Password Reset Flow
# In routes/auth_routes.py
auth_bp.add_url_rule('/forgot-password', view_func=auth_controller.forgot_password, methods=['GET', 'POST'])
auth_bp.add_url_rule('/verify-reset-otp', view_func=auth_controller.verify_reset_otp, methods=['GET', 'POST'])
auth_bp.add_url_rule('/reset-new-password', view_func=auth_controller.reset_new_password, methods=['GET', 'POST'])