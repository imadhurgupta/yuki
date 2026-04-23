import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Product, Carousel, Category

def add_data():
    with app.app_context():
        # Clear existing data
        Carousel.query.delete()
        Product.query.delete()
        Category.query.delete()
        
        # Carousels (Banners for each category)
        c1 = Carousel(title="Home & Kitchen Innovations", subtitle="Functional 3D Printed Solutions", image_file="banner_home.png", link="/shop")
        c2 = Carousel(title="Level Up Your Play", subtitle="Miniatures, Puzzles & Board Game Accessories", image_file="banner_toys.png", link="/shop")
        c3 = Carousel(title="Cosplay & Entertainment", subtitle="Props, RC Parts & Musical Instruments", image_file="banner_hobby.png", link="/shop")
        c4 = Carousel(title="Tech & Gadget Accessories", subtitle="Custom Stands, Cases & Enclosures", image_file="banner_electronics.png", link="/shop")
        c5 = Carousel(title="Fashion & Personal Care", subtitle="Unique Jewelry & Ergonomic Aids", image_file="banner_fashion.png", link="/shop")
        db.session.add_all([c1, c2, c3, c4, c5])
        
        # Product categories
        categories = [
            ('Home & Kitchen', 'cat_home.png'), 
            ('Toys & Games', 'cat_toys.png'), 
            ('Hobby & Entertainment', 'cat_hobby.png'), 
            ('Electronics & Gadgets', 'cat_electronics.png'),
            ('Fashion & Personal Care', 'cat_fashion.png')
        ]
        
        for cat_name, img_file in categories:
            cat = Category.query.filter_by(name=cat_name).first()
            if not cat:
                db.session.add(Category(name=cat_name, image_file=img_file))
            else:
                cat.image_file = img_file
                
        # Products
        products = [
            # Home & Kitchen
            Product(name="Custom Replacement Oven Knob", base_price=150.0, shipping_charge=20.0, section="Home & Kitchen", category="Appliance Parts", description="Durable 3D printed replacement knob for standard ovens.", sizes="Universal", image_file="prod_oven_knob.png", stock=100),
            Product(name="Modular Drawer Organizer", base_price=350.0, shipping_charge=40.0, section="Home & Kitchen", category="Organization", description="Customizable modular compartments for kitchen utensils.", sizes="Adjustable", image_file="prod_organizer.png", stock=50),
            Product(name="Citrus Juicer Attachment", base_price=200.0, shipping_charge=25.0, section="Home & Kitchen", category="Gadgets", description="Food-safe 3D printed manual citrus juicer attachment.", sizes="Standard", image_file="prod_juicer.png", stock=75),
            
            # Toys & Games
            Product(name="Fantasy Tabletop Miniature Set", base_price=899.0, shipping_charge=0.0, section="Toys & Games", category="Miniatures", description="Highly detailed resin printed miniatures for D&D and tabletop RPGs.", sizes="28mm Scale", image_file="prod_miniatures.png", stock=30),
            Product(name="Hexagonal Board Game Tile Holders", base_price=450.0, shipping_charge=30.0, section="Toys & Games", category="Board Game Accessories", description="Interlocking tile holders for popular strategy board games.", sizes="Standard Hex", image_file="prod_tile_holders.png", stock=60),
            Product(name="Brain Teaser Interlocking Puzzle", base_price=299.0, shipping_charge=20.0, section="Toys & Games", category="Puzzles", description="Challenging 3D printed geometric interlocking puzzle.", sizes="Small", image_file="prod_puzzle.png", stock=100),
            Product(name="Articulated Dragon Action Figure", base_price=1200.0, shipping_charge=50.0, section="Toys & Games", category="Action Figures", description="Fully articulated 3D printed dragon with moving joints.", sizes="Large", image_file="prod_dragon.png", stock=20),
            
            # Hobby & Entertainment
            Product(name="Cyberpunk Cosplay Mask", base_price=2500.0, shipping_charge=0.0, section="Hobby & Entertainment", category="Cosplay Props", description="High-quality 3D printed wearable cyberpunk mask with LED mounts.", sizes="One Size", image_file="prod_mask.png", stock=15),
            Product(name="Acoustic 3D Printed Ocarina", base_price=600.0, shipping_charge=40.0, section="Hobby & Entertainment", category="Musical Instruments", description="Fully playable, pitch-perfect 12-hole ocarina.", sizes="Alto C", image_file="prod_ocarina.png", stock=40),
            Product(name="RC Car Custom Spoiler", base_price=450.0, shipping_charge=30.0, section="Hobby & Entertainment", category="RC Parts", description="Aerodynamic custom spoiler for 1/10 scale RC drift cars.", sizes="1/10 Scale", image_file="prod_rc_spoiler.png", stock=40),
            
            # Electronics & Gadgets
            Product(name="Adjustable Ergonomic Phone Stand", base_price=299.0, shipping_charge=25.0, section="Electronics & Gadgets", category="Phone Accessories", description="Sturdy 3D printed phone and tablet stand with adjustable angles.", sizes="Universal", image_file="prod_phonestand.png", stock=150),
            Product(name="Vented Hard Shell Laptop Case", base_price=1299.0, shipping_charge=80.0, section="Electronics & Gadgets", category="Laptop Cases", description="Snap-on 3D printed protective laptop shell with hexagonal cooling vents.", sizes="13-inch / 15-inch", image_file="prod_laptop_case.png", stock=25),
            Product(name="Raspberry Pi Custom Enclosure", base_price=599.0, shipping_charge=40.0, section="Electronics & Gadgets", category="Enclosures", description="Vented custom enclosure for Raspberry Pi 4 with cooling fan mount.", sizes="Standard Pi 4", image_file="prod_pi_case.png", stock=80),
            
            # Fashion & Personal Care
            Product(name="Geometric Custom Pendant", base_price=199.0, shipping_charge=20.0, section="Fashion & Personal Care", category="Jewelry", description="Unique geometric 3D printed pendant necklace.", sizes="One Size", image_file="prod_pendant.png", stock=60),
            Product(name="Ultra-Light Eyewear Frames", base_price=899.0, shipping_charge=40.0, section="Fashion & Personal Care", category="Eyewear", description="Custom fit, ultra-lightweight 3D printed glasses frames.", sizes="Custom", image_file="prod_frames.png", stock=20),
            Product(name="Ergonomic Crutch Grip Pads", base_price=350.0, shipping_charge=30.0, section="Fashion & Personal Care", category="Healthcare Aids", description="Soft-TPU 3D printed ergonomic grips to reduce hand fatigue.", sizes="Universal", image_file="prod_crutch_grips.png", stock=45)
        ]
        
        db.session.add_all(products)
        
        try:
            db.session.commit()
            print("Successfully added new categories, banners, and products to the database!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding data: {e}")

if __name__ == '__main__':
    add_data()