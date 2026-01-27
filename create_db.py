from app import app
from models import db, User, Product

def create_database():
    with app.app_context():
        # 1. Wipe everything (Clean Slate)
        db.drop_all()
        db.create_all()
        print(">> Old tables dropped and new tables created.")
        
        # 2. Create Admin
        admin = User(username='admin', email='madhurguptaofficial@gmail.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        print(">> Admin account created.")
        
        # 3. Add Sample Products (This was missing logic before)
        # Note: 'materials' field is REMOVED to prevent crashes
        product1 = Product(
            name="Custom Printed T-Shirt",
            base_price=499.0,
            category="T-Shirts",
            sizes="S, M, L, XL",
            image_file="default_tshirt.jpg" # Make sure to put a dummy image in static/uploads if possible
        )

        product2 = Product(
            name="Personalized Coffee Mug",
            base_price=299.0,
            category="Mugs",
            sizes="Standard",
            image_file="default_mug.jpg"
        )

        product3 = Product(
            name="Premium Hoodie",
            base_price=899.0,
            category="Hoodies",
            sizes="M, L, XL, XXL",
            image_file="default_hoodie.jpg"
        )

        # Add objects to session
        db.session.add(product1)
        db.session.add(product2)
        db.session.add(product3)
        
        # 4. Commit Changes
        db.session.commit()
        print(">> Products added successfully!")
        print(">> Database initialization complete.")

if __name__ == "__main__":
    create_database()