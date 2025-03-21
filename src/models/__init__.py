"""
Models package initialization.
"""
from enum import Enum, auto

# Enums
class PrinterStatus(Enum):
    """
    Printer status enum.
    """
    IDLE = "idle"
    PRINTING = "printing"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    ERROR = "error"


class OrderStatus(Enum):
    """
    Order status enum.
    """
    NEW = "new"
    PROCESSING = "processing"
    PRINTING = "printing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(Enum):
    """
    Payment status enum.
    """
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PrintJobStatus(Enum):
    """
    Print job status enum.
    """
    QUEUED = "queued"
    PRINTING = "printing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EmailStatus(Enum):
    """
    Email status enum.
    """
    UNREAD = "unread"
    READ = "read"
    SENT = "sent"
    DRAFT = "draft"


# Import models
from .user import User
from .printer import Printer
from .customer import Customer
from .sales_channel import SalesChannel
from .order import Order, OrderItem
from .print_job import PrintJob
from .customer_email import CustomerEmail
from .supplier import Supplier
from .supplier_email import SupplierEmail
from .raw_material import RawMaterial

# Export all models
__all__ = [
    "User",
    "Printer",
    "Customer",
    "SalesChannel",
    "Order",
    "OrderItem",
    "PrintJob",
    "CustomerEmail",
    "Supplier",
    "SupplierEmail",
    "RawMaterial",
    "PrinterStatus",
    "OrderStatus",
    "PaymentStatus",
    "PrintJobStatus",
    "EmailStatus"
]
