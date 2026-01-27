import os
import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Product, Order

# --- HOME PAGE ---
def home():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category')
    
    query = Product.query
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    products = query.paginate(page=page, per_page=6)
    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]

    return render_template('guest/index.html', 
                           products=products, 
                           categories=categories, 
                           current_category=category_filter)

# --- PRODUCT DETAIL PAGE ---
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('guest/product_detail.html', product=product)

# --- CHECKOUT PAGE (Login Required) ---
@login_required
def checkout(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        # 1. Capture Delivery Details
        full_name = request.form.get('full_name')
        mobile = request.form.get('mobile_number')
        raw_address = request.form.get('address')
        
        # 2. Capture Personalization Details
        custom_text = request.form.get('custom_text') or "None"
        color = request.form.get('color') or "Standard"
        instructions = request.form.get('instructions') or "None"
        
        # 3. Capture Order Specs
        quantity = int(request.form.get('quantity'))
        size = request.form.get('size')
        
        # 4. Handle File Upload
        file = request.files.get('custom_file')
        filename = None
        if file and file.filename != '':
            original_filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{original_filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            file.save(file_path)
            filename = unique_name
        
        # 5. SMART STACKING: Combine all text details into one block
        # This saves Name, Mobile, Address, Text, Color, and Notes into the 'address' column
        final_details_block = (
            f"CUSTOMER DETAILS\n"
            f"Name: {full_name}\n"
            f"Mobile: {mobile}\n"
            f"Address: {raw_address}\n\n"
            f"PERSONALIZATION\n"
            f"Text on Product: {custom_text}\n"
            f"Color: {color}\n"
            f"Instructions: {instructions}"
        )

        total_price = product.base_price * quantity

        new_order = Order(
            transaction_id=str(uuid.uuid4().hex[:8]).upper(),
            user_id=current_user.id,
            product_id=product.id,
            quantity=quantity,
            total_price=total_price,
            full_name=full_name,
            mobile_number=mobile,
            address=raw_address, # <--- Saving the giant block here
            size=size,
            customization_file=filename,
            date_ordered=datetime.utcnow(),
            status="Pending"
        )

        db.session.add(new_order)
        db.session.commit()

        flash('Order placed successfully!', 'success')
        return redirect(url_for('user_bp.profile'))

    return render_template('user/checkout.html', product=product)

# --- NEW: USER PROFILE PAGE ---
@login_required
def profile():
    # Fetch orders for the current user, newest first
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date_ordered.desc()).all()
    return render_template('user/profile.html', orders=orders)

# --- NEW: ORDER DETAIL / RECEIPT PAGE ---
@login_required
def order_detail(order_id):
    # Fetch order by ID
    order = Order.query.get_or_404(order_id)
    
    # Security Check: Ensure the current user owns this order
    if order.user_id != current_user.id:
        abort(403) # Forbidden access
        
    return render_template('user/order_detail.html', order=order)