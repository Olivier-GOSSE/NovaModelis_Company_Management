"""
Customer email model for the application.
"""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base
from models import EmailStatus


class CustomerEmail(Base):
    """
    Customer email model.
    """
    __tablename__ = "customer_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    is_incoming = Column(Boolean, default=False, nullable=False)
    status = Column(Enum(EmailStatus), default=EmailStatus.UNREAD, nullable=False)
    received_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="emails")
    
    def __repr__(self):
        return f"<CustomerEmail {self.subject}>"
