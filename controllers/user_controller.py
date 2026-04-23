import os
import uuid
import urllib.parse  # <--- Added for safe QR URL generation
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, current_app, abort, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
# Added SiteSetting and Review to imports
from models import db, Product, Order, Carousel, Cart, SiteSetting, Review, Coupon, Category

# =========================================================
# 1. PUBLIC VIEWS (Home, Shop, Details)
# =========================================================

def home():
    """Renders the homepage with banners and trending products."""
    banners = Carousel.query.all()
    
    # Fetch Sections
    sections = db.session.query(Product.section).distinct().all()
    sections = [s[0] for s in sections] 
    
    # Create category map from admin uploaded icons
    categories = Category.query.all()
    category_map = {cat.name: cat.image_file for cat in categories}
    
    # Fetch Trending
    products = Product.query.order_by(Product.id.desc()).limit(8).all()

    return render_template('guest/index.html', 
                           banners=banners, 
                           sections=sections, 
                           category_map=category_map,
                           products=products)

def shop():
    """Renders the shop page with pagination and filters."""
    page = request.args.get('page', 1, type=int)
    section_filter = request.args.get('section')
    search_query = request.args.get('search')
    
    query = Product.query
    if section_filter:
        query = query.filter_by(section=section_filter)
        
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    
    products = query.paginate(page=page, per_page=9) 
    sections = [s[0] for s in db.session.query(Product.section).distinct().all()]

    return render_template('guest/shop.html', 
                           products=products, 
                           sections=sections, 
                           current_section=section_filter,
                           search_query=search_query)

def product_detail(product_id):
    """Shows details for a specific product and suggests related products."""
    product = Product.query.get_or_404(product_id)
    
    # Fetch related products from the same section, excluding the current product
    related_products = Product.query.filter(
        Product.section == product.section,
        Product.id != product.id
    ).limit(4).all()
    
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in product.reviews:
        if review.rating in rating_counts:
            rating_counts[review.rating] += 1
            
    return render_template('guest/product_detail.html', product=product, related_products=related_products, rating_counts=rating_counts)

@login_required
def submit_review(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment')
        
        if not rating or rating < 1 or rating > 5:
            flash("Please provide a valid rating between 1 and 5.", "danger")
            return redirect(url_for('user_bp.product_detail', product_id=product.id))
        media_file_name = None
        if 'media_file' in request.files:
            files = request.files.getlist('media_file')
            saved_files = []
            for file in files:
                if file and file.filename != '':
                    filename = secure_filename(f"rev_{uuid.uuid4().hex[:8]}_{file.filename}")
                    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(upload_path)
                    saved_files.append(filename)
            if saved_files:
                media_file_name = ",".join(saved_files)
            
        new_review = Review(
            product_id=product.id,
            user_id=current_user.id,
            rating=rating,
            comment=comment,
            media_file=media_file_name
        )
        db.session.add(new_review)
        db.session.commit()
        flash("Thank you for your review!", "success")
        
    return redirect(url_for('user_bp.product_detail', product_id=product.id))

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
    if current_user.is_admin:
        flash("Admins cannot add items to cart.", "warning")
        return redirect(url_for('user_bp.home'))
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
    if current_user.is_admin:
        flash("Admins do not have a shopping cart.", "warning")
        return redirect(url_for('admin_bp.dashboard'))
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    original_subtotal = sum(item.product.base_price * item.quantity for item in cart_items)
    subtotal = sum(item.product.get_price_for_quantity(item.quantity) * item.quantity for item in cart_items)
    bulk_savings = original_subtotal - subtotal
    shipping_total = sum(item.product.shipping_charge for item in cart_items)
    grand_total = subtotal + shipping_total
    
    return render_template('user/cart.html', 
                           cart=cart_items, 
                           subtotal=subtotal, 
                           original_subtotal=original_subtotal,
                           bulk_savings=bulk_savings,
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
    if current_user.is_admin:
        flash("Admins cannot perform checkout.", "warning")
        return redirect(url_for('admin_bp.dashboard'))
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
        item_base_cost = product.get_price_for_quantity(quantity) * quantity
        total_price = item_base_cost + (product.shipping_charge or 0.0)
        
        # Apply Coupon if present
        coupon_code = request.form.get('coupon_code')
        discount_amount = 0.0
        if coupon_code:
            coupon = Coupon.query.filter_by(code=coupon_code.upper(), is_active=True).first()
            if coupon and (coupon.applicable_category == 'All' or coupon.applicable_category == product.section):
                discount_amount = item_base_cost * (coupon.discount_percentage / 100.0)
                total_price -= discount_amount

        # Mandatory Advance (Product Specific)
        advance_amount = total_price * (product.advance_percentage / 100.0)

        # Deduct Stock
        product.stock -= quantity

        # Store everything in session instead of creating order
        session['pending_checkout'] = {
            'type': 'buy_now',
            'product_id': product.id,
            'quantity': quantity,
            'size': size,
            'full_name': full_name,
            'mobile_number': mobile,
            'address': full_address,
            'payment_method': payment_method,
            'instructions': instructions,
            'customization_file': filename,
            'coupon_code': coupon_code
        }

        return redirect(url_for('user_bp.payment_pending'))

    active_coupons = Coupon.query.filter_by(is_active=True).all()
    return render_template('user/checkout.html', product=product, coupons=active_coupons)

@login_required
def apply_coupon():
    """Validates coupon code via AJAX and calculates discount amount."""
    from flask import jsonify
    data = request.get_json()
    code = data.get('code')
    is_cart = data.get('is_cart', False)
    
    if not code:
        return jsonify({"success": False, "message": "No code provided"}), 400
        
    coupon = Coupon.query.filter_by(code=code.upper(), is_active=True).first()
    
    if not coupon:
        return jsonify({"success": False, "message": "Invalid or expired coupon"}), 404

    discount_amount = 0.0
    
    if is_cart:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        applicable_count = 0
        for item in cart_items:
            if coupon.applicable_category == 'All' or coupon.applicable_category == item.product.section:
                item_price = item.product.get_price_for_quantity(item.quantity) * item.quantity
                discount_amount += item_price * (coupon.discount_percentage / 100.0)
                applicable_count += 1
        
        if applicable_count == 0:
            return jsonify({"success": False, "message": "Invalid or expired coupon"}), 400
            
    else:
        product_id = data.get('product_id')
        qty = int(data.get('qty', 1))
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({"success": False, "message": "Product not found"}), 404
            
        if coupon.applicable_category != 'All' and coupon.applicable_category != product.section:
            return jsonify({"success": False, "message": "Invalid or expired coupon"}), 400
            
        item_price = product.get_price_for_quantity(qty) * qty
        discount_amount = item_price * (coupon.discount_percentage / 100.0)

    return jsonify({
        "success": True, 
        "discount_amount": discount_amount,
        "discount_percentage": coupon.discount_percentage,
        "message": f"Coupon applied! Amount: ₹{discount_amount:.2f}"
    })

@login_required
def checkout_cart():
    """Bulk Checkout using Database Cart."""
    if current_user.is_admin:
        flash("Admins cannot perform checkout.", "warning")
        return redirect(url_for('admin_bp.dashboard'))
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('user_bp.home'))

    original_subtotal = sum(item.product.base_price * item.quantity for item in cart_items)
    subtotal = sum(item.product.get_price_for_quantity(item.quantity) * item.quantity for item in cart_items)
    bulk_savings = original_subtotal - subtotal
    
    shipping_total = sum(item.product.shipping_charge for item in cart_items)
    grand_total = subtotal + shipping_total

    # Calculate Mandatory Advance (Sum of individual product requirements)
    mandatory_advance = 0.0
    for item in cart_items:
        item_price = item.product.get_price_for_quantity(item.quantity) * item.quantity
        item_total = item_price + item.product.shipping_charge
        mandatory_advance += item_total * (item.product.advance_percentage / 100.0)

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
        coupon_code = request.form.get('coupon_code')
        
        file = request.files.get('custom_file')
        filename = None
        if file and file.filename != '':
            ext = secure_filename(file.filename).rsplit('.', 1)[1]
            filename = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        # Store everything in session instead of creating order
        session['pending_checkout'] = {
            'type': 'cart',
            'full_name': full_name,
            'mobile_number': mobile,
            'address': full_address,
            'payment_method': payment_method,
            'instructions': instructions,
            'customization_file': filename,
            'coupon_code': coupon_code
        }

        return redirect(url_for('user_bp.payment_pending'))

    active_coupons = Coupon.query.filter_by(is_active=True).all()
    return render_template('user/checkout_cart.html', cart=cart_items, subtotal=subtotal, original_subtotal=original_subtotal, bulk_savings=bulk_savings, shipping=shipping_total, total=grand_total, coupons=active_coupons, mandatory_advance=mandatory_advance)


# =========================================================
# 4. USER PROFILE & ORDER MANAGEMENT
# =========================================================

@login_required
def profile():
    """Displays user's order history. Admins are redirected to dashboard."""
    if current_user.is_admin:
        return redirect(url_for('admin_bp.dashboard'))
        
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date_ordered.desc()).all()
    return render_template('user/profile.html', orders=orders)

@login_required
def update_profile():
    """Handles updating user profile information."""
    if current_user.is_admin:
        flash("Admins cannot update profile details here.", "warning")
        return redirect(url_for('admin_bp.dashboard'))

    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.mobile_number = request.form.get('mobile_number')
        current_user.address = request.form.get('address')
        current_user.city = request.form.get('city')
        current_user.state = request.form.get('state')
        current_user.pincode = request.form.get('pincode')
        
        # New Password logic
        new_password = request.form.get('new_password')
        if new_password and new_password.strip():
            current_user.password = new_password
            flash('Password updated successfully!', 'success')
        
        db.session.commit()
        flash('Profile details updated!', 'success')
        
    return redirect(url_for('user_bp.profile'))

@login_required
def order_detail(order_id):
    """View details of a specific past order."""
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('user/order_detail.html', order=order)

@login_required
def generate_invoice(txn_id):
    """Displays the printable invoice for a specific transaction."""
    # Fetch all items sharing the same Transaction ID
    order_items = Order.query.filter_by(transaction_id=txn_id).all()
    
    if not order_items:
        flash("Invoice not found.", "danger")
        return redirect(url_for('user_bp.profile'))

    # Security check: Does any item belong to this user? (Or is admin)
    first_order = order_items[0]
    if first_order.user_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('user_bp.home'))

    grand_total = sum(item.total_price for item in order_items)

    return render_template('user/invoice.html', 
                           order=first_order, 
                           items=order_items, 
                           grand_total=grand_total)

# =========================================================
# 5. PAYMENT PAGE (Fixed: With Admin UPI Settings)
# =========================================================

@login_required
def payment_page(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return redirect(url_for('user_bp.home'))
        
    related_items = Order.query.filter_by(transaction_id=order.transaction_id).all()
    grand_total = sum(item.total_price for item in related_items)
    total_advance = sum(item.advance_amount for item in related_items)

    # --- QR & UPI LOGIC ---
    try:
        setting = SiteSetting.query.first()
        qr_file = setting.qr_code_file if setting else None
        
        # 1. Get UPI ID and Clean it (Remove spaces/tabs)
        raw_upi_id = setting.upi_id if (setting and setting.upi_id) else 'shop@upi'
        shop_upi_id = raw_upi_id.strip() 

        # 2. Generate Safe QR URL
        generated_qr_url = None
        if not qr_file:
            # Construct the UPI Link manually to ensure 100% compatibility
            clean_name = "Yuki" # No spaces
            clean_amount = f"{total_advance:.2f}" # Default to Advance for mandatory payment
            
            raw_upi_link = f"upi://pay?pa={shop_upi_id}&pn={clean_name}&am={clean_amount}&cu=INR"
            final_data = urllib.parse.quote(raw_upi_link)
            generated_qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&margin=10&data={final_data}"

    except Exception as e:
        print(f">> ERROR generating QR: {e}")
        qr_file = None
        shop_upi_id = 'shop@upi'
        generated_qr_url = None

    return render_template('user/payment.html', 
                           order=order, 
                           grand_total=grand_total, 
                           total_advance=total_advance,
                           qr_code=qr_file,
                           shop_upi_id=shop_upi_id,
                           generated_qr_url=generated_qr_url)

@login_required
def process_payment(order_id):
    """Handles Payment Proof Upload."""
    initial_order = Order.query.get_or_404(order_id)
    
    # 1. Handle File Upload (Screenshot)
    file = request.files.get('payment_proof')
    filename = None
    
    if file and file.filename != '':
        ext = secure_filename(file.filename).rsplit('.', 1)[1]
        # Name it specifically for this order
        filename = f"pay_proof_{initial_order.transaction_id}.{ext}"
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
    
    # 2. Update All Items in this Transaction
    related_items = Order.query.filter_by(transaction_id=initial_order.transaction_id).all()
    
    for item in related_items:
        item.status = "Verification Pending"  # <--- New Status
        if filename:
            item.payment_proof = filename     # <--- Save Screenshot
        
    db.session.commit()
    
    flash('Payment proof uploaded! Waiting for Admin confirmation.', 'info')
    return redirect(url_for('user_bp.generate_invoice', txn_id=initial_order.transaction_id))

@login_required
def payment_pending():
    """Handles Payment Page for orders NOT yet in DB (Held in Cart/Session)."""
    data = session.get('pending_checkout')
    if not data:
        return redirect(url_for('user_bp.cart'))
    
    advance_total_req = 0.0
    
    if data['type'] == 'buy_now':
        product = Product.query.get_or_404(data['product_id'])
        qty = int(data['quantity'])
        base_cost = product.get_price_for_quantity(qty) * qty
        item_total = base_cost + product.shipping_charge
        
        # Apply Coupon
        if data.get('coupon_code'):
            coupon = Coupon.query.filter_by(code=data['coupon_code'].upper(), is_active=True).first()
            if coupon and (coupon.applicable_category == 'All' or coupon.applicable_category == product.section):
                item_total -= base_cost * (coupon.discount_percentage / 100.0)
        
        total_price = item_total
        if data['payment_method'] == '100_online':
            advance_total_req = total_price
        else:
            advance_total_req = total_price * (product.advance_percentage / 100.0)
    else:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        if not cart_items:
            return redirect(url_for('user_bp.cart'))
            
        coupon = None
        if data.get('coupon_code'):
            coupon = Coupon.query.filter_by(code=data['coupon_code'].upper(), is_active=True).first()
            
        for item in cart_items:
            base_cost = item.product.get_price_for_quantity(item.quantity) * item.quantity
            item_total = base_cost + item.product.shipping_charge
            if coupon and (coupon.applicable_category == 'All' or coupon.applicable_category == item.product.section):
                item_total -= base_cost * (coupon.discount_percentage / 100.0)
            
            total_price += item_total
            if data['payment_method'] == '100_online':
                advance_total_req += item_total
            else:
                advance_total_req += item_total * (item.product.advance_percentage / 100.0)

    total_advance = advance_total_req

    # 2. QR Logic
    try:
        setting = SiteSetting.query.first()
        qr_file = setting.qr_code_file if setting else None
        raw_upi_id = setting.upi_id if (setting and setting.upi_id) else 'shop@upi'
        shop_upi_id = raw_upi_id.strip() 
        
        generated_qr_url = None
        if not qr_file:
            clean_name = "Yuki"
            clean_amount = f"{total_advance:.2f}"
            raw_upi_link = f"upi://pay?pa={shop_upi_id}&pn={clean_name}&am={clean_amount}&cu=INR"
            final_data = urllib.parse.quote(raw_upi_link)
            generated_qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&margin=10&data={final_data}"
    except Exception as e:
        print(f"QR Error: {e}")
        qr_file = None
        shop_upi_id = 'shop@upi'
        generated_qr_url = None

    effective_pct = (total_advance / total_price) * 100 if total_price > 0 else 0

    return render_template('user/payment.html', 
                           pending=True, 
                           grand_total=total_price, 
                           total_advance=total_advance,
                           advance_percentage=effective_pct,
                           payment_method=data['payment_method'],
                           qr_code=qr_file,
                           shop_upi_id=shop_upi_id,
                           generated_qr_url=generated_qr_url)

@login_required
def process_payment_pending():
    """Finalizes Checkout: Creates Orders and Clears Cart AFTER screenshot is uploaded."""
    data = session.get('pending_checkout')
    if not data:
        return redirect(url_for('user_bp.cart'))
        
    # 1. Handle Screenshot Upload
    file = request.files.get('payment_proof')
    if not file or file.filename == '':
        flash("Please upload payment screenshot to confirm your order.", "danger")
        return redirect(url_for('user_bp.payment_pending'))
        
    shared_txn_id = str(uuid.uuid4().hex[:8]).upper()
    ext = secure_filename(file.filename).rsplit('.', 1)[1]
    proof_filename = f"pay_proof_{shared_txn_id}.{ext}"
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], proof_filename))

    # 2. Create Orders
    order_ids = []
    coupon = None
    if data.get('coupon_code'):
        coupon = Coupon.query.filter_by(code=data['coupon_code'].upper(), is_active=True).first()

    items_to_process = []
    if data['type'] == 'buy_now':
        product = Product.query.get(data['product_id'])
        items_to_process.append({
            'product': product,
            'quantity': int(data['quantity']),
            'size': data['size']
        })
    else:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        for ci in cart_items:
            items_to_process.append({
                'product': ci.product,
                'quantity': ci.quantity,
                'size': ci.size,
                'cart_id': ci.id
            })

    for item_data in items_to_process:
        prod = item_data['product']
        qty = item_data['quantity']
        
        # Deduct Stock
        prod.stock -= qty
        
        base_cost = prod.get_price_for_quantity(qty) * qty
        item_total = base_cost + prod.shipping_charge
        discount = 0.0
        if coupon and (coupon.applicable_category == 'All' or coupon.applicable_category == prod.section):
            discount = base_cost * (coupon.discount_percentage / 100.0)
            item_total -= discount
            
        if data['payment_method'] == '100_online':
            advance_amt = item_total
        else:
            advance_amt = item_total * (prod.advance_percentage / 100.0)

        new_order = Order(
            transaction_id=shared_txn_id,
            user_id=current_user.id,
            product_id=prod.id,
            quantity=qty,
            size=item_data['size'],
            total_price=item_total,
            discount_amount=discount,
            advance_amount=advance_amt,
            amount_paid=0.0,
            full_name=data['full_name'],
            mobile_number=data['mobile_number'],
            address=data['address'],
            payment_method=data['payment_method'],
            instructions=data['instructions'],
            customization_file=data['customization_file'],
            payment_proof=proof_filename,
            status="Verification Pending",
            email=current_user.email
        )
        db.session.add(new_order)
        db.session.flush()
        order_ids.append(new_order.id)
        
        # If it was a cart item, delete it
        if 'cart_id' in item_data:
            ci = Cart.query.get(item_data['cart_id'])
            if ci: db.session.delete(ci)

    db.session.commit()
    session.pop('pending_checkout', None)
    
    flash('Order confirmed! Admin will verify your payment shortly.', 'success')
    return redirect(url_for('user_bp.generate_invoice', txn_id=shared_txn_id))
