# File that initializes the PostgreSQL database

from app.database import engine
from app.models import Base

def init_database():
    """Binds metadate schemas into the physical database"""
    print("Initializing database via SQLAlchemy metadata mapping")

    # Find subclasses of Base and create tables
    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully.")

if __name__ == "__main__":
    init_database()
    