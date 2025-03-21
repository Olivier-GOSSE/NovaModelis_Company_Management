"""
Raw Material model for the application.
"""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base


class RawMaterial(Base):
    """Raw Material model."""
    __tablename__ = "raw_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    reference_code = Column(String, index=True)
    type = Column(String)
    unit = Column(String)
    cost = Column(Float)
    quantity = Column(Float)
    reorder_level = Column(Float)
    supplier = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        """Return string representation of the model."""
        return f"<RawMaterial {self.name}>"
