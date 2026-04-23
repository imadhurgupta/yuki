import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Carousel

def clear_banners():
    with app.app_context():
        try:
            num_deleted = Carousel.query.delete()
            db.session.commit()
            print(f"Successfully removed all {num_deleted} banners from the database.")
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing banners: {e}")

if __name__ == '__main__':
    clear_banners()
