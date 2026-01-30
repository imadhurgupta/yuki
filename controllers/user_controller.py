import os
import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, current_app, abort, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
# from flask_mail import Message # Uncomment if you have SMTP configured
from models import db, Product, Order, Carousel, Cart 

# =========================================================
# 1. PUBLIC VIEWS (Home, Shop, Details)
# =========================================================

def home():
    """Renders the homepage with banners and trending products."""
    banners = Carousel.query.all()
    
    # Fetch Sections
    sections = db.session.query(Product.section).distinct().all()
    sections = [s[0] for s in sections] 
    
    # Fetch Trending
    products = Product.query.order_by(Product.id.desc()).limit(8).all()

    return render_template('guest/index.html', 
                           banners=banners, 
                           sections=sections, 
                           products=products)

def shop():
    """Renders the shop page with pagination and filters."""
    page = request.args.get('page', 1, type=int)
    section_filter = request.args.get('section')
    
    query = Product.query
    if section_filter:
        query = query.filter_by(section=section_filter)
    
    products = query.paginate(page=page, per_page=9) 
    sections = [s[0] for s in db.session.query(Product.section).distinct().all()]

    return render_template('guest/shop.html', 
                           products=products, 
                           sections=sections, 
                           current_section=section_filter)

def product_detail(product_id):
    """Shows details for a specific product."""
    product = Product.query.get_or_404(product_id)
    return render_template('guest/product_detail.html', product=product)

def about():
    return render_template('guest/about.html')

def contact():
    """Handles the contact form."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        print(f">> MOCK EMAIL: Message received from {name} ({email})")
        flash(f'Thanks {name}! We will get back to you shortly.', 'success')
        return redirect(url_for('user_bp.contact'))
        
    return render_template('guest/contact.html')


# =========================================================
# 2. CART ACTIONS (DATABASE BASED)
# =========================================================

@login_required
def add_to_cart(product_id):
    """Adds item to the Database Cart."""
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    size = request.form.get('size', 'Std')
    
    existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product.id, size=size).first()
    
    if existing_item:
        existing_item.quantity += quantity
        flash(f'Updated quantity for {product.name}!', 'info')
    else:
        new_item = Cart(
            user_id=current_user.id,
            product_id=product.id,
            quantity=quantity,
            size=size
        )
        db.session.add(new_item)
        flash(f'Added {product.name} to cart!', 'success')
    
    db.session.commit()
    return redirect(url_for('user_bp.cart'))

@login_required
def cart():
    """Displays user's cart from Database."""
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    subtotal = sum(item.product.base_price * item.quantity for item in cart_items)
    shipping_total = sum(item.product.shipping_charge for item in cart_items)
    grand_total = subtotal + shipping_total
    
    return render_template('user/cart.html', 
                           cart=cart_items, 
                           subtotal=subtotal, 
                           shipping=shipping_total, 
                           total=grand_total)

@login_required
def remove_from_cart(cart_id):
    """Removes item from DB Cart."""
    item = Cart.query.get_or_404(cart_id)
    
    if item.user_id != current_user.id:
        abort(403)
        
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('user_bp.cart'))


# =========================================================
# 3. CHECKOUT LOGIC (Stock Logic Only)
# =========================================================

@login_required
def checkout(product_id):
    """Buy Now (Single Item Checkout)."""
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))

        # Stock Validation
        if product.stock < quantity:
            flash(f"Sorry! Only {product.stock} units available for {product.name}.", "danger")
            return redirect(url_for('user_bp.product_detail', product_id=product.id))

        # Capture Data
        full_name = request.form.get('full_name')
        mobile = request.form.get('mobile_number')
        address_parts = [
            request.form.get('address'),
            request.form.get('city'),
            request.form.get('state'),
            request.form.get('pincode')
        ]
        full_address = ", ".join(filter(None, address_parts))
        
        payment_method = request.form.get('payment_method')
        instructions = request.form.get('instructions')
        size = request.form.get('size')
        
        # Handle File Upload
        file = request.files.get('custom_file')
        filename = None
        if file and file.filename != '':
            ext = secure_filename(file.filename).rsplit('.', 1)[1]
            filename = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        # Calculate Cost
        total_price = (product.base_price * quantity) + (product.shipping_charge or 0.0)

        # Deduct Stock
        product.stock -= quantity

        # Save Order
        new_order = Order(
            transaction_id=str(uuid.uuid4().hex[:8]).upper(),
            user_id=current_user.id,
            product_id=product.id,
            quantity=quantity,
            total_price=total_price,
            full_name=full_name,
            mobile_number=mobile,
            address=full_address,
            payment_method=payment_method,
            instructions=instructions,
            size=size,
            customization_file=filename,
            status="Pending",
            email=current_user.email
        )

        db.session.add(new_order)
        db.session.commit() 

        if payment_method == 'COD':
            flash('Order placed successfully!', 'success')
            return redirect(url_for('user_bp.generate_invoice', order_id=new_order.id))
        else:
            return redirect(url_for('user_bp.payment_page', order_id=new_order.id))

    return render_template('user/checkout.html', product=product)

@login_required
def checkout_cart():
    """Bulk Checkout using Database Cart."""
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('user_bp.home'))

    subtotal = sum(item.product.base_price * item.quantity for item in cart_items)
    shipping_total = sum(item.product.shipping_charge for item in cart_items)
    grand_total = subtotal + shipping_total

    if request.method == 'POST':
        # Stock Validation
        for item in cart_items:
            if item.product.stock < item.quantity:
                flash(f"Out of stock: {item.product.name} (Only {item.product.stock} left). Please update cart.", "danger")
                return redirect(url_for('user_bp.cart'))

        # Capture Data
        full_name = request.form.get('full_name')
        mobile = request.form.get('mobile_number')
        address_parts = [
            request.form.get('address'),
            request.form.get('city'),
            request.form.get('state'),
            request.form.get('pincode')
        ]
        full_address = ", ".join(filter(None, address_parts))
        payment_method = request.form.get('payment_method')
        instructions = request.form.get('instructions')
        
        file = request.files.get('custom_file')
        filename = None
        if file and file.filename != '':
            ext = secure_filename(file.filename).rsplit('.', 1)[1]
            filename = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        # Generate ONE shared transaction ID
        shared_txn_id = str(uuid.uuid4().hex[:8]).upper()
        last_order_id = None
        
        # Create Orders
        for item in cart_items:
            # Deduct Stock
            item.product.stock -= item.quantity

            item_total = (item.product.base_price * item.quantity) + item.product.shipping_charge
            
            new_order = Order(
                transaction_id=shared_txn_id,
                user_id=current_user.id,
                product_id=item.product_id,
                quantity=item.quantity,
                size=item.size,
                total_price=item_total,
                full_name=full_name,
                mobile_number=mobile,
                address=full_address,
                payment_method=payment_method,
                instructions=instructions, 
                customization_file=filename,
                status="Pending",
                email=current_user.email
            )
            db.session.add(new_order)
            db.session.flush()
            last_order_id = new_order.id
        
        # Delete items from cart
        for item in cart_items:
            db.session.delete(item)

        db.session.commit() 

        if payment_method == 'COD':
            flash('Order placed successfully!', 'success')
            return redirect(url_for('user_bp.generate_invoice', order_id=last_order_id))
        else:
            return redirect(url_for('user_bp.payment_page', order_id=last_order_id))

    return render_template('user/checkout_cart.html', cart=cart_items, subtotal=subtotal, shipping=shipping_total, total=grand_total)


# =========================================================
# 4. USER PROFILE & ORDER MANAGEMENT
# =========================================================

@login_required
def profile():
    """Displays user's order history."""
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date_ordered.desc()).all()
    return render_template('user/profile.html', orders=orders)

@login_required
def order_detail(order_id):
    """View details of a specific past order."""
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('user/order_detail.html', order=order)

@login_required
def generate_invoice(order_id):
    """Displays the printable invoice for a specific transaction."""
    current_order = Order.query.get_or_404(order_id)
    
    if current_order.user_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('user_bp.home'))

    # Fetch all items sharing the same Transaction ID
    order_items = Order.query.filter_by(transaction_id=current_order.transaction_id).all()
    grand_total = sum(item.total_price for item in order_items)

    return render_template('user/invoice.html', 
                           order=current_order, 
                           items=order_items, 
                           grand_total=grand_total)

# =========================================================
# 5. PAYMENT MOCKUP
# =========================================================

@login_required
def payment_page(order_id):
    """Mock Payment Gateway Page."""
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return redirect(url_for('user_bp.home'))
        
    # Calculate Total for Bulk Orders
    related_items = Order.query.filter_by(transaction_id=order.transaction_id).all()
    grand_total = sum(item.total_price for item in related_items)

    return render_template('user/payment.html', order=order, grand_total=grand_total)

@login_required
def process_payment(order_id):
    """Mock Payment Success Handler."""
    initial_order = Order.query.get_or_404(order_id)
    related_items = Order.query.filter_by(transaction_id=initial_order.transaction_id).all()
    
    for item in related_items:
        item.status = "Processing"
        
    db.session.commit()
    
    flash('Payment Successful!', 'success')
    return redirect(url_for('user_bp.generate_invoice', order_id=initial_order.id))