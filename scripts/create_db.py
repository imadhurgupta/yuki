import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
from models import db, User, Product, Carousel, SiteSetting 
import os
import time
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """
    Resets the database and seeds it with initial data.
    """
    max_retries = 15
    db_connected = False

    # 1. WAIT FOR DATABASE CONNECTION
    for attempt in range(max_retries):
        try:
            with app.app_context():
                print(f">> Connecting to database (Attempt {attempt+1}/{max_retries})...")
                db.create_all() # Ensure tables exist
                db_connected = True
                print(">> Connection successful.")
                break 
        except OperationalError as e:
            print(f">> Database not ready. Retrying in 2s...")
            time.sleep(2)
    
    if not db_connected:
        print(">> CRITICAL: Could not connect to database.")
        exit(1)

    # 2. SEED / UPDATE DATA
    with app.app_context():
        # --- A. ADMIN USER SETUP ---
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_pass = os.getenv('ADMIN_PASSWORD')

        # 1. Promote Correct Admin
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            print(f">> Creating NEW Admin User: {admin_email}")
            admin = User(full_name='System Admin', email=admin_email, is_admin=True)
            db.session.add(admin)
        else:
            print(f">> Promoting to Admin: {admin_email}")
            admin.is_admin = True
            admin.full_name = 'System Admin'
        admin.password = admin_pass

        # 2. Demote ALL Other Admins
        # This ensures that only the email specified in .env is the admin.
        User.query.filter(User.email != admin_email, User.is_admin == True).update({User.is_admin: False})
        print(f">> Demoted all other users from Admin status.")

        
        # --- B. SEED SETTINGS ---
        if not SiteSetting.query.first():
            print(">> Seeding Default Site Settings...")
            db.session.add(SiteSetting(upi_id='shop@upi'))

        # --- C. SEED BANNERS (If missing) ---
        if Carousel.query.count() == 0:
            print(">> Seeding Banners...")
            b1 = Carousel(title="Summer Collection", subtitle="Flat 30% Off", image_file="default.jpg", link="#")
            db.session.add(b1)

        # --- D. SEED PRODUCTS (If missing) ---
        if Product.query.count() == 0:
            print(">> Seeding Inventory...")
            p1 = Product(name="Classic Black Tee", base_price=499, section="T-Shirts", category="Standard", image_file="default.jpg", sizes="S, M, L, XL")
            p2 = Product(name="Urban Heavy Hoodie", base_price=999, section="Hoodies", category="Oversized", image_file="default.jpg", sizes="M, L, XL")
            db.session.add_all([p1, p2])
        
        # --- E. COMMIT EVERYTHING ---
        db.session.commit()
        
        print("----------------------------------------------------")
        print(f"   LOGIN CREDENTIALS (UPDATED): ")
        print(f"   Email:    {admin_email}")
        print(f"   Password: {admin_pass}")
        print("----------------------------------------------------")

if __name__ == "__main__":
    create_database()