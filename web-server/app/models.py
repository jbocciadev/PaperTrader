from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    # Set up of users table
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # Set up pk
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    cash_balance = Column(Float, default=10000.0, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # ID as primary key
    # Link the user from users database via foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shares = Column(Integer, nullable=False)
    ticker = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False) # Options: "Buy" or "Sell"

