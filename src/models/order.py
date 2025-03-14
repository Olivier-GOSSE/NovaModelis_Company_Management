"""
Order models for the application.
"""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base
from models import OrderStatus, PaymentStatus


class Order(Base):
    """
    Order model.
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sales_channel_id = Column(Integer, ForeignKey("sales_channels.id"), nullable=True)
    order_date = Column(DateTime, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.NEW, nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    tax_amount = Column(Float, default=0.0, nullable=False)
    shipping_amount = Column(Float, default=0.0, nullable=False)
    discount_amount = Column(Float, default=0.0, nullable=False)
    shipping_address_line1 = Column(String(100), nullable=True)
    shipping_address_line2 = Column(String(100), nullable=True)
    shipping_city = Column(String(50), nullable=True)
    shipping_state_province = Column(String(50), nullable=True)
    shipping_postal_code = Column(String(20), nullable=True)
    shipping_country = Column(String(50), nullable=True)
    tracking_number = Column(String(100), nullable=True)
    shipping_carrier = Column(String(50), nullable=True)
    invoice_generated = Column(Boolean, default=False, nullable=False)
    shipping_label_generated = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    sales_channel = relationship("SalesChannel", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    print_jobs = relationship("PrintJob", back_populates="order")
    
    def __repr__(self):
        return f"<Order {self.order_number}>"


class OrderItem(Base):
    """
    Order item model.
    """
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_name = Column(String(100), nullable=False)
    product_sku = Column(String(50), nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    
    def __repr__(self):
        return f"<OrderItem {self.product_name}>"
