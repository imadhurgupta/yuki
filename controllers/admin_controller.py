import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from models import db, Product, Order

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def dashboard():
    # Sort orders by date (newest first)
    orders = Order.query.order_by(Order.date_ordered.desc()).all()
    products = Product.query.all()
    active_tab = request.args.get('tab', 'orders')
    
    # FIX: Point to 'user/dashboard.html' since your file is in that folder
    return render_template('admin/dashboard.html', orders=orders, products=products, active_tab=active_tab)

def add_product():
    if request.method == 'POST':
        # 1. Get data
        name = request.form.get('name')
        price = request.form.get('price')
        category = request.form.get('category')
        sizes = request.form.get('sizes')
        
        # 2. Handle Image
        image = request.files.get('image')
        filename = None
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        # 3. Create Product (REMOVE 'materials' from here!)
        new_product = Product(
            name=name,
            base_price=float(price),
            category=category,
            sizes=sizes,
            image_file=filename
            # materials=...  <-- DELETE THIS LINE if it exists
        )

        try:
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            print(e)

        return redirect(url_for('admin_bp.dashboard'))
    
    return redirect(url_for('admin_bp.dashboard'))

def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        product.name = request.form.get('name')
        product.base_price = float(request.form.get('price'))
        product.description = request.form.get('description')
        product.sizes = request.form.get('sizes')
        product.materials = request.form.get('materials')
        product.category = request.form.get('category') # <--- NEW: Update Category
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                product.image_file = filename
        
        db.session.commit()
        flash('Product updated!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('admin_bp.dashboard', tab='products'))

def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('admin_bp.dashboard', tab='products'))

def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status')
    db.session.commit()
    return redirect(url_for('admin_bp.dashboard'))