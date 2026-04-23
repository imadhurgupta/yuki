from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
import re
import random
from flask_mail import Message
from threading import Thread
from sqlalchemy.exc import IntegrityError
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

from extensions import oauth

# =========================================================
# EMAIL HELPER FUNCTIONS
# =========================================================

def send_email_thread(app, msg):
    """Sends email using the app context and existing mail extension."""
    with app.app_context():
        try:
            # Access the mail instance directly from extensions to avoid circular imports
            mail = app.extensions.get('mail')
            if mail:
                mail.send(msg)
                print(f">> Email sent to {msg.recipients}")
            else:
                print(">> Error: Mail extension not found in app.")
        except Exception as e:
            print(f">> Error sending email: {e}")

def send_async_email(subject, recipient, body):
    """Starts a background thread to send an email."""
    try:
        msg = Message(subject, recipients=[recipient])
        msg.body = body
        # Pass the actual app object to the thread context
        app = current_app._get_current_object()
        Thread(target=send_email_thread, args=(app, msg)).start()
    except Exception as e:
        print(f">> Error starting email thread: {e}")

# =========================================================
# UTILITY FUNCTIONS
# =========================================================

def generate_otp():
    """Generates a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def get_serializer():
    """Returns a serializer for secure token generation."""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

# =========================================================
# AUTH ROUTES
# =========================================================

def register():
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')

        # 1. Email Format Check
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('auth_bp.register'))

        # 2. Check if Email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('auth_bp.login'))

        # 3. Generate OTP & Save Temp Data
        otp = generate_otp()
        
        session['temp_user'] = {
            'full_name': full_name, 
            'email': email, 
            'password': password
        }
        session['otp'] = otp
        
        # 4. Send Verification Email
        print(f">> DEBUG: Generated Registration OTP: {otp}") 
        send_async_email("Verify your Registration", email, f"Your Verification OTP is: {otp}")
        
        flash('OTP sent to your email. Please verify.', 'info')
        return redirect(url_for('auth_bp.verify_otp', action='register'))

    return render_template('user/register.html')

def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.home'))

    if request.method == 'POST':
        email_input = request.form.get('email') 
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email_input).first()

        if user and user.check_password(password):
            if user.is_admin:
                # Require OTP for Admin
                otp = generate_otp()
                session['pending_user_id'] = user.id
                session['otp'] = otp
                
                print(f">> DEBUG: Generated Login OTP for Admin: {otp}")
                send_async_email("Admin Login OTP", user.email, f"Your Admin Login OTP is: {otp}")
                
                flash('OTP sent to your email. Please verify to access admin dashboard.', 'info')
                return redirect(url_for('auth_bp.verify_otp', action='login'))
            else:
                # Log regular user in directly
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('user_bp.home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('user/login.html')

def verify_otp(action):
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        system_otp = session.get('otp')
        
        if not system_otp:
            flash('Session expired. Please register/login again.', 'warning')
            return redirect(url_for('auth_bp.login'))

        if user_otp == system_otp:
            # --- ACTION: REGISTER ---
            if action == 'register':
                data = session.get('temp_user')
                
                if not data or 'full_name' not in data:
                    flash('Registration data missing. Please try again.', 'danger')
                    return redirect(url_for('auth_bp.register'))

                try:
                    email = data.get('email')
                    admin_email = current_app.config.get('ADMIN_EMAIL')
                    
                    new_user = User(
                        full_name=data.get('full_name'), 
                        email=email,
                        is_admin=(email == admin_email)
                    )
                    # Using property setter for hashing
                    new_user.password = data.get('password') 
                    
                    db.session.add(new_user)
                    db.session.commit()
                    
                    # Cleanup Session
                    session.pop('temp_user', None)
                    session.pop('otp', None)
                    
                    flash('Account created successfully! Please login.', 'success')
                    return redirect(url_for('auth_bp.login'))
                    
                except IntegrityError:
                    db.session.rollback()
                    flash('Error: Email already exists.', 'danger')
                    return redirect(url_for('auth_bp.register'))
                except Exception as e:
                    db.session.rollback()
                    print(f"Error creating user: {e}")
                    flash('An unknown error occurred.', 'danger')
                    return redirect(url_for('auth_bp.register'))

            # --- ACTION: LOGIN ---
            elif action == 'login':
                user_id = session.get('pending_user_id')
                user = User.query.get(user_id)
                
                if user:
                    login_user(user)
                    # Cleanup Session
                    session.pop('pending_user_id', None)
                    session.pop('otp', None)
                    
                    if user.is_admin:
                        return redirect(url_for('admin_bp.dashboard'))
                    return redirect(url_for('user_bp.home'))
                else:
                    flash('User not found.', 'danger')
                    return redirect(url_for('auth_bp.login'))
        
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            
    return render_template('user/verify_otp.html', action=action)

# =========================================================
# FORGOT PASSWORD LOGIC
# =========================================================

# In controllers/auth_controller.py

# ... (Keep existing imports and functions) ...

# 1. FORGOT PASSWORD (Ask for Email)
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            otp = generate_otp()
            session['reset_email'] = email
            session['reset_otp'] = otp
            
            send_async_email("Password Reset OTP", email, f"Your Password Reset OTP is: {otp}")
            
            flash('OTP sent to your email.', 'info')
            return redirect(url_for('auth_bp.verify_reset_otp'))
        else:
            # Fake success for security
            flash('If that email exists, we have sent an OTP.', 'info')
            return redirect(url_for('auth_bp.verify_reset_otp'))

    # UPDATED PATH: user/forgot_password.html
    return render_template('user/forgot_password.html')

# 2. VERIFY RESET OTP
def verify_reset_otp():
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        system_otp = session.get('reset_otp')
        
        if user_otp == system_otp:
            # Mark session as verified for the next step
            session['reset_verified'] = True
            return redirect(url_for('auth_bp.reset_new_password'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')

    return render_template('user/verify_reset_otp.html')

# 3. SET NEW PASSWORD
def reset_new_password():
    # Security Check: Ensure they passed the OTP step
    if not session.get('reset_verified') or not session.get('reset_email'):
        flash('Unauthorized access. Please restart the process.', 'danger')
        return redirect(url_for('user_bp.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('user_bp.reset_new_password'))
            
        email = session.get('reset_email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # UPDATE PASSWORD
            user.password = password
            db.session.commit()
            
            # CLEAR SESSION
            session.pop('reset_email', None)
            session.pop('reset_otp', None)
            session.pop('reset_verified', None)
            
            flash('Password reset successful! You can now login.', 'success')
            return redirect(url_for('auth_bp.login'))
        else:
            flash('User not found.', 'danger')

    return render_template('user/reset_password.html')

@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('user_bp.home'))

# =========================================================
# GOOGLE OAUTH LOGIC
# =========================================================

def google_login():
    """Redirect to Google for authentication."""
    redirect_uri = url_for('auth_bp.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
    except Exception as e:
        print(f"OAuth Error: {e}")
        flash('Authentication failed or session expired. Please try again.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    if not user_info:
        flash('Failed to fetch user info from Google.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    email = user_info.get('email')
    full_name = user_info.get('name')
    
    user = User.query.filter_by(email=email).first()
    admin_email = current_app.config.get('ADMIN_EMAIL')
    
    if not user:
        # Create a new user if they don't exist
        user = User(
            full_name=full_name,
            email=email,
            is_admin=(email == admin_email)
        )
        db.session.add(user)
        try:
            db.session.commit()
            flash('Account created via Google!', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Database write error: {e}")
            flash('Error: Could not save account because the database is read-only on Vercel. Please configure a PostgreSQL database for production.', 'danger')
            # Fake the user id so they can at least look around
            user.id = random.randint(1000, 9999) 
    else:
        # If user exists, ensure admin status is correct if they are the admin
        if email == admin_email and not user.is_admin:
            user.is_admin = True
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
    
    login_user(user)
    flash(f'Welcome back, {user.full_name}!', 'success')
    
    if user.is_admin:
        return redirect(url_for('admin_bp.dashboard'))
    return redirect(url_for('user_bp.home'))