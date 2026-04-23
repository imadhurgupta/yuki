import os
import urllib.request
from urllib.parse import quote

def download_placeholder_images():
    # Set this to your Flask app's actual image directory
    # Usually it's something like 'static/images'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(base_dir, 'static', 'images')
    
    # Create the directory if it doesn't exist
    os.makedirs(image_dir, exist_ok=True)

    # List of all images referenced in the database script
    images_to_create = [
        # Categories
        ('cat_home.png', 'Home & Kitchen'),
        ('cat_toys.png', 'Toys & Games'),
        ('cat_hobby.png', 'Hobby & Entertainment'),
        ('cat_electronics.png', 'Electronics & Gadgets'),
        ('cat_fashion.png', 'Fashion & Personal Care'),
        
        # Banners (Using a wider aspect ratio)
        ('banner_home.png', 'Home Innovations Banner'),
        ('banner_toys.png', 'Toys & Games Banner'),
        ('banner_hobby.png', 'Cosplay & Hobby Banner'),
        ('banner_electronics.png', 'Tech Gadgets Banner'),
        ('banner_fashion.png', 'Fashion Banner'),

        # Products
        ('prod_oven_knob.png', 'Replacement Oven Knob'),
        ('prod_organizer.png', 'Modular Drawer Organizer'),
        ('prod_juicer.png', 'Citrus Juicer Attachment'),
        ('prod_miniatures.png', 'Tabletop Miniatures'),
        ('prod_tile_holders.png', 'Game Tile Holders'),
        ('prod_puzzle.png', 'Interlocking Puzzle'),
        ('prod_dragon.png', 'Articulated Dragon'),
        ('prod_mask.png', 'Cyberpunk Cosplay Mask'),
        ('prod_ocarina.png', 'Acoustic Ocarina'),
        ('prod_rc_spoiler.png', 'RC Car Spoiler'),
        ('prod_phonestand.png', 'Ergonomic Phone Stand'),
        ('prod_laptop_case.png', 'Vented Laptop Case'),
        ('prod_pi_case.png', 'Raspberry Pi Enclosure'),
        ('prod_pendant.png', 'Geometric Pendant'),
        ('prod_frames.png', 'Ultra-Light Frames'),
        ('prod_crutch_grips.png', 'Ergonomic Crutch Grips'),
    ]

    print(f"Downloading placeholder images to: {image_dir}")
    
    for filename, text in images_to_create:
        filepath = os.path.join(image_dir, filename)
        
        # Only download if the file doesn't already exist
        if not os.path.exists(filepath):
            # Dimensions: 1200x400 for banners, 600x600 for products/categories
            dimensions = "1200x400" if "banner" in filename else "600x600"
            
            # Using placehold.co to generate dark-mode friendly placeholders
            url = f"https://placehold.co/{dimensions}/2a2a2a/ffffff/png?text={quote(text)}"
            
            try:
                urllib.request.urlretrieve(url, filepath)
                print(f"✅ Downloaded: {filename}")
            except Exception as e:
                print(f"❌ Failed to download {filename}: {e}")
        else:
            print(f"⏭️  Already exists: {filename}")

if __name__ == '__main__':
    download_placeholder_images()
    print("All images are ready!")