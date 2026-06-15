from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    # Set up of users table
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # Set up pk
    username = Column(String, unique=True, index=True, nullable=False)
    cash_balance = Column(Float, default=10000.0, nullable=False)