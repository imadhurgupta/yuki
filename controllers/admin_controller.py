import os
import uuid
from flask import render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Order, Product, Carousel, ProductImage, SiteSetting, Coupon, Category, Review

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
    coupons = Coupon.query.order_by(Coupon.id.desc()).all()
    categories = Category.query.all()

    # --- Fetch Settings for the View ---
    site_setting = SiteSetting.query.first()
    
    # Ensure this matches your actual template filename (admin/index.html or admin/dashboard.html)
    return render_template('admin/dashboard.html', 
                           total_orders=total_orders, 
                           total_products=total_products,
                           pending_orders=pending_orders,
                           orders=orders,
                           products=products,
                           banners=banners,
                           coupons=coupons,
                           categories=categories,
                           site_setting=site_setting)

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

@login_required
def edit_banner(banner_id):
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    
    banner = Carousel.query.get_or_404(banner_id)
    
    if request.method == 'POST':
        banner.title = request.form.get('title')
        banner.subtitle = request.form.get('subtitle')
        banner.link = request.form.get('link')
        
        file = request.files.get('image')
        if file and file.filename != '':
            delete_file(banner.image_file)
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            file.save(path)
            banner.image_file = unique_name
            
        db.session.commit()
        flash('Banner updated successfully.', 'success')
        
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
            
            # Default Icon if none provided
            section_icon = request.form.get('section_icon') or 'fas fa-box-open'
            
            category = request.form.get('category')
            sizes = request.form.get('sizes')
            stock = int(request.form.get('stock', 10))
            bulk_min_qty = int(request.form.get('bulk_min_qty') or 0)
            bulk_discount_percentage = float(request.form.get('bulk_discount_percentage') or 0.0)
            advance_percentage = float(request.form.get('advance_percentage') or 40.0)
            
            # --- Get Description ---
            description = request.form.get('description')

            # 2. Handle Main Thumbnail
            file = request.files.get('image')
            filename = 'default.jpg'
            
            if file and file.filename != '':
                fname = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{fname}"
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                file.save(path)
                filename = unique_name
            
            # 3. Create Product & Commit
            # FIX: Added 'description=description' here
            new_product = Product(
                name=name, base_price=base_price, shipping_charge=shipping_charge,
                section=section, section_icon=section_icon,
                category=category, 
                description=description, # <--- THIS WAS MISSING
                stock=stock, sizes=sizes, image_file=filename,
                bulk_min_qty=bulk_min_qty, bulk_discount_percentage=bulk_discount_percentage,
                advance_percentage=advance_percentage
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
                    
                    new_img = ProductImage(image_file=g_unique, product_id=new_product.id)
                    db.session.add(new_img)
            
            db.session.commit()
            flash('Product added with details!', 'success')
            
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
    
    # 3. Delete Database Record
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
            
            product.section_icon = request.form.get('section_icon') or 'fas fa-box-open'
            
            product.category = request.form.get('category')
            product.sizes = request.form.get('sizes')
            product.stock = int(request.form.get('stock'))
            product.bulk_min_qty = int(request.form.get('bulk_min_qty') or 0)
            product.bulk_discount_percentage = float(request.form.get('bulk_discount_percentage') or 0.0)
            product.advance_percentage = float(request.form.get('advance_percentage') or 40.0)
            
            # --- Update Description ---
            product.description = request.form.get('description')

            # 2. Handle Main Image Replacement
            file = request.files.get('image')
            if file and file.filename != '':
                delete_file(product.image_file) # Remove old
                fname = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{fname}"
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                file.save(path)
                product.image_file = unique_name

            # 3. Add NEW Gallery Images
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

@login_required
def delete_product_image(image_id):
    if not current_user.is_admin: return redirect(url_for('user_bp.home'))
    
    img = ProductImage.query.get_or_404(image_id)
    delete_file(img.image_file)
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
        amount_paid = request.form.get('amount_paid')

        # Update all items sharing the same Transaction ID
        related_orders = Order.query.filter_by(transaction_id=order.transaction_id).all()
        
        for o in related_orders:
            o.status = new_status
            if amount_paid:
                # If we are updating amount_paid, we distribute the total paid proportionally 
                # or just set it on the transaction group. 
                # For simplicity, if it's a single item transaction, it's easy.
                # If bulk, we'll just set it on the first item or divide it.
                # Let's divide it proportionally by total_price.
                total_txn_value = sum(item.total_price for item in related_orders)
                if total_txn_value > 0:
                    proportion = o.total_price / total_txn_value
                    o.amount_paid = float(amount_paid) * proportion

        db.session.commit()
        flash(f'Transaction {order.transaction_id} updated to {new_status}.', 'success')
        
    return redirect(url_for('admin_bp.dashboard'))

@login_required
def view_order(txn_id):
    if not current_user.is_admin: 
        return redirect(url_for('user_bp.home'))
        
    # Fetch all items sharing the same Transaction ID
    transaction_items = Order.query.filter_by(transaction_id=txn_id).all()
    if not transaction_items:
        flash("Order not found.", "danger")
        return redirect(url_for('admin_bp.dashboard'))
        
    order = transaction_items[0]
    grand_total = sum(item.total_price for item in transaction_items)
    total_paid = sum(item.amount_paid for item in transaction_items)
    
    return render_template('admin/order_detail.html', 
                           order=order, 
                           items=transaction_items, 
                           grand_total=grand_total,
                           total_paid=total_paid)

# =========================================================
# SETTINGS: QR CODE & UPI ID
# =========================================================
@login_required
def upload_qr():
    if not current_user.is_admin: 
        return redirect(url_for('user_bp.home'))
        
    if request.method == 'POST':
        # Get or Create Settings Row
        setting = SiteSetting.query.first()
        if not setting:
            setting = SiteSetting()
            db.session.add(setting)

        # 1. Update UPI ID (Text)
        upi_id = request.form.get('upi_id')
        if upi_id:
            setting.upi_id = upi_id

        # 2. Update QR Image (File)
        file = request.files.get('qr_image')
        if file and file.filename != '':
            # Delete old QR if it exists
            if setting.qr_code_file:
                delete_file(setting.qr_code_file)

            # Generate Unique Name
            ext = secure_filename(file.filename).rsplit('.', 1)[1]
            filename = f"qr_{uuid.uuid4().hex[:8]}.{ext}" 
            
            # Ensure folder exists
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            path = os.path.join(upload_folder, filename)
            file.save(path)
            setting.qr_code_file = filename
            
        db.session.commit()
        flash('Payment settings updated successfully!', 'success')
            
    return redirect(url_for('admin_bp.dashboard'))

@login_required
def delete_qr():
    if not current_user.is_admin:
        return redirect(url_for('user_bp.home'))
    
    setting = SiteSetting.query.first()
    
    if setting and setting.qr_code_file:
        delete_file(setting.qr_code_file)
        setting.qr_code_file = None
        db.session.commit()
        flash('QR Code removed successfully.', 'info')
    else:
        flash('No QR Code to remove.', 'warning')
        
    return redirect(url_for('admin_bp.dashboard'))

# =========================================================
# COUPONS MANAGEMENT
# =========================================================
@login_required
def add_coupon():
    if not current_user.is_admin:
        return redirect(url_for('user_bp.home'))
        
    if request.method == 'POST':
        code = request.form.get('code')
        discount = float(request.form.get('discount_percentage', 0))
        applicable_category = request.form.get('applicable_category', 'All')
        
        if not code or discount <= 0:
            flash('Invalid coupon code or discount percentage.', 'danger')
            return redirect(url_for('admin_bp.dashboard'))
            
        existing = Coupon.query.filter_by(code=code.upper()).first()
        if existing:
            flash(f'Coupon {code.upper()} already exists.', 'danger')
        else:
            new_coupon = Coupon(
                code=code.upper(), 
                discount_percentage=discount, 
                is_active=True,
                applicable_category=applicable_category
            )
            db.session.add(new_coupon)
            db.session.commit()
            flash(f'Coupon {code.upper()} added successfully.', 'success')
            
    return redirect(url_for('admin_bp.dashboard'))

@login_required
def toggle_coupon_status(coupon_id):
    if not current_user.is_admin:
        return redirect(url_for('user_bp.home'))
        
    coupon = Coupon.query.get_or_404(coupon_id)
    coupon.is_active = not coupon.is_active
    db.session.commit()
    
    status = "activated" if coupon.is_active else "deactivated"
    flash(f"Coupon {coupon.code} has been {status}.", 'success')
    return redirect(url_for('admin_bp.dashboard'))

@login_required
def delete_coupon(coupon_id):
    if not current_user.is_admin:
        return redirect(url_for('user_bp.home'))
        
    coupon = Coupon.query.get_or_404(coupon_id)
    db.session.delete(coupon)
    db.session.commit()
    
    flash('Coupon deleted completely.', 'info')
    return redirect(url_for('admin_bp.dashboard'))

# =========================================================
# CATEGORY MANAGEMENT
# =========================================================
@login_required
def add_category():
    if not current_user.is_admin:
        return redirect(url_for('user_bp.home'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        file = request.files.get('image')
        
        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('admin_bp.dashboard'))
            
        existing = Category.query.filter_by(name=name).first()
        if existing:
            # Update existing
            if file and file.filename != '':
                delete_file(existing.image_file)
                filename = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{filename}"
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                file.save(path)
                existing.image_file = unique_name
                db.session.commit()
                flash('Category icon updated successfully.', 'success')
            else:
                flash('Category already exists. Upload an image to update the icon.', 'warning')
        else:
            # Create new
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{filename}"
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                file.save(path)
                
                new_category = Category(name=name, image_file=unique_name)
                db.session.add(new_category)
                db.session.commit()
                flash('Category created successfully.', 'success')
            else:
                flash('Image is required to create a category icon.', 'warning')
                
    return redirect(url_for('admin_bp.dashboard'))

@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        return redirect(url_for('user_bp.home'))
        
    category = Category.query.get_or_404(category_id)
    delete_file(category.image_file)
    db.session.delete(category)
    db.session.commit()
    
    flash('Category icon deleted.', 'info')
    return redirect(url_for('admin_bp.dashboard'))

# =========================================================
# REVIEW MANAGEMENT
# =========================================================
@login_required
def delete_review(review_id):
    if not current_user.is_admin:
        return redirect(url_for('user_bp.home'))
        
    review = Review.query.get_or_404(review_id)
    product_id = review.product_id
    
    # Delete associated media files if any
    if review.media_file:
        for media in review.media_file.split(','):
            media = media.strip()
            if media:
                delete_file(media)
            
    db.session.delete(review)
    db.session.commit()
    
    flash('Review deleted successfully.', 'info')
    return redirect(url_for('user_bp.product_detail', product_id=product_id))
