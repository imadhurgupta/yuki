import os
import uuid
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
# Added ProductImage to imports
from models import db, User, Order, Product, Carousel, ProductImage 

# =========================================================
# HELPER: Delete File from Disk
# =========================================================
def delete_file(filename):
    """Safely removes a file from the uploads folder."""
    if filename and filename != 'default.jpg':
        try:
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(path):
                os.remove(path)
                print(f">> Deleted old file: {filename}")
        except Exception as e:
            print(f">> Error deleting file: {e}")

# =========================================================
# ADMIN DASHBOARD
# =========================================================
@login_required
def dashboard():
    """Displays the main admin dashboard with stats and tables."""
    if not current_user.is_admin:
        flash("Access Denied. Admin only.", "danger")
        return redirect(url_for('user_bp.home'))
        
    total_orders = Order.query.count()
    total_products = Product.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    
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

# =========================================================
# CAROUSEL MANAGEMENT
# =========================================================
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
            flash('Banner added successfully.', 'success')
        else:
            flash('Image is required for banners.', 'warning')
            
    return redirect(url_for('admin_bp.dashboard'))

@login_required
def delete_banner(banner_id):
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    
    banner = Carousel.query.get_or_404(banner_id)
    delete_file(banner.image_file)
    
    db.session.delete(banner)
    db.session.commit()
    flash('Banner deleted.', 'info')
    return redirect(url_for('admin_bp.dashboard'))

# =========================================================
# PRODUCT MANAGEMENT (Inventory)
# =========================================================
@login_required
def add_product():
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    
    if request.method == 'POST':
        try:
            # 1. Get Basic Data
            name = request.form.get('name')
            base_price = float(request.form.get('price'))
            shipping_charge = float(request.form.get('shipping_charge') or 0)
            section = request.form.get('section')
            category = request.form.get('category')
            sizes = request.form.get('sizes')
            
            # 2. Handle Main Thumbnail
            file = request.files.get('image')
            filename = 'default.jpg'
            
            if file and file.filename != '':
                fname = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{fname}"
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                file.save(path)
                filename = unique_name

            stock = int(request.form.get('stock', 10))    
            
            # 3. Create Product & Commit (Need ID for gallery)
            new_product = Product(
                name=name, base_price=base_price, shipping_charge=shipping_charge,
                section=section, category=category, stock=stock, sizes=sizes, image_file=filename
            )
            db.session.add(new_product)
            db.session.commit() 

            # 4. Handle Multiple Gallery Images
            gallery_files = request.files.getlist('gallery_images')
            for g_file in gallery_files:
                if g_file and g_file.filename != '':
                    g_fname = secure_filename(g_file.filename)
                    g_unique = f"{uuid.uuid4().hex}_{g_fname}"
                    g_path = os.path.join(current_app.config['UPLOAD_FOLDER'], g_unique)
                    g_file.save(g_path)
                    
                    # Create ProductImage record
                    new_img = ProductImage(image_file=g_unique, product_id=new_product.id)
                    db.session.add(new_img)
            
            db.session.commit()
            flash('Product added with images!', 'success')
            
        except ValueError:
            flash('Invalid Price or Shipping value.', 'danger')
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'danger')
        
    return redirect(url_for('admin_bp.dashboard'))

@login_required
def delete_product(product_id):
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    
    product = Product.query.get_or_404(product_id)
    
    # 1. Delete Main Image
    delete_file(product.image_file)

    # 2. Delete All Gallery Images from Disk
    for img in product.images:
        delete_file(img.image_file)
    
    # 3. Delete Database Record (Cascade handles ProductImage rows)
    db.session.delete(product)
    db.session.commit()
    flash('Product and all images deleted.', 'info')
    return redirect(url_for('admin_bp.dashboard'))

@login_required
def edit_product(product_id):
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            # 1. Update Basic Info
            product.name = request.form.get('name')
            product.base_price = float(request.form.get('price'))
            product.shipping_charge = float(request.form.get('shipping_charge') or 0)
            product.section = request.form.get('section')
            product.category = request.form.get('category')
            product.sizes = request.form.get('sizes')
            product.stock = int(request.form.get('stock'))
            
            # 2. Handle Main Image Replacement
            file = request.files.get('image')
            if file and file.filename != '':
                delete_file(product.image_file) # Remove old
                fname = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{fname}"
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                file.save(path)
                product.image_file = unique_name

            # 3. Add NEW Gallery Images (Appends to existing)
            gallery_files = request.files.getlist('gallery_images')
            for g_file in gallery_files:
                if g_file and g_file.filename != '':
                    g_fname = secure_filename(g_file.filename)
                    g_unique = f"{uuid.uuid4().hex}_{g_fname}"
                    g_path = os.path.join(current_app.config['UPLOAD_FOLDER'], g_unique)
                    g_file.save(g_path)
                    
                    new_img = ProductImage(image_file=g_unique, product_id=product.id)
                    db.session.add(new_img)
                
            db.session.commit()
            flash('Product updated successfully!', 'success')
            
        except ValueError:
            flash('Invalid Price entered.', 'danger')
            
    return redirect(url_for('admin_bp.dashboard'))

# =========================================================
# NEW: DELETE SINGLE GALLERY IMAGE
# =========================================================
@login_required
def delete_product_image(image_id):
    """Deletes a specific image from a product gallery."""
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    
    img = ProductImage.query.get_or_404(image_id)
    
    # Remove file from disk
    delete_file(img.image_file)
    
    # Remove from DB
    db.session.delete(img)
    db.session.commit()
    
    flash('Gallery image removed.', 'info')
    return redirect(url_for('admin_bp.dashboard'))

# =========================================================
# ORDER MANAGEMENT
# =========================================================
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

@login_required
def view_order(order_id):
    if not current_user.is_admin: 
        return redirect(url_for('user_bp.home'))
        
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)