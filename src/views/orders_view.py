"""
Orders view for the application.
"""
import os
import sys
import logging
import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QDialog, QLineEdit, QFormLayout,
    QComboBox, QMessageBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QDateEdit, QCheckBox
)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QDate
from PySide6.QtGui import QIcon, QFont, QColor, QPainter

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal
from models import (
    Order, OrderItem, OrderStatus, PaymentStatus, 
    Customer, SalesChannel, PrintJob, PrintJobStatus
)
import config


class OrderDetailsDialog(QDialog):
    """
    Dialog for viewing and editing order details.
    """
    def __init__(self, order=None, parent=None):
        super().__init__(parent)
        
        self.order = order
        self.is_edit_mode = order is not None
        
        self.setWindowTitle(f"{'Edit' if self.is_edit_mode else 'Add'} Order")
        self.setMinimumSize(700, 600)
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_order_data()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Order number
        self.order_number_input = QLineEdit()
        if not self.is_edit_mode:
            # Generate a new order number
            today = datetime.date.today()
            self.order_number_input.setText(f"ORD-{today.year}-{today.month:02d}{today.day:02d}-")
        
        form_layout.addRow("Order Number:", self.order_number_input)
        
        # Customer
        self.customer_combo = QComboBox()
        self.load_customers()
        form_layout.addRow("Customer:", self.customer_combo)
        
        # Sales channel
        self.sales_channel_combo = QComboBox()
        self.load_sales_channels()
        form_layout.addRow("Sales Channel:", self.sales_channel_combo)
        
        # Order date
        self.order_date_input = QDateEdit()
        self.order_date_input.setCalendarPopup(True)
        self.order_date_input.setDate(QDate.currentDate())
        form_layout.addRow("Order Date:", self.order_date_input)
        
        # Status
        self.status_combo = QComboBox()
        for status in OrderStatus:
            self.status_combo.addItem(status.value.capitalize(), status)
        form_layout.addRow("Status:", self.status_combo)
        
        # Payment status
        self.payment_status_combo = QComboBox()
        for status in PaymentStatus:
            self.payment_status_combo.addItem(status.value.capitalize(), status)
        form_layout.addRow("Payment Status:", self.payment_status_combo)
        
        # Total amount
        self.total_amount_input = QDoubleSpinBox()
        self.total_amount_input.setRange(0, 10000)
        self.total_amount_input.setPrefix("$")
        self.total_amount_input.setDecimals(2)
        form_layout.addRow("Total Amount:", self.total_amount_input)
        
        # Tax amount
        self.tax_amount_input = QDoubleSpinBox()
        self.tax_amount_input.setRange(0, 1000)
        self.tax_amount_input.setPrefix("$")
        self.tax_amount_input.setDecimals(2)
        form_layout.addRow("Tax Amount:", self.tax_amount_input)
        
        # Shipping amount
        self.shipping_amount_input = QDoubleSpinBox()
        self.shipping_amount_input.setRange(0, 1000)
        self.shipping_amount_input.setPrefix("$")
        self.shipping_amount_input.setDecimals(2)
        form_layout.addRow("Shipping Amount:", self.shipping_amount_input)
        
        # Discount amount
        self.discount_amount_input = QDoubleSpinBox()
        self.discount_amount_input.setRange(0, 1000)
        self.discount_amount_input.setPrefix("$")
        self.discount_amount_input.setDecimals(2)
        form_layout.addRow("Discount Amount:", self.discount_amount_input)
        
        # Shipping address
        self.shipping_address_line1_input = QLineEdit()
        form_layout.addRow("Shipping Address Line 1:", self.shipping_address_line1_input)
        
        self.shipping_address_line2_input = QLineEdit()
        form_layout.addRow("Shipping Address Line 2:", self.shipping_address_line2_input)
        
        self.shipping_city_input = QLineEdit()
        form_layout.addRow("Shipping City:", self.shipping_city_input)
        
        self.shipping_state_province_input = QLineEdit()
        form_layout.addRow("Shipping State/Province:", self.shipping_state_province_input)
        
        self.shipping_postal_code_input = QLineEdit()
        form_layout.addRow("Shipping Postal Code:", self.shipping_postal_code_input)
        
        self.shipping_country_input = QLineEdit()
        form_layout.addRow("Shipping Country:", self.shipping_country_input)
        
        # Tracking information
        self.tracking_number_input = QLineEdit()
        form_layout.addRow("Tracking Number:", self.tracking_number_input)
        
        self.shipping_carrier_input = QLineEdit()
        form_layout.addRow("Shipping Carrier:", self.shipping_carrier_input)
        
        # Flags
        flags_layout = QHBoxLayout()
        
        self.invoice_generated_check = QCheckBox("Invoice Generated")
        flags_layout.addWidget(self.invoice_generated_check)
        
        self.shipping_label_generated_check = QCheckBox("Shipping Label Generated")
        flags_layout.addWidget(self.shipping_label_generated_check)
        
        form_layout.addRow("Flags:", flags_layout)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_input)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self.save_order)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def load_customers(self):
        """
        Load customers into the combo box.
        """
        try:
            db = SessionLocal()
            customers = db.query(Customer).order_by(Customer.first_name, Customer.last_name).all()
            
            for customer in customers:
                self.customer_combo.addItem(
                    f"{customer.first_name} {customer.last_name} ({customer.email})",
                    customer.id
                )
        except Exception as e:
            logging.error(f"Error loading customers: {str(e)}")
        finally:
            db.close()
    
    def load_sales_channels(self):
        """
        Load sales channels into the combo box.
        """
        try:
            db = SessionLocal()
            sales_channels = db.query(SalesChannel).order_by(SalesChannel.name).all()
            
            for channel in sales_channels:
                self.sales_channel_combo.addItem(channel.name, channel.id)
        except Exception as e:
            logging.error(f"Error loading sales channels: {str(e)}")
        finally:
            db.close()
    
    def load_order_data(self):
        """
        Load order data into the form.
        """
        if not self.order:
            return
        
        self.order_number_input.setText(self.order.order_number)
        
        # Set customer
        customer_index = self.customer_combo.findData(self.order.customer_id)
        if customer_index >= 0:
            self.customer_combo.setCurrentIndex(customer_index)
        
        # Set sales channel
        if self.order.sales_channel_id:
            channel_index = self.sales_channel_combo.findData(self.order.sales_channel_id)
            if channel_index >= 0:
                self.sales_channel_combo.setCurrentIndex(channel_index)
        
        # Set order date
        self.order_date_input.setDate(QDate(
            self.order.order_date.year,
            self.order.order_date.month,
            self.order.order_date.day
        ))
        
        # Set status
        status_index = self.status_combo.findData(self.order.status)
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)
        
        # Set payment status
        payment_status_index = self.payment_status_combo.findData(self.order.payment_status)
        if payment_status_index >= 0:
            self.payment_status_combo.setCurrentIndex(payment_status_index)
        
        # Set amounts
        self.total_amount_input.setValue(self.order.total_amount)
        self.tax_amount_input.setValue(self.order.tax_amount)
        self.shipping_amount_input.setValue(self.order.shipping_amount)
        self.discount_amount_input.setValue(self.order.discount_amount)
        
        # Set shipping address
        if self.order.shipping_address_line1:
            self.shipping_address_line1_input.setText(self.order.shipping_address_line1)
        
        if self.order.shipping_address_line2:
            self.shipping_address_line2_input.setText(self.order.shipping_address_line2)
        
        if self.order.shipping_city:
            self.shipping_city_input.setText(self.order.shipping_city)
        
        if self.order.shipping_state_province:
            self.shipping_state_province_input.setText(self.order.shipping_state_province)
        
        if self.order.shipping_postal_code:
            self.shipping_postal_code_input.setText(self.order.shipping_postal_code)
        
        if self.order.shipping_country:
            self.shipping_country_input.setText(self.order.shipping_country)
        
        # Set tracking information
        if self.order.tracking_number:
            self.tracking_number_input.setText(self.order.tracking_number)
        
        if self.order.shipping_carrier:
            self.shipping_carrier_input.setText(self.order.shipping_carrier)
        
        # Set flags
        self.invoice_generated_check.setChecked(self.order.invoice_generated)
        self.shipping_label_generated_check.setChecked(self.order.shipping_label_generated)
        
        # Set notes
        if self.order.notes:
            self.notes_input.setText(self.order.notes)
    
    def save_order(self):
        """
        Save the order data.
        """
        # Validate required fields
        order_number = self.order_number_input.text().strip()
        
        if not order_number:
            QMessageBox.warning(self, "Validation Error", "Order number is required.")
            return
        
        customer_id = self.customer_combo.currentData()
        if customer_id is None:
            QMessageBox.warning(self, "Validation Error", "Customer is required.")
            return
        
        try:
            db = SessionLocal()
            
            # Check if order number is already in use
            existing_order = db.query(Order).filter(Order.order_number == order_number).first()
            if existing_order and (not self.is_edit_mode or existing_order.id != self.order.id):
                QMessageBox.warning(self, "Validation Error", "Order number is already in use.")
                return
            
            if self.is_edit_mode:
                # Update existing order
                order = db.query(Order).filter(Order.id == self.order.id).first()
                if not order:
                    QMessageBox.warning(self, "Error", "Order not found.")
                    return
            else:
                # Create new order
                order = Order()
                order.created_at = datetime.datetime.utcnow()
                db.add(order)
            
            # Update order data
            order.order_number = order_number
            order.customer_id = customer_id
            order.sales_channel_id = self.sales_channel_combo.currentData()
            
            # Get order date
            qdate = self.order_date_input.date()
            order.order_date = datetime.datetime(qdate.year(), qdate.month(), qdate.day())
            
            order.status = self.status_combo.currentData()
            order.payment_status = self.payment_status_combo.currentData()
            order.total_amount = self.total_amount_input.value()
            order.tax_amount = self.tax_amount_input.value()
            order.shipping_amount = self.shipping_amount_input.value()
            order.discount_amount = self.discount_amount_input.value()
            
            order.shipping_address_line1 = self.shipping_address_line1_input.text().strip() or None
            order.shipping_address_line2 = self.shipping_address_line2_input.text().strip() or None
            order.shipping_city = self.shipping_city_input.text().strip() or None
            order.shipping_state_province = self.shipping_state_province_input.text().strip() or None
            order.shipping_postal_code = self.shipping_postal_code_input.text().strip() or None
            order.shipping_country = self.shipping_country_input.text().strip() or None
            
            order.tracking_number = self.tracking_number_input.text().strip() or None
            order.shipping_carrier = self.shipping_carrier_input.text().strip() or None
            
            order.invoice_generated = self.invoice_generated_check.isChecked()
            order.shipping_label_generated = self.shipping_label_generated_check.isChecked()
            
            order.notes = self.notes_input.toPlainText().strip() or None
            
            # Update timestamps
            if order.status == OrderStatus.SHIPPED and not order.shipped_at:
                order.shipped_at = datetime.datetime.utcnow()
            
            if order.status == OrderStatus.DELIVERED and not order.delivered_at:
                order.delivered_at = datetime.datetime.utcnow()
            
            order.updated_at = datetime.datetime.utcnow()
            
            db.commit()
            
            logging.info(f"Order {order.order_number} {'updated' if self.is_edit_mode else 'created'}")
            
            self.accept()
        except Exception as e:
            logging.error(f"Error saving order: {str(e)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
        finally:
            db.close()


class OrdersView(QWidget):
    """
    Orders view for the application.
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
        
        header_title = QLabel("Orders")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search orders...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_orders)
        
        search_layout.addWidget(self.search_input)
        
        # Filter by status
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses", None)
        for status in OrderStatus:
            self.status_filter.addItem(status.value.capitalize(), status)
        
        self.status_filter.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(src/resources/icons/dropdown.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                selection-background-color: #3B82F6;
            }
        """)
        self.status_filter.currentIndexChanged.connect(self.refresh_data)
        
        # Add order button
        self.add_btn = QPushButton("Add Order")
        self.add_btn.setIcon(QIcon("src/resources/icons/add.png"))
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
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
        self.add_btn.clicked.connect(self.add_order)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addLayout(search_layout)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.status_filter)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(header_layout)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(8)
        self.orders_table.setHorizontalHeaderLabels([
            "Order #", "Customer", "Date", "Status", "Payment", "Total", "Items", "Actions"
        ])
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
        
        main_layout.addWidget(self.orders_table)
        
        # Order details
        details_frame = QFrame()
        details_frame.setObjectName("detailsFrame")
        details_frame.setStyleSheet("""
            #detailsFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(15, 15, 15, 15)
        details_layout.setSpacing(10)
        
        details_header = QHBoxLayout()
        details_title = QLabel("Order Details")
        details_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        details_header.addWidget(details_title)
        details_header.addStretch()
        
        details_layout.addLayout(details_header)
        
        # Order details content
        details_content = QLabel("Select an order to view details")
        details_content.setAlignment(Qt.AlignCenter)
        details_content.setStyleSheet("color: #94A3B8; font-size: 14px;")
        
        details_layout.addWidget(details_content)
        
        main_layout.addWidget(details_frame)
    
    def refresh_data(self):
        """
        Refresh the orders data.
        """
        try:
            # Get orders based on filter
            query = self.db.query(Order).order_by(Order.order_date.desc())
            
            # Apply status filter if selected
            status_filter = self.status_filter.currentData()
            if status_filter:
                query = query.filter(Order.status == status_filter)
            
            orders = query.all()
            
            # Populate orders table
            self.orders_table.setRowCount(len(orders))
            
            # Set row height for better icon visibility
            for i in range(len(orders)):
                self.orders_table.setRowHeight(i, 40)
                
            for i, order in enumerate(orders):
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
                
                # Status
                status_item = QTableWidgetItem(order.status.value.capitalize())
                self.orders_table.setItem(i, 3, status_item)
                
                # Payment status
                payment_item = QTableWidgetItem(order.payment_status.value.capitalize())
                self.orders_table.setItem(i, 4, payment_item)
                
                # Total
                total_item = QTableWidgetItem(f"${order.total_amount:.2f}")
                self.orders_table.setItem(i, 5, total_item)
                
                # Items count
                items_count = len(order.items) if order.items else 0
                items_item = QTableWidgetItem(str(items_count))
                self.orders_table.setItem(i, 6, items_item)
                
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
                view_btn.setToolTip("View Order")
                
                # Edit button
                edit_btn = QPushButton()
                edit_btn.setIcon(QIcon("src/resources/icons/edit.png"))
                edit_btn.setIconSize(QSize(16, 16))
                edit_btn.setFixedSize(30, 30)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                edit_btn.setToolTip("Edit Order")
                edit_btn.clicked.connect(lambda checked, o=order: self.edit_order(o))
                
                # Print invoice button
                invoice_btn = QPushButton()
                invoice_btn.setIcon(QIcon("src/resources/icons/invoice.png"))
                invoice_btn.setIconSize(QSize(16, 16))
                invoice_btn.setFixedSize(30, 30)
                invoice_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                invoice_btn.setToolTip("Print Invoice")
                
                # Print shipping label button
                shipping_btn = QPushButton()
                shipping_btn.setIcon(QIcon("src/resources/icons/shipping.png"))
                shipping_btn.setIconSize(QSize(16, 16))
                shipping_btn.setFixedSize(30, 30)
                shipping_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                shipping_btn.setToolTip("Print Shipping Label")
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(invoice_btn)
                actions_layout.addWidget(shipping_btn)
                actions_layout.addStretch()
                
                self.orders_table.setCellWidget(i, 7, actions_widget)
            
            logging.info("Orders view refreshed")
        except Exception as e:
            logging.error(f"Error refreshing orders data: {str(e)}")
    
    def filter_orders(self):
        """
        Filter orders based on search text.
        """
        search_text = self.search_input.text().lower()
        
        for i in range(self.orders_table.rowCount()):
            row_hidden = True
            
            # Check if search text is in any of the first 5 columns
            for j in range(5):
                item = self.orders_table.item(i, j)
                if item and search_text in item.text().lower():
                    row_hidden = False
                    break
            
            self.orders_table.setRowHidden(i, row_hidden)
    
    def add_order(self):
        """
        Open the add order dialog.
        """
        dialog = OrderDetailsDialog(parent=self)
        if dialog.exec():
            # Refresh the view to show the new order
            self.refresh_data()
    
    def edit_order(self, order):
        """
        Open the edit order dialog.
        """
        dialog = OrderDetailsDialog(order, self)
        if dialog.exec():
            # Refresh the view to show the updated order
            self.refresh_data()
