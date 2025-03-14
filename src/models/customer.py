"""
Customer model for the application.
"""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from database.base import Base


class Customer(Base):
    """
    Customer model.
    """
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address_line1 = Column(String(100), nullable=True)
    address_line2 = Column(String(100), nullable=True)
    city = Column(String(50), nullable=True)
    state_province = Column(String(50), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    orders = relationship("Order", back_populates="customer")
    emails = relationship("CustomerEmail", back_populates="customer")
    
    @property
    def full_name(self):
        """
        Get the full name of the customer.
        
        Returns:
            str: The full name of the customer.
        """
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Customer {self.full_name}>"
