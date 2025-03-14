"""
Database initialization module for the application.
"""
import os
import sys
import logging
import datetime
import bcrypt

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal, init_db
from models import (
    User, Printer, Customer, SalesChannel, Order, OrderItem, 
    PrintJob, CustomerEmail, PrinterStatus, OrderStatus, 
    PaymentStatus, PrintJobStatus, EmailStatus
)
import config


def setup_database():
    """
    Set up the database with initial data.
    """
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(config.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Create admin user if it doesn't exist
    create_admin_user()
    
    # Create demo data if enabled
    if config.CREATE_DEMO_DATA:
        create_demo_data()


def create_admin_user():
    """
    Create admin user if it doesn't exist.
    """
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == config.ADMIN_USERNAME).first()
        
        if not admin_user:
            # Create admin user
            hashed_password = bcrypt.hashpw(
                config.ADMIN_PASSWORD.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            admin_user = User(
                username=config.ADMIN_USERNAME,
                email=config.ADMIN_EMAIL,
                full_name="Administrator",
                hashed_password=hashed_password,
                is_admin=True,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            
            db.add(admin_user)
            db.commit()
            
            logging.info(f"Admin user '{config.ADMIN_USERNAME}' created")
        else:
            logging.info(f"Admin user '{config.ADMIN_USERNAME}' already exists")
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating admin user: {str(e)}")
    finally:
        db.close()


def create_demo_data():
    """
    Create demo data for the application.
    """
    db = SessionLocal()
    try:
        # Check if demo data already exists
        if db.query(Printer).count() > 0:
            logging.info("Demo data already exists")
            return
        
        # Create demo printers
        printers = [
            Printer(
                name="Prusa i3 MK3S+",
                model="i3 MK3S+",
                manufacturer="Prusa Research",
                build_volume_x=250,
                build_volume_y=210,
                build_volume_z=210,
                status=PrinterStatus.IDLE,
                ip_address="192.168.1.101",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            ),
            Printer(
                name="Creality Ender 3 Pro",
                model="Ender 3 Pro",
                manufacturer="Creality",
                build_volume_x=220,
                build_volume_y=220,
                build_volume_z=250,
                status=PrinterStatus.IDLE,
                ip_address="192.168.1.102",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            ),
            Printer(
                name="Ultimaker S5",
                model="S5",
                manufacturer="Ultimaker",
                build_volume_x=330,
                build_volume_y=240,
                build_volume_z=300,
                status=PrinterStatus.MAINTENANCE,
                ip_address="192.168.1.103",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            ),
            Printer(
                name="Formlabs Form 3",
                model="Form 3",
                manufacturer="Formlabs",
                build_volume_x=145,
                build_volume_y=145,
                build_volume_z=185,
                status=PrinterStatus.PRINTING,
                ip_address="192.168.1.104",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
        ]
        
        db.add_all(printers)
        db.commit()
        
        # Create demo customers
        customers = [
            Customer(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="555-123-4567",
                address_line1="123 Main St",
                city="Anytown",
                state_province="CA",
                postal_code="12345",
                country="USA",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            ),
            Customer(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone="555-987-6543",
                address_line1="456 Oak Ave",
                address_line2="Apt 7B",
                city="Somewhere",
                state_province="NY",
                postal_code="67890",
                country="USA",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            ),
            Customer(
                first_name="Robert",
                last_name="Johnson",
                email="robert.johnson@example.com",
                phone="555-456-7890",
                address_line1="789 Pine Rd",
                city="Elsewhere",
                state_province="TX",
                postal_code="54321",
                country="USA",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
        ]
        
        db.add_all(customers)
        db.commit()
        
        # Create demo sales channels
        sales_channels = [
            SalesChannel(
                name="Website",
                website_url="https://www.novamodelisshop.com",
                commission_rate=0.0,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            ),
            SalesChannel(
                name="Etsy",
                website_url="https://www.etsy.com/shop/novamodelisshop",
                commission_rate=6.5,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            ),
            SalesChannel(
                name="Amazon Handmade",
                website_url="https://www.amazon.com/handmade/novamodelisshop",
                commission_rate=15.0,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
        ]
        
        db.add_all(sales_channels)
        db.commit()
        
        # Create demo orders
        orders = [
            Order(
                order_number="ORD-2025-0001",
                customer_id=1,
                sales_channel_id=1,
                order_date=datetime.datetime.utcnow() - datetime.timedelta(days=5),
                status=OrderStatus.DELIVERED,
                payment_status=PaymentStatus.PAID,
                total_amount=125.99,
                tax_amount=10.50,
                shipping_amount=8.99,
                discount_amount=0.0,
                shipping_address_line1="123 Main St",
                shipping_city="Anytown",
                shipping_state_province="CA",
                shipping_postal_code="12345",
                shipping_country="USA",
                tracking_number="1Z999AA10123456784",
                shipping_carrier="UPS",
                invoice_generated=True,
                shipping_label_generated=True,
                shipped_at=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                delivered_at=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=5),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            ),
            Order(
                order_number="ORD-2025-0002",
                customer_id=2,
                sales_channel_id=2,
                order_date=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                status=OrderStatus.PRINTING,
                payment_status=PaymentStatus.PAID,
                total_amount=89.95,
                tax_amount=7.50,
                shipping_amount=5.99,
                discount_amount=10.0,
                shipping_address_line1="456 Oak Ave",
                shipping_address_line2="Apt 7B",
                shipping_city="Somewhere",
                shipping_state_province="NY",
                shipping_postal_code="67890",
                shipping_country="USA",
                invoice_generated=True,
                shipping_label_generated=False,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
            ),
            Order(
                order_number="ORD-2025-0003",
                customer_id=3,
                sales_channel_id=3,
                order_date=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                status=OrderStatus.NEW,
                payment_status=PaymentStatus.PENDING,
                total_amount=149.99,
                tax_amount=12.50,
                shipping_amount=0.0,  # Free shipping
                discount_amount=0.0,
                shipping_address_line1="789 Pine Rd",
                shipping_city="Elsewhere",
                shipping_state_province="TX",
                shipping_postal_code="54321",
                shipping_country="USA",
                invoice_generated=False,
                shipping_label_generated=False,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            )
        ]
        
        db.add_all(orders)
        db.commit()
        
        # Create demo order items
        order_items = [
            OrderItem(
                order_id=1,
                product_name="Custom Miniature Figure",
                product_sku="MIN-001",
                quantity=1,
                unit_price=125.99,
                total_price=125.99,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=5),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=5)
            ),
            OrderItem(
                order_id=2,
                product_name="Architectural Model",
                product_sku="ARC-002",
                quantity=1,
                unit_price=89.95,
                total_price=89.95,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
            ),
            OrderItem(
                order_id=3,
                product_name="Custom Jewelry Piece",
                product_sku="JWL-003",
                quantity=1,
                unit_price=149.99,
                total_price=149.99,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            )
        ]
        
        db.add_all(order_items)
        db.commit()
        
        # Create demo print jobs
        print_jobs = [
            PrintJob(
                job_name="Miniature Figure - John Doe",
                printer_id=1,
                order_id=1,
                file_path="/models/miniature_figure_001.stl",
                material="PLA",
                color="Gray",
                layer_height=0.1,
                infill_percentage=20,
                status=PrintJobStatus.COMPLETED,
                estimated_print_time=180,  # 3 hours
                actual_print_time=195,  # 3 hours 15 minutes
                started_at=datetime.datetime.utcnow() - datetime.timedelta(days=4, hours=5),
                completed_at=datetime.datetime.utcnow() - datetime.timedelta(days=4, hours=2),
                progress=100.0,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=5),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=4)
            ),
            PrintJob(
                job_name="Architectural Model - Jane Smith",
                printer_id=4,
                order_id=2,
                file_path="/models/architectural_model_002.stl",
                material="Resin",
                color="White",
                layer_height=0.05,
                infill_percentage=50,
                status=PrintJobStatus.PRINTING,
                estimated_print_time=360,  # 6 hours
                started_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
                progress=33.3,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=2),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            )
        ]
        
        db.add_all(print_jobs)
        db.commit()
        
        # Create demo customer emails
        customer_emails = [
            CustomerEmail(
                customer_id=1,
                subject="Order Confirmation - ORD-2025-0001",
                body="Thank you for your order! We'll notify you when your item ships.",
                is_incoming=False,
                status=EmailStatus.SENT,
                received_at=datetime.datetime.utcnow() - datetime.timedelta(days=5),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=5),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=5)
            ),
            CustomerEmail(
                customer_id=1,
                subject="Shipping Notification - ORD-2025-0001",
                body="Your order has shipped! Tracking number: 1Z999AA10123456784",
                is_incoming=False,
                status=EmailStatus.SENT,
                received_at=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
            ),
            CustomerEmail(
                customer_id=1,
                subject="Re: Shipping Notification - ORD-2025-0001",
                body="Thank you for the update! Looking forward to receiving my order.",
                is_incoming=True,
                status=EmailStatus.READ,
                received_at=datetime.datetime.utcnow() - datetime.timedelta(days=3, hours=2),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=3, hours=2),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=3, hours=1)
            ),
            CustomerEmail(
                customer_id=2,
                subject="Order Confirmation - ORD-2025-0002",
                body="Thank you for your order! We'll notify you when your item ships.",
                is_incoming=False,
                status=EmailStatus.SENT,
                received_at=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
            ),
            CustomerEmail(
                customer_id=2,
                subject="Question about my order",
                body="Hi, I was wondering if I could get an update on when my order will be ready? Thanks!",
                is_incoming=True,
                status=EmailStatus.UNREAD,
                received_at=datetime.datetime.utcnow() - datetime.timedelta(hours=5),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=5),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(hours=5)
            ),
            CustomerEmail(
                customer_id=3,
                subject="Order Confirmation - ORD-2025-0003",
                body="Thank you for your order! We'll notify you when your item ships.",
                is_incoming=False,
                status=EmailStatus.SENT,
                received_at=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            ),
            CustomerEmail(
                customer_id=3,
                subject="Custom design request",
                body="Hello, I'd like to discuss some customizations for my jewelry piece. Can we schedule a call?",
                is_incoming=True,
                status=EmailStatus.UNREAD,
                received_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            )
        ]
        
        db.add_all(customer_emails)
        db.commit()
        
        logging.info("Demo data created successfully")
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating demo data: {str(e)}")
    finally:
        db.close()
