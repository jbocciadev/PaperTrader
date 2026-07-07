import pytest
from app.models import Base, User, Transaction

def test_create_user_model(db_session):
    """Check that a user record can be created in the database"""

    # Bind the db metadata
    Base.metadata.create_all(bind=db_session.get_bind())

    # Initialize User record with test funds
    new_user = User(username="trader_juan",password_hash="abc123xyz", cash_balance=10000.0)

    # Add and save record into database
    db_session.add(new_user)
    db_session.commit()

    # Query db to confirm user record has been successfully stored
    stored_user = db_session.query(User).filter_by(username="trader_juan").first()

    # Assertions
    assert stored_user is not None
    assert stored_user.id is not None # Auto-gen. primary key
    assert stored_user.cash_balance == 10000.0

def test_create_transaction_ledger_entry(db_session):
    """Check that transactions are stored with foreign key to user"""

    Base.metadata.create_all(bind=db_session.get_bind())

    # Create mock user for the test
    user = User(username="test_investor", password_hash="abc123xyz", cash_balance=50000.0)
    db_session.add(user)
    db_session.commit()

    # Create details for transaction record
    transaction_record = Transaction(
        user_id = user.id,
        ticker = "TSLA",
        shares = 10,
        price = 150.34,
        transaction_type = "BUY"
    )
    db_session.add(transaction_record)
    db_session.commit()

    # Query the database to confirm record has been created correctly
    stored_user = db_session.query(User).filter_by(username="test_investor").first()
    saved_transaction = db_session.query(Transaction).filter_by(ticker="TSLA").first()

    # Assertions
    assert saved_transaction is not None
    assert saved_transaction.id is not None
    assert saved_transaction.user_id == stored_user.id
    assert saved_transaction.transaction_type == "BUY"
