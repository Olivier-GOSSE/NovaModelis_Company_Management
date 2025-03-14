"""
Dashboard view for the application.
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QColor, QPainter
from sqlalchemy import func

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from models import (
    Order, OrderStatus, PaymentStatus, PrintJob, PrintJobStatus, 
    Customer, CustomerEmail, EmailStatus, Printer
)
import config


class StatCard(QFrame):
    """
    Stat card widget for displaying statistics.
    """
    def __init__(self, title, value, icon_path, color="#3B82F6"):
        super().__init__()
        
        self.setObjectName("statCard")
        self.setStyleSheet(f"""
            #statCard {{
                background-color: #1E293B;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(32, 32)))
        
        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #94A3B8; font-size: 14px;")
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet("color: #F8FAFC; font-size: 24px; font-weight: bold;")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        
        # Add widgets to layout
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()


class DashboardView(QWidget):
    """
    Dashboard view for the application.
    """
    def __init__(self, db):
        super().__init__()
        
        self.db = db
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_title = QLabel("Dashboard")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(QIcon("src/resources/icons/refresh.png"))
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Create stat cards (will be populated in refresh_data)
        self.orders_card = StatCard("Total Orders", "0", "src/resources/icons/order.png")
        self.revenue_card = StatCard("Total Revenue", "$0", "src/resources/icons/revenue.png", "#10B981")
        self.customers_card = StatCard("Total Customers", "0", "src/resources/icons/customer.png", "#F59E0B")
        self.printers_card = StatCard("Active Printers", "0", "src/resources/icons/printer.png", "#EF4444")
        
        stats_layout.addWidget(self.orders_card)
        stats_layout.addWidget(self.revenue_card)
        stats_layout.addWidget(self.customers_card)
        stats_layout.addWidget(self.printers_card)
        
        main_layout.addLayout(stats_layout)
        
        # Content grid
        content_layout = QGridLayout()
        content_layout.setSpacing(15)
        
        # Recent orders
        orders_frame = QFrame()
        orders_frame.setObjectName("ordersFrame")
        orders_frame.setStyleSheet("""
            #ordersFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        orders_layout = QVBoxLayout(orders_frame)
        orders_layout.setContentsMargins(15, 15, 15, 15)
        orders_layout.setSpacing(10)
        
        orders_header = QHBoxLayout()
        orders_title = QLabel("Recent Orders")
        orders_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        view_all_orders = QPushButton("View All")
        view_all_orders.setCursor(Qt.PointingHandCursor)
        view_all_orders.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3B82F6;
                border: none;
            }
            QPushButton:hover {
                color: #2563EB;
            }
        """)
        
        orders_header.addWidget(orders_title)
        orders_header.addStretch()
        orders_header.addWidget(view_all_orders)
        
        orders_layout.addLayout(orders_header)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Order #", "Customer", "Date", "Amount", "Status"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E293B;
                border-radius: 8px;
                border: none;
                gridline-color: #334155;
            }
            QHeaderView::section {
                background-color: #0F172A;
                color: #94A3B8;
                border: none;
                padding: 5px;
            }
            QTableWidget::item {
                color: #F8FAFC;
                border: none;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #334155;
            }
        """)
        
        orders_layout.addWidget(self.orders_table)
        
        # Active print jobs
        jobs_frame = QFrame()
        jobs_frame.setObjectName("jobsFrame")
        jobs_frame.setStyleSheet("""
            #jobsFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        jobs_layout = QVBoxLayout(jobs_frame)
        jobs_layout.setContentsMargins(15, 15, 15, 15)
        jobs_layout.setSpacing(10)
        
        jobs_header = QHBoxLayout()
        jobs_title = QLabel("Active Print Jobs")
        jobs_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        view_all_jobs = QPushButton("View All")
        view_all_jobs.setCursor(Qt.PointingHandCursor)
        view_all_jobs.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3B82F6;
                border: none;
            }
            QPushButton:hover {
                color: #2563EB;
            }
        """)
        
        jobs_header.addWidget(jobs_title)
        jobs_header.addStretch()
        jobs_header.addWidget(view_all_jobs)
        
        jobs_layout.addLayout(jobs_header)
        
        # Jobs table
        self.jobs_table = QTableWidget()
        self.jobs_table.setColumnCount(5)
        self.jobs_table.setHorizontalHeaderLabels(["Job Name", "Printer", "Started", "Progress", "Est. Completion"])
        self.jobs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.jobs_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.jobs_table.verticalHeader().setVisible(False)
        self.jobs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.jobs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.jobs_table.setAlternatingRowColors(True)
        self.jobs_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E293B;
                border-radius: 8px;
                border: none;
                gridline-color: #334155;
            }
            QHeaderView::section {
                background-color: #0F172A;
                color: #94A3B8;
                border: none;
                padding: 5px;
            }
            QTableWidget::item {
                color: #F8FAFC;
                border: none;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #334155;
            }
        """)
        
        jobs_layout.addWidget(self.jobs_table)
        
        # Unread messages
        messages_frame = QFrame()
        messages_frame.setObjectName("messagesFrame")
        messages_frame.setStyleSheet("""
            #messagesFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        messages_layout = QVBoxLayout(messages_frame)
        messages_layout.setContentsMargins(15, 15, 15, 15)
        messages_layout.setSpacing(10)
        
        messages_header = QHBoxLayout()
        messages_title = QLabel("Unread Messages")
        messages_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        view_all_messages = QPushButton("View All")
        view_all_messages.setCursor(Qt.PointingHandCursor)
        view_all_messages.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3B82F6;
                border: none;
            }
            QPushButton:hover {
                color: #2563EB;
            }
        """)
        
        messages_header.addWidget(messages_title)
        messages_header.addStretch()
        messages_header.addWidget(view_all_messages)
        
        messages_layout.addLayout(messages_header)
        
        # Messages table
        self.messages_table = QTableWidget()
        self.messages_table.setColumnCount(4)
        self.messages_table.setHorizontalHeaderLabels(["From", "Subject", "Date", "Actions"])
        self.messages_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.messages_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.messages_table.verticalHeader().setVisible(False)
        self.messages_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.messages_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.messages_table.setAlternatingRowColors(True)
        self.messages_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E293B;
                border-radius: 8px;
                border: none;
                gridline-color: #334155;
            }
            QHeaderView::section {
                background-color: #0F172A;
                color: #94A3B8;
                border: none;
                padding: 5px;
            }
            QTableWidget::item {
                color: #F8FAFC;
                border: none;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #334155;
            }
        """)
        
        messages_layout.addWidget(self.messages_table)
        
        # Add widgets to content grid
        content_layout.addWidget(orders_frame, 0, 0)
        content_layout.addWidget(jobs_frame, 0, 1)
        content_layout.addWidget(messages_frame, 1, 0, 1, 2)
        
        main_layout.addLayout(content_layout)
    
    def refresh_data(self):
        """
        Refresh the dashboard data.
        """
        try:
            # Get statistics
            total_orders = self.db.query(Order).count()
            total_revenue = self.db.query(Order).filter(Order.payment_status == PaymentStatus.PAID).with_entities(
                func.sum(Order.total_amount)
            ).scalar() or 0
            total_customers = self.db.query(Customer).count()
            active_printers = self.db.query(PrintJob).filter(PrintJob.status == PrintJobStatus.PRINTING).count()
            
            # Update stat cards
            self.orders_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(total_orders))
            self.revenue_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(f"${total_revenue:.2f}")
            self.customers_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(total_customers))
            self.printers_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(active_printers))
            
            # Get recent orders
            recent_orders = self.db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
            
            # Populate orders table
            self.orders_table.setRowCount(len(recent_orders))
            for i, order in enumerate(recent_orders):
                # Order number
                order_num_item = QTableWidgetItem(order.order_number)
                self.orders_table.setItem(i, 0, order_num_item)
                
                # Customer
                customer = self.db.query(Customer).filter(Customer.id == order.customer_id).first()
                customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Unknown"
                customer_item = QTableWidgetItem(customer_name)
                self.orders_table.setItem(i, 1, customer_item)
                
                # Date
                date_item = QTableWidgetItem(order.order_date.strftime("%d %b %Y"))
                self.orders_table.setItem(i, 2, date_item)
                
                # Amount
                amount_item = QTableWidgetItem(f"${order.total_amount:.2f}")
                self.orders_table.setItem(i, 3, amount_item)
                
                # Status
                status_item = QTableWidgetItem(order.status.value.capitalize())
                self.orders_table.setItem(i, 4, status_item)
            
            # Get active print jobs
            active_jobs = self.db.query(PrintJob).filter(PrintJob.status == PrintJobStatus.PRINTING).all()
            
            # Populate jobs table
            self.jobs_table.setRowCount(len(active_jobs))
            for i, job in enumerate(active_jobs):
                # Job name
                job_name_item = QTableWidgetItem(job.job_name)
                self.jobs_table.setItem(i, 0, job_name_item)
                
                # Printer
                printer = self.db.query(Printer).filter(Printer.id == job.printer_id).first()
                printer_name = printer.name if printer else "Unknown"
                printer_item = QTableWidgetItem(printer_name)
                self.jobs_table.setItem(i, 1, printer_item)
                
                # Started
                started_item = QTableWidgetItem(job.started_at.strftime("%d %b %Y %H:%M"))
                self.jobs_table.setItem(i, 2, started_item)
                
                # Progress
                progress_item = QTableWidgetItem(f"{job.progress:.1f}%")
                self.jobs_table.setItem(i, 3, progress_item)
                
                # Estimated completion
                est_completion = job.estimated_completion_time
                est_completion_text = est_completion.strftime("%d %b %Y %H:%M") if est_completion else "Unknown"
                est_completion_item = QTableWidgetItem(est_completion_text)
                self.jobs_table.setItem(i, 4, est_completion_item)
            
            # Get unread messages
            unread_messages = self.db.query(CustomerEmail).filter(
                CustomerEmail.is_incoming == True,
                CustomerEmail.status == EmailStatus.UNREAD
            ).order_by(CustomerEmail.received_at.desc()).all()
            
            # Populate messages table
            self.messages_table.setRowCount(len(unread_messages))
            for i, message in enumerate(unread_messages):
                # From
                customer = self.db.query(Customer).filter(Customer.id == message.customer_id).first()
                from_text = f"{customer.first_name} {customer.last_name}" if customer else "Unknown"
                from_item = QTableWidgetItem(from_text)
                self.messages_table.setItem(i, 0, from_item)
                
                # Subject
                subject_item = QTableWidgetItem(message.subject)
                self.messages_table.setItem(i, 1, subject_item)
                
                # Date
                date_item = QTableWidgetItem(message.received_at.strftime("%d %b %Y %H:%M"))
                self.messages_table.setItem(i, 2, date_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 0, 5, 0)
                actions_layout.setSpacing(5)
                
                # View button
                view_btn = QPushButton()
                view_btn.setIcon(QIcon("src/resources/icons/view.png"))
                view_btn.setIconSize(QSize(16, 16))
                view_btn.setFixedSize(30, 30)
                view_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                view_btn.setToolTip("View Message")
                
                # Reply button
                reply_btn = QPushButton()
                reply_btn.setIcon(QIcon("src/resources/icons/reply.png"))
                reply_btn.setIconSize(QSize(16, 16))
                reply_btn.setFixedSize(30, 30)
                reply_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                reply_btn.setToolTip("Reply")
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(reply_btn)
                actions_layout.addStretch()
                
                self.messages_table.setCellWidget(i, 3, actions_widget)
            
            logging.info("Dashboard data refreshed")
        except Exception as e:
            logging.error(f"Error refreshing dashboard data: {str(e)}")
