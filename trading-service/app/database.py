import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get PostgreSQL database details from environment variables
# Fallback to a local default i not configured
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/papertrader")

# Initialize the engine connection
engine = create_engine(DATABASE_URL)

# Create a session maker for handling transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Generate and return (yield) database session on request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        