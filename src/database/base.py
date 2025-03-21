"""
Database base module for the application.

This module provides the SQLAlchemy engine, session factory, and base class
for all models. It also provides a function to initialize the database.
"""
import os
import sys
import logging
import time
from contextlib import contextmanager

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

import config
from utils.performance import timeit

logger = logging.getLogger(__name__)

# Create engine with optimized settings
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if config.DATABASE_URL.startswith("sqlite") else {},
    echo=config.SQL_ECHO,
    pool_size=10,  # Number of connections to keep open
    max_overflow=20,  # Maximum number of connections to create beyond pool_size
    pool_timeout=30,  # Seconds to wait before giving up on getting a connection from the pool
    pool_recycle=1800  # Seconds after which a connection is recycled (30 minutes)
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ScopedSession = scoped_session(SessionLocal)

# Create declarative base
Base = declarative_base()

# Add query property to Base
Base.query = ScopedSession.query_property()


# Add event listeners for query performance logging
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    if config.SQL_ECHO:
        logger.debug(f"SQL: {statement}")
        logger.debug(f"Parameters: {parameters}")


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    try:
        total = time.time() - conn.info['query_start_time'].pop(-1)
        if total > 0.5:  # Log slow queries (more than 500ms)
            logger.warning(f"Slow query ({total:.2f}s): {statement}")
        elif config.SQL_ECHO:
            logger.debug(f"Query execution time: {total:.2f}s")
    except (IndexError, KeyError) as e:
        logger.error(f"Error calculating query time: {str(e)}")


@timeit
def init_db():
    """
    Initialize the database.
    
    This function imports all models to ensure they are registered with the Base,
    and creates all tables in the database.
    """
    # Import all models to ensure they are registered with the Base
    from models import (
        User, Printer, Customer, SalesChannel, Order, OrderItem, 
        PrintJob, CustomerEmail, RawMaterial, Supplier, SupplierEmail
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
