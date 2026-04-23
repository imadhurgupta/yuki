import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Product

def clear_products():
    with app.app_context():
        try:
            num_deleted = Product.query.delete()
            db.session.commit()
            print(f"Successfully removed all {num_deleted} products from the database.")
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing products: {e}")

if __name__ == '__main__':
    clear_products()
