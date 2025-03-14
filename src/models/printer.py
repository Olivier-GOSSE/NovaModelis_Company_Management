"""
Printer model for the application.
"""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum
from sqlalchemy.orm import relationship

from database.base import Base
from models import PrinterStatus


class Printer(Base):
    """
    Printer model.
    """
    __tablename__ = "printers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    build_volume_x = Column(Integer, nullable=False)  # mm
    build_volume_y = Column(Integer, nullable=False)  # mm
    build_volume_z = Column(Integer, nullable=False)  # mm
    status = Column(Enum(PrinterStatus), default=PrinterStatus.IDLE, nullable=False)
    ip_address = Column(String(50), nullable=True)
    api_key = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    print_jobs = relationship("PrintJob", back_populates="printer")
    
    @property
    def build_volume(self):
        """
        Get the build volume as a string.
        
        Returns:
            str: The build volume as a string.
        """
        return f"{self.build_volume_x} x {self.build_volume_y} x {self.build_volume_z} mm"
    
    def __repr__(self):
        return f"<Printer {self.name}>"
