from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from urllib.parse import urlparse
import re
import random
from flask_mail import Message
from threading import Thread

# --- THREADED EMAIL SENDER ---
def send_email_thread(app, msg):
    with app.app_context():
        try:
            from app import mail
            mail.send(msg)
        except Exception as e:
            print(f">> Error sending email: {e}")

def send_async_email(subject, recipient, body):
    try:
        msg = Message(subject, recipients=[recipient])
        msg.body = body
        app = current_app._get_current_object()
        Thread(target=send_email_thread, args=(app, msg)).start()
    except Exception as e:
        print(f"Error preparing email thread: {e}")

# --- HELPER: GENERATE OTP ---
def generate_otp():
    return str(random.randint(100000, 999999))

# --- REGISTER (Step 1) ---
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Checks
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('auth_bp.register'))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('User already exists.', 'danger')
            return redirect(url_for('auth_bp.register'))

        # STOP! Don't save to DB yet.
        # Generate OTP
        otp = generate_otp()
        
        # Save temp data to SESSION
        session['temp_user'] = {'username': username, 'email': email, 'password': password}
        session['otp'] = otp
        
        # Send Email
        send_async_email("Verify your Registration", email, f"Your OTP is: {otp}")
        
        flash('OTP sent to your email. Please verify.', 'info')
        return redirect(url_for('auth_bp.verify_otp', action='register'))

    return render_template('user/register.html')

# --- LOGIN (Step 1) ---
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.home'))

    if request.method == 'POST':
        login_input = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter((User.username == login_input) | (User.email == login_input)).first()

        if user and user.check_password(password):
            # STOP! Don't login yet.
            otp = generate_otp()
            
            # Save User ID to SESSION
            session['pending_user_id'] = user.id
            session['otp'] = otp
            
            # Send Email
            send_async_email("Login Verification Code", user.email, f"Your Login OTP is: {otp}")
            
            flash('Enter the OTP sent to your email.', 'info')
            return redirect(url_for('auth_bp.verify_otp', action='login'))
        else:
            flash('Invalid credentials.', 'danger')

    return render_template('user/login.html')

# --- VERIFY OTP (Step 2) ---
def verify_otp(action):
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        system_otp = session.get('otp')
        
        if user_otp == system_otp:
            # OTP MATCHED!
            
            if action == 'register':
                # Retrieve data from session
                data = session.get('temp_user')
                if data:
                    new_user = User(username=data['username'], email=data['email'])
                    new_user.set_password(data['password'])
                    db.session.add(new_user)
                    db.session.commit()
                    
                    # Cleanup session
                    session.pop('temp_user', None)
                    session.pop('otp', None)
                    
                    flash('Account verified & created! Please login.', 'success')
                    return redirect(url_for('auth_bp.login'))

            elif action == 'login':
                # Retrieve ID from session
                user_id = session.get('pending_user_id')
                user = User.query.get(user_id)
                if user:
                    login_user(user)
                    
                    # Cleanup session
                    session.pop('pending_user_id', None)
                    session.pop('otp', None)
                    
                    return redirect(url_for('user_bp.home'))
        
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            
    return render_template('user/verify_otp.html')

@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('user_bp.home'))