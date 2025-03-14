"""
Sales channel model for the application.
"""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship

from database.base import Base


class SalesChannel(Base):
    """
    Sales channel model.
    """
    __tablename__ = "sales_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    website_url = Column(String(255), nullable=True)
    api_key = Column(String(255), nullable=True)
    commission_rate = Column(Float, default=0.0, nullable=False)  # Percentage
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    orders = relationship("Order", back_populates="sales_channel")
    
    def __repr__(self):
        return f"<SalesChannel {self.name}>"
