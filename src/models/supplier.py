"""
Supplier model for the application.
"""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from database.base import Base


class Supplier(Base):
    """
    Supplier model.
    """
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    contact_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address_line1 = Column(String(100), nullable=True)
    address_line2 = Column(String(100), nullable=True)
    city = Column(String(50), nullable=True)
    state_province = Column(String(50), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    website = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    emails = relationship("SupplierEmail", back_populates="supplier", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        """
        Get the full name of the supplier.
        
        Returns:
            str: The full name of the supplier.
        """
        return f"{self.company_name} ({self.contact_name})"
    
    def __repr__(self):
        return f"<Supplier {self.company_name}>"
