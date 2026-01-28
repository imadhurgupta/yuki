from app import app
from models import db, User, Product, Carousel

def create_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print(">> Database refreshed.")
        
        # 1. Admin
        admin = User(username='Admin', email='madhurguptaofficial@gmail.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        
        # 2. Add Carousel Banners
        b1 = Carousel(title="Summer Collection 2026", subtitle="Flat 30% Off on Hoodies", image_file="banner1.jpg", link="#")
        b2 = Carousel(title="Custom Mugs", subtitle="Start your day with a smile", image_file="banner2.jpg", link="#")
        db.session.add_all([b1, b2])

        # 3. Add Products (Section -> Category)
        p1 = Product(name="Men's Classic Tee", base_price=499, section="Men", category="T-Shirts", image_file="tshirt.jpg")
        p2 = Product(name="Men's Urban Hoodie", base_price=999, section="Men", category="Hoodies", image_file="hoodie.jpg")
        p3 = Product(name="Women's Crop Top", base_price=399, section="Women", category="T-Shirts", image_file="crop.jpg")
        p4 = Product(name="Custom Coffee Mug", base_price=199, section="Accessories", category="Mugs", image_file="mug.jpg")
        
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()
        print(">> Data initialized successfully!")

if __name__ == "__main__":
    create_database()