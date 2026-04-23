import os
from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager
from models import db, User, mail
from extensions import oauth
from werkzeug.middleware.proxy_fix import ProxyFix # Required for Gunicorn/Docker

# Import Blueprints
from routes.user_routes import user_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp

# Load Env Vars
load_dotenv()
client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
print(f">> STARTUP: Client ID: {client_id[:15]}...")

app = Flask(__name__)

# --- 1. CONFIGURATION ---
# Security
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_this_in_production_key')
app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL')

# Database Config
basedir = os.path.abspath(os.path.dirname(__file__))
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///' + os.path.join(basedir, 'yuki.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_ADDRESS')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_ADDRESS')

# File Upload Config
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/images')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip'}
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 # 20 MB limit
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except OSError:
    pass # Vercel is read-only, safely ignore if folder creation fails

# --- 2. INITIALIZE EXTENSIONS ---
db.init_app(app)
mail.init_app(app)
oauth.init_app(app)

# Define Google OAuth
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

login_manager = LoginManager(app)
login_manager.login_view = 'auth_bp.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- 3. REGISTER BLUEPRINTS ---
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

# --- 4. ERROR HANDLERS ---
@app.errorhandler(413)
def request_entity_too_large(error):
    from flask import render_template
    # If the user uploads a file > 20MB, return a clean error page or message.
    return "File uploaded is too large. The maximum allowed size is 20 MB. Please go back and try a smaller file.", 413

# --- 4. GUNICORN SETUP (Important) ---
# Tell Flask it is behind a proxy (Docker). This fixes URL generation.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# --- 5. LOCAL DEVELOPMENT ENTRY POINT ---
# This block is ignored by Gunicorn. It only runs if you type `python app.py`
if __name__ == '__main__':
    # Fix for OAuth over HTTP on localhost
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    print(f">> Starting in Development Mode using: {app.config['SQLALCHEMY_DATABASE_URI']}")
    with app.app_context():
        try:
            db.create_all()
            print(">> Local DB tables checked.")
        except Exception as e:
            print(f">> Warning: DB connection failed: {e}")
            
    app.run(debug=True, host="0.0.0.0", port=5000)