import pytest
from app.models import Base, User

def test_create_user_model(db_session):
    """Check that a user record can be created in the database"""

    # Bind the db metadata
    Base.metadata.create_all(bind=db_session.get_bind())

    # Initialize User record with test funds
    new_user = User(username="trader_juan", cash_balance=10000.0)

    # Add and save record into database
    db.session.add(new_user)
    db.sessio.commit()

    # Query db to confirm user record has been successfully stored
    stored_user = db.session.query(User).filter_by(username="trader_juan").first()

    # Assertions
    assert stored_user is not None
    assert stored_user.id is not None # Auto-gen. primary key
    assert stored_user.cash_balance == 10000.0