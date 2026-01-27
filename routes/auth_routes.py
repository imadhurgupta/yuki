from flask import Blueprint
from controllers import auth_controller

auth_bp = Blueprint('auth_bp', __name__)

# Map URLs to Controller Functions
auth_bp.add_url_rule('/register', view_func=auth_controller.register, methods=['GET', 'POST'])
auth_bp.add_url_rule('/login', view_func=auth_controller.login, methods=['GET', 'POST'])
auth_bp.add_url_rule('/logout', view_func=auth_controller.logout)
auth_bp.add_url_rule('/verify-otp/<action>', view_func=auth_controller.verify_otp, methods=['GET', 'POST'])