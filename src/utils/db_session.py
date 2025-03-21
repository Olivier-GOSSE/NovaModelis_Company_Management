"""
Database session utility module.
This module provides utilities for managing database sessions.
"""
import logging
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

from database.base import SessionLocal

logger = logging.getLogger(__name__)

@contextmanager
def db_session():
    """
    Context manager for database sessions.
    
    This context manager ensures that the session is properly closed
    after use, and that any exceptions are properly handled.
    
    Yields:
        Session: A SQLAlchemy session object.
    
    Example:
        with db_session() as session:
            users = session.query(User).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise
    finally:
        session.close()
