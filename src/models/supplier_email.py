"""
Supplier email model for the application.
"""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base
from models import EmailStatus


class SupplierEmail(Base):
    """
    Supplier email model.
    """
    __tablename__ = "supplier_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    is_incoming = Column(Boolean, default=False, nullable=False)
    status = Column(Enum(EmailStatus), default=EmailStatus.UNREAD, nullable=False)
    received_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="emails")
    
    def __repr__(self):
        return f"<SupplierEmail {self.subject}>"
