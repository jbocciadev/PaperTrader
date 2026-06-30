import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv(dotenv_path="../.env")

# Get PostgreSQL database details from environment variables
# Fallback to a local default i not configured
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/papertrader")

# Check that a db was loaded, otherwise raise an error
if not DATABASE_URL:
    raise ValueError("DATABASE_URL env var missing or not loaded.")

# Initialize the engine connection
engine = create_engine(DATABASE_URL)

# Create a session maker for handling transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Generate and return (yield) database session on request"""
    # Reference: https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
