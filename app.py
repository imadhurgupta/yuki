import os
from flask import Flask
from flask_login import LoginManager
from models import db, User
from flask_mail import Mail, Message

# Import Blueprints from the routes folder
from routes.user_routes import user_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)

# --- Configuration ---
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this for production!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atipriya.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_ADDRESS')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_ADDRESS')

# File Upload Config
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Initialize Extensions ---
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth_bp.login'  # Redirects here if user isn't logged in
login_manager.login_message_category = 'info'

# Initialize Mail
mail = Mail(app)

# --- User Loader (Required for Flask-Login) ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Register Blueprints ---
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

# --- Main Entry Point ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)