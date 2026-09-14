import os
import sys

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.db.database import engine, Base
from app.db import models  # Import models to register them with Base

def init_db():
    """
    Creates database tables for all defined SQLAlchemy models if they do not exist.
    """
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully.")
