import os
import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, current_app, abort, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Product, Order, Carousel

# --- HOME PAGE ---
def home():
    # 1. Fetch Banners (Managed via Admin -> Website Tab)
    banners = Carousel.query.all()
    
    # 2. Fetch Sections (Managed via Admin -> Product -> "Section" field)
    # This gets unique values like "Men", "Women", "Kids" dynamically
    sections = db.session.query(Product.section).distinct().all()
    sections = [s[0] for s in sections] # Clean the list
    
    # 3. Fetch Trending Products (Managed via Admin -> Inventory)
    # Shows the 8 most recently added items
    products = Product.query.order_by(Product.id.desc()).limit(8).all()

    return render_template('guest/index.html', 
                           banners=banners, 
                           sections=sections, 
                           products=products)

# --- PRODUCT DETAIL PAGE ---
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('guest/product_detail.html', product=product)

# --- INVOICE GENERATOR ---
@login_required
def generate_invoice(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Security: Only owner or admin can view
    if order.user_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('user_bp.home'))

    return render_template('user/invoice.html', order=order)

# --- 1. DIRECT ORDER (Single Product - Buy Now) ---
@login_required
def checkout(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        # Capture Data
        full_name = request.form.get('full_name')
        mobile = request.form.get('mobile_number')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        payment_method = request.form.get('payment_method')
        instructions = request.form.get('instructions')
        
        quantity = int(request.form.get('quantity'))
        size = request.form.get('size')
        
        # File Upload
        file = request.files.get('custom_file')
        filename = None
        if file and file.filename != '':
            original_filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{original_filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            file.save(file_path)
            filename = unique_name
        
        # Calculate Logic
        subtotal = product.base_price * quantity
        shipping = product.shipping_charge or 0.0
        total_price = subtotal + shipping

        # Create ONE Order Record
        new_order = Order(
            transaction_id=str(uuid.uuid4().hex[:8]).upper(),
            user_id=current_user.id,
            product_id=product.id,
            quantity=quantity,
            total_price=total_price,
            full_name=full_name,
            mobile_number=mobile,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            payment_method=payment_method,
            instructions=instructions,
            size=size,
            customization_file=filename,
            date_ordered=datetime.utcnow(),
            status="Pending"
        )

        db.session.add(new_order)
        db.session.commit()

        if payment_method == 'COD':
            flash('Order placed successfully!', 'success')
            return redirect(url_for('user_bp.generate_invoice', order_id=new_order.id))
        else:
            return redirect(url_for('user_bp.payment_page', order_id=new_order.id))

    return render_template('user/checkout.html', product=product)

# --- 2. CART CHECKOUT (Multiple Products) ---
@login_required
def checkout_cart():
    # 1. Get Cart
    cart = session.get('cart', [])
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('user_bp.home'))

    # 2. Calculate Totals
    subtotal = sum(item['price'] * item['qty'] for item in cart)
    shipping_total = sum(item['shipping'] for item in cart)
    grand_total = subtotal + shipping_total

    # 3. Handle POST (When user clicks "Place Order" on the checkout page)
    if request.method == 'POST':
        # Capture Common Data
        full_name = request.form.get('full_name')
        mobile = request.form.get('mobile_number')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        payment_method = request.form.get('payment_method')
        instructions = request.form.get('instructions')
        
        # File Upload (Applies to whole order)
        file = request.files.get('custom_file')
        filename = None
        if file and file.filename != '':
            original_filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{original_filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            file.save(file_path)
            filename = unique_name

        # Generate ONE Transaction ID for all items
        txn_id = str(uuid.uuid4().hex[:8]).upper()

        # Create Database Records
        for item in cart:
            item_total = (item['price'] * item['qty']) + item['shipping']
            
            new_order = Order(
                transaction_id=txn_id,
                user_id=current_user.id,
                product_id=item['id'],
                quantity=item['qty'],
                size=item['size'],
                total_price=item_total,
                full_name=full_name,
                mobile_number=mobile,
                address=address,
                city=city,
                state=state,
                pincode=pincode,
                payment_method=payment_method,
                instructions=instructions, 
                customization_file=filename,
                date_ordered=datetime.utcnow(),
                status="Pending"
            )
            db.session.add(new_order)

        # Commit and Clear Cart
        db.session.commit()
        session.pop('cart', None)
        session.modified = True

        flash('Bulk order placed successfully!', 'success')
        return redirect(url_for('user_bp.profile'))

    # 4. Render the BULK checkout template (Critical Fix)
    return render_template('user/checkout_cart.html', cart=cart, subtotal=subtotal, shipping=shipping_total, total=grand_total)

# --- USER PROFILE PAGE ---
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date_ordered.desc()).all()
    return render_template('user/profile.html', orders=orders)

# --- ORDER DETAIL ---
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    return render_template('user/order_detail.html', order=order)

# --- PAYMENT GATEWAY ---
@login_required
def payment_page(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('user_bp.home'))
    return render_template('user/payment.html', order=order)

# --- PROCESS PAYMENT ---
@login_required
def process_payment(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = "Processing" 
    db.session.commit()
    flash('Payment Successful! Order is now processing.', 'success')
    return redirect(url_for('user_bp.generate_invoice', order_id=order.id))

# --- CART: ADD ITEM ---
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    
    quantity = int(request.form.get('quantity', 1))
    size = request.form.get('size', 'Std')
    
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    
    found = False
    for item in cart:
        if item['id'] == product.id and item['size'] == size:
            item['qty'] += quantity
            found = True
            break
    
    if not found:
        cart.append({
            'id': product.id,
            'name': product.name,
            'price': product.base_price,
            'image': product.image_file,
            'size': size,
            'qty': quantity,
            'shipping': product.shipping_charge
        })
    
    session.modified = True
    flash(f'Added {product.name} to cart!', 'success')
    return redirect(url_for('user_bp.cart'))

# --- CART: VIEW PAGE ---
@login_required
def cart():
    cart = session.get('cart', [])
    
    subtotal = sum(item['price'] * item['qty'] for item in cart)
    shipping_total = sum(item['shipping'] for item in cart)
    grand_total = subtotal + shipping_total
    
    return render_template('user/cart.html', cart=cart, subtotal=subtotal, shipping=shipping_total, total=grand_total)

# --- CART: REMOVE ITEM ---
@login_required
def remove_from_cart(index):
    if 'cart' in session:
        cart = session['cart']
        if 0 <= index < len(cart):
            item_name = cart[index]['name']
            del cart[index]
            session.modified = True
            flash(f'Removed {item_name} from cart.', 'info')
    return redirect(url_for('user_bp.cart'))

# --- ABOUT PAGE ---
def about():
    return render_template('guest/about.html')

# --- CONTACT PAGE ---
def contact():
    if request.method == 'POST':
        # Capture form data (In a real app, you'd send an email here)
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Just show success message for now
        flash(f'Thanks {name}! We have received your message and will reply to {email} shortly.', 'success')
        return redirect(url_for('user_bp.contact'))
        
    return render_template('guest/contact.html')

# --- SHOP PAGE (All Products) ---
def shop():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category')
    
    query = Product.query
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    # Show 9 products per page
    products = query.paginate(page=page, per_page=9) 
    
    # Get all unique categories for the filter buttons
    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]

    return render_template('guest/shop.html', 
                           products=products, 
                           categories=categories, 
                           current_category=category_filter)