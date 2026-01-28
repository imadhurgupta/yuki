import os
import uuid
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Order, Product, Carousel

# --- DASHBOARD ---
@login_required
def dashboard():
    if not current_user.is_admin:
        flash("Access Denied.", "danger")
        return redirect(url_for('user_bp.home'))
        
    # Stats
    total_orders = Order.query.count()
    total_products = Product.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    
    # Data
    orders = Order.query.order_by(Order.date_ordered.desc()).all()
    products = Product.query.order_by(Product.id.desc()).all()
    banners = Carousel.query.all()
    
    return render_template('admin/dashboard.html', 
                           total_orders=total_orders, 
                           total_products=total_products,
                           pending_orders=pending_orders,
                           orders=orders,
                           products=products,
                           banners=banners)

# --- CAROUSEL ACTIONS ---
@login_required
def add_banner():
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        link = request.form.get('link')
        file = request.files.get('image')
        
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            file.save(path)
            
            new_banner = Carousel(title=title, subtitle=subtitle, image_file=unique_name, link=link)
            db.session.add(new_banner)
            db.session.commit()
            flash('Banner added.', 'success')
            
    return redirect(url_for('admin_bp.dashboard'))

@login_required
def delete_banner(banner_id):
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    banner = Carousel.query.get_or_404(banner_id)
    db.session.delete(banner)
    db.session.commit()
    flash('Banner deleted.', 'info')
    return redirect(url_for('admin_bp.dashboard'))

# --- PRODUCT ACTIONS ---
@login_required
def add_product():
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        base_price = float(request.form.get('price'))
        shipping_charge = float(request.form.get('shipping_charge') or 0)
        section = request.form.get('section')
        category = request.form.get('category')
        sizes = request.form.get('sizes')
        
        file = request.files.get('image')
        filename = 'default.jpg'
        
        if file and file.filename != '':
            fname = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{fname}"
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            file.save(path)
            filename = unique_name
            
        new_product = Product(
            name=name, base_price=base_price, shipping_charge=shipping_charge,
            section=section, category=category, sizes=sizes, image_file=filename
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added.', 'success')
        
    return redirect(url_for('admin_bp.dashboard'))

@login_required
def delete_product(product_id):
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('admin_bp.dashboard'))

# --- NEW: EDIT PRODUCT (Fixes the BuildError) ---
@login_required
def edit_product(product_id):
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.base_price = float(request.form.get('price'))
        product.shipping_charge = float(request.form.get('shipping_charge') or 0)
        product.section = request.form.get('section')
        product.category = request.form.get('category')
        product.sizes = request.form.get('sizes')
        
        # Handle Image Update
        file = request.files.get('image')
        if file and file.filename != '':
            fname = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{fname}"
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            file.save(path)
            product.image_file = unique_name
            
        db.session.commit()
        flash('Product updated successfully!', 'success')
        
    return redirect(url_for('admin_bp.dashboard'))

# --- NEW: UPDATE ORDER STATUS (Fixes the other dropdown) ---
@login_required
def update_order(order_id):
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    
    order = Order.query.get_or_404(order_id)
    if request.method == 'POST':
        new_status = request.form.get('status')
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.transaction_id} updated to {new_status}.', 'success')
        
    return redirect(url_for('admin_bp.dashboard'))