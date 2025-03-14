"""
Customers view for the application.
"""
import os
import sys
import logging
import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QDialog, QLineEdit, QFormLayout,
    QComboBox, QMessageBox, QSpinBox, QDoubleSpinBox, QTextEdit
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QFont, QColor, QPainter

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal
from models import Customer, Order, CustomerEmail, EmailStatus
import config


class CustomerDetailsDialog(QDialog):
    """
    Dialog for viewing and editing customer details.
    """
    def __init__(self, customer=None, parent=None):
        super().__init__(parent)
        
        self.customer = customer
        self.is_edit_mode = customer is not None
        
        self.setWindowTitle(f"{'Modifier' if self.is_edit_mode else 'Ajouter'} Client")
        self.setMinimumSize(500, 600)
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_customer_data()
    
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
        
        # First name
        self.first_name_input = QLineEdit()
        form_layout.addRow("Prénom:", self.first_name_input)
        
        # Last name
        self.last_name_input = QLineEdit()
        form_layout.addRow("Nom:", self.last_name_input)
        
        # Email
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        form_layout.addRow("Téléphone:", self.phone_input)
        
        # Address line 1
        self.address_line1_input = QLineEdit()
        form_layout.addRow("Adresse ligne 1:", self.address_line1_input)
        
        # Address line 2
        self.address_line2_input = QLineEdit()
        form_layout.addRow("Adresse ligne 2:", self.address_line2_input)
        
        # City
        self.city_input = QLineEdit()
        form_layout.addRow("Ville:", self.city_input)
        
        # State/Province
        self.state_province_input = QLineEdit()
        form_layout.addRow("État/Province:", self.state_province_input)
        
        # Postal code
        self.postal_code_input = QLineEdit()
        form_layout.addRow("Code postal:", self.postal_code_input)
        
        # Country
        self.country_input = QLineEdit()
        form_layout.addRow("Pays:", self.country_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_input)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self.save_customer)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def load_customer_data(self):
        """
        Load customer data into the form.
        """
        if not self.customer:
            return
        
        self.first_name_input.setText(self.customer.first_name)
        self.last_name_input.setText(self.customer.last_name)
        self.email_input.setText(self.customer.email)
        
        if self.customer.phone:
            self.phone_input.setText(self.customer.phone)
        
        if self.customer.address_line1:
            self.address_line1_input.setText(self.customer.address_line1)
        
        if self.customer.address_line2:
            self.address_line2_input.setText(self.customer.address_line2)
        
        if self.customer.city:
            self.city_input.setText(self.customer.city)
        
        if self.customer.state_province:
            self.state_province_input.setText(self.customer.state_province)
        
        if self.customer.postal_code:
            self.postal_code_input.setText(self.customer.postal_code)
        
        if self.customer.country:
            self.country_input.setText(self.customer.country)
        
        if self.customer.notes:
            self.notes_input.setText(self.customer.notes)
    
    def save_customer(self):
        """
        Save the customer data.
        """
        # Validate required fields
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        
        if not first_name:
            QMessageBox.warning(self, "Erreur de validation", "Le prénom est requis.")
            return
        
        if not last_name:
            QMessageBox.warning(self, "Erreur de validation", "Le nom est requis.")
            return
        
        if not email:
            QMessageBox.warning(self, "Erreur de validation", "L'email est requis.")
            return
        
        try:
            db = SessionLocal()
            
            # Check if email is already in use
            existing_customer = db.query(Customer).filter(Customer.email == email).first()
            if existing_customer and (not self.is_edit_mode or existing_customer.id != self.customer.id):
                QMessageBox.warning(self, "Erreur de validation", "Cet email est déjà utilisé.")
                return
            
            if self.is_edit_mode:
                # Update existing customer
                customer = db.query(Customer).filter(Customer.id == self.customer.id).first()
                if not customer:
                    QMessageBox.warning(self, "Erreur", "Client non trouvé.")
                    return
            else:
                # Create new customer
                customer = Customer()
                customer.created_at = datetime.datetime.utcnow()
                db.add(customer)
            
            # Update customer data
            customer.first_name = first_name
            customer.last_name = last_name
            customer.email = email
            customer.phone = self.phone_input.text().strip() or None
            customer.address_line1 = self.address_line1_input.text().strip() or None
            customer.address_line2 = self.address_line2_input.text().strip() or None
            customer.city = self.city_input.text().strip() or None
            customer.state_province = self.state_province_input.text().strip() or None
            customer.postal_code = self.postal_code_input.text().strip() or None
            customer.country = self.country_input.text().strip() or None
            customer.notes = self.notes_input.toPlainText().strip() or None
            customer.updated_at = datetime.datetime.utcnow()
            
            db.commit()
            
            logging.info(f"Customer {customer.first_name} {customer.last_name} {'updated' if self.is_edit_mode else 'created'}")
            
            self.accept()
        except Exception as e:
            logging.error(f"Error saving customer: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            db.close()


class CustomersView(QWidget):
    """
    Customers view for the application.
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
        
        header_title = QLabel("Clients")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher des clients...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_customers)
        
        search_layout.addWidget(self.search_input)
        
        # Add customer button
        self.add_btn = QPushButton("Ajouter un client")
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
        self.add_btn.clicked.connect(self.add_customer)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addLayout(search_layout)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(header_layout)
        
        # Customers table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(7)
        self.customers_table.setHorizontalHeaderLabels([
            "Nom", "Email", "Téléphone", "Localisation", "Commandes", "Total dépensé", "Actions"
        ])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customers_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.customers_table.verticalHeader().setVisible(False)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.customers_table.setAlternatingRowColors(True)
        self.customers_table.setStyleSheet("""
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
        
        main_layout.addWidget(self.customers_table)
        
        # Recent messages
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
        messages_title = QLabel("Messages récents")
        messages_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        messages_header.addWidget(messages_title)
        messages_header.addStretch()
        
        messages_layout.addLayout(messages_header)
        
        # Messages table
        self.messages_table = QTableWidget()
        self.messages_table.setColumnCount(5)
        self.messages_table.setHorizontalHeaderLabels([
            "Client", "Sujet", "Date", "Statut", "Actions"
        ])
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
        
        main_layout.addWidget(messages_frame)
    
    def refresh_data(self):
        """
        Refresh the customers data.
        """
        try:
            # Get all customers
            customers = self.db.query(Customer).all()
            
            # Populate customers table
            self.customers_table.setRowCount(len(customers))
            for i, customer in enumerate(customers):
                # Name
                name_item = QTableWidgetItem(f"{customer.first_name} {customer.last_name}")
                self.customers_table.setItem(i, 0, name_item)
                
                # Email
                email_item = QTableWidgetItem(customer.email)
                self.customers_table.setItem(i, 1, email_item)
                
                # Phone
                phone_item = QTableWidgetItem(customer.phone or "")
                self.customers_table.setItem(i, 2, phone_item)
                
                # Location
                location_parts = []
                if customer.city:
                    location_parts.append(customer.city)
                if customer.state_province:
                    location_parts.append(customer.state_province)
                if customer.country:
                    location_parts.append(customer.country)
                
                location_text = ", ".join(location_parts) if location_parts else ""
                location_item = QTableWidgetItem(location_text)
                self.customers_table.setItem(i, 3, location_item)
                
                # Orders count
                orders_count = len(customer.orders) if customer.orders else 0
                orders_item = QTableWidgetItem(str(orders_count))
                self.customers_table.setItem(i, 4, orders_item)
                
                # Total spent
                total_spent = sum(order.total_amount for order in customer.orders) if customer.orders else 0
                total_spent_item = QTableWidgetItem(f"{total_spent:.2f} €")
                self.customers_table.setItem(i, 5, total_spent_item)
                
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
                view_btn.setToolTip("Voir le client")
                
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
                edit_btn.setToolTip("Modifier le client")
                edit_btn.clicked.connect(lambda checked, c=customer: self.edit_customer(c))
                
                # Delete button
                delete_btn = QPushButton()
                delete_btn.setIcon(QIcon("src/resources/icons/delete.png"))
                delete_btn.setIconSize(QSize(16, 16))
                delete_btn.setFixedSize(30, 30)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                delete_btn.setToolTip("Supprimer le client")
                delete_btn.clicked.connect(lambda checked, c=customer: self.delete_customer(c))
                
                # Email button
                email_btn = QPushButton()
                email_btn.setIcon(QIcon("src/resources/icons/email.png"))
                email_btn.setIconSize(QSize(16, 16))
                email_btn.setFixedSize(30, 30)
                email_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                email_btn.setToolTip("Envoyer un email au client")
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addWidget(email_btn)
                actions_layout.addStretch()
                
                self.customers_table.setCellWidget(i, 6, actions_widget)
            
            # Get recent messages
            recent_messages = self.db.query(CustomerEmail).order_by(CustomerEmail.received_at.desc()).limit(10).all()
            
            # Populate messages table
            self.messages_table.setRowCount(len(recent_messages))
            for i, message in enumerate(recent_messages):
                # Customer
                customer = self.db.query(Customer).filter(Customer.id == message.customer_id).first()
                customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Inconnu"
                customer_item = QTableWidgetItem(customer_name)
                self.messages_table.setItem(i, 0, customer_item)
                
                # Subject
                subject_item = QTableWidgetItem(message.subject)
                self.messages_table.setItem(i, 1, subject_item)
                
                # Date
                date_item = QTableWidgetItem(message.received_at.strftime("%d %b %Y %H:%M"))
                self.messages_table.setItem(i, 2, date_item)
                
                # Status
                status_text = message.status.value.capitalize()
                if message.is_incoming and message.status == EmailStatus.UNREAD:
                    status_text = "Nouveau"
                
                status_item = QTableWidgetItem(status_text)
                self.messages_table.setItem(i, 3, status_item)
                
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
                view_btn.setToolTip("Voir le message")
                
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
                reply_btn.setToolTip("Répondre")
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(reply_btn)
                actions_layout.addStretch()
                
                self.messages_table.setCellWidget(i, 4, actions_widget)
            
            logging.info("Customers view refreshed")
        except Exception as e:
            logging.error(f"Error refreshing customers data: {str(e)}")
    
    def filter_customers(self):
        """
        Filter customers based on search text.
        """
        search_text = self.search_input.text().lower()
        
        for i in range(self.customers_table.rowCount()):
            row_hidden = True
            
            # Check if search text is in any of the first 4 columns
            for j in range(4):
                item = self.customers_table.item(i, j)
                if item and search_text in item.text().lower():
                    row_hidden = False
                    break
            
            self.customers_table.setRowHidden(i, row_hidden)
    
    def add_customer(self):
        """
        Open the add customer dialog.
        """
        dialog = CustomerDetailsDialog(parent=self)
        if dialog.exec():
            # Refresh the view to show the new customer
            self.refresh_data()
    
    def edit_customer(self, customer):
        """
        Open the edit customer dialog.
        """
        dialog = CustomerDetailsDialog(customer, self)
        if dialog.exec():
            # Refresh the view to show the updated customer
            self.refresh_data()
    
    def delete_customer(self, customer):
        """
        Delete a customer.
        """
        # Check if customer has orders
        orders_count = self.db.query(Order).filter(Order.customer_id == customer.id).count()
        
        if orders_count > 0:
            QMessageBox.warning(
                self, "Suppression impossible", 
                f"Impossible de supprimer le client '{customer.first_name} {customer.last_name}' car il a des commandes."
            )
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirmer la suppression", 
            f"Êtes-vous sûr de vouloir supprimer le client '{customer.first_name} {customer.last_name}' ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete customer emails
                self.db.query(CustomerEmail).filter(CustomerEmail.customer_id == customer.id).delete()
                
                # Delete customer
                self.db.query(Customer).filter(Customer.id == customer.id).delete()
                self.db.commit()
                
                logging.info(f"Customer {customer.first_name} {customer.last_name} deleted")
                
                # Refresh the view
                self.refresh_data()
            except Exception as e:
                logging.error(f"Error deleting customer: {str(e)}")
                QMessageBox.warning(self, "Erreur", f"Une erreur est survenue : {str(e)}")
