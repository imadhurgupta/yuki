from app import app
from models import db, User, Product, Carousel, Cart

def create_database():
    """
    Resets the database and seeds it with initial data.
    WARNING: This will delete all existing users, orders, and products.
    """
    with app.app_context():
        # 1. RESET DATABASE
        print(">> Dropping old tables...")
        db.drop_all()  # Deletes existing data
        print(">> Creating new tables...")
        db.create_all() # Creates tables based on your models
        
        # 2. CREATE ADMIN USER
        # This is the account you will use to log into the Dashboard.
        print(">> Creating Admin User...")
        admin = User(
            username='Admin', 
            email='madhurguptaofficial@gmail.com', 
            is_admin=True
        )
        admin.set_password('admin123') # Sets the password hash
        db.session.add(admin)
        
        # 3. ADD CAROUSEL BANNERS
        # These appear on the Home page.
        print(">> Adding Banner Images...")
        b1 = Carousel(
            title="Summer Collection 2026", 
            subtitle="Flat 30% Off on Hoodies", 
            image_file="banner1.jpg", 
            link="#"
        )
        b2 = Carousel(
            title="Custom Mugs", 
            subtitle="Start your day with a smile", 
            image_file="banner2.jpg", 
            link="#"
        )
        db.session.add_all([b1, b2])

        # 4. ADD SAMPLE PRODUCTS
        # We use 'section' for the Main Category (buttons on Shop page)
        # We use 'category' for the Subtype (displayed on Product card)
        print(">> Seeding Inventory...")
        
        p1 = Product(
            name="Classic Black Tee", 
            base_price=499, 
            section="T-Shirts",       # Main Filter
            category="Standard",      # Subtype
            image_file="tshirt.jpg",
            sizes="S, M, L, XL"       # Default sizes
        )
        
        p2 = Product(
            name="Urban Heavy Hoodie", 
            base_price=999, 
            section="Hoodies",        # Main Filter
            category="Oversized",     # Subtype
            image_file="hoodie.jpg",
            sizes="M, L, XL"
        )
        
        p3 = Product(
            name="Summer Crop Top", 
            base_price=399, 
            section="T-Shirts",       # Main Filter
            category="Crop Top",      # Subtype
            image_file="crop.jpg",
            sizes="S, M, L"
        )
        
        p4 = Product(
            name="Custom Coffee Mug", 
            base_price=199, 
            section="Mugs",           # Main Filter
            category="Ceramic",       # Subtype
            image_file="mug.jpg",
            sizes="Standard"
        )
        
        # Add all objects to the session
        db.session.add_all([p1, p2, p3, p4])
        
        # 5. COMMIT CHANGES
        db.session.commit()
        print(">> Success! Database initialized with correct categories.")
        print(">> You can now run 'python run.py'")

if __name__ == "__main__":
    create_database()