"""
Database base module for the application.
"""
import os
import sys

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config


# Create engine
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if config.DATABASE_URL.startswith("sqlite") else {},
    echo=config.SQL_ECHO
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


def init_db():
    """
    Initialize the database.
    """
    # Import all models to ensure they are registered with the Base
    from models import (
        User, Printer, Customer, SalesChannel, Order, OrderItem, 
        PrintJob, CustomerEmail
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
