"""
Print job model for the application.
"""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base
from models import PrintJobStatus


class PrintJob(Base):
    """
    Print job model.
    """
    __tablename__ = "print_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String(100), nullable=False)
    printer_id = Column(Integer, ForeignKey("printers.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    file_path = Column(String(255), nullable=True)
    material = Column(String(50), nullable=True)
    color = Column(String(50), nullable=True)
    layer_height = Column(Float, nullable=True)  # mm
    infill_percentage = Column(Integer, nullable=True)  # %
    status = Column(Enum(PrintJobStatus), default=PrintJobStatus.QUEUED, nullable=False)
    estimated_print_time = Column(Integer, nullable=True)  # minutes
    actual_print_time = Column(Integer, nullable=True)  # minutes
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    progress = Column(Float, default=0.0, nullable=False)  # %
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    printer = relationship("Printer", back_populates="print_jobs")
    order = relationship("Order", back_populates="print_jobs")
    
    @property
    def estimated_completion_time(self):
        """
        Get the estimated completion time.
        
        Returns:
            datetime: The estimated completion time.
        """
        if self.started_at and self.estimated_print_time:
            return self.started_at + datetime.timedelta(minutes=self.estimated_print_time)
        return None
    
    def __repr__(self):
        return f"<PrintJob {self.job_name}>"
