import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create a temporary database for test runs
@pytest.fixture(scope="function")
def db_session():
    """Provides a clean, isolated in-memory database session for a unit test."""
    
    # Cerate the virtual memory engine
    engine = create_engine("sqlite:///:memory:")
    
    # Create a session factory
    TestingSessionLocal = sessionmaker(bind=engine)
    
    
    session = TestingSessionLocal()
    try:
        yield session  # Pass the active database connection to the test function
    finally:
        session.close()  # Remove the database when session os over