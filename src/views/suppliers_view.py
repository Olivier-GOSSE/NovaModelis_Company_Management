"""
Suppliers view for the application.
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
from models import Supplier, SupplierEmail, EmailStatus
from views.supplier_email_view import SupplierEmailComposeDialog, SupplierEmailViewDialog
import config


class SupplierDetailsDialog(QDialog):
    """
    Dialog for viewing and editing supplier details.
    """
    def __init__(self, supplier=None, parent=None, read_only=False):
        # For window dragging
        self.dragging = False
        self.drag_position = None
        
        super().__init__(parent)
        
        self.supplier = supplier
        self.is_edit_mode = supplier is not None
        self.read_only = read_only
        
        # Remove window frame and title bar
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        # Set window transparency
        self.setWindowOpacity(0.9)  # 10% transparency
        
        self.setMinimumSize(500, 600)
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_supplier_data()
            
        # If read-only mode, disable all inputs
        if self.read_only:
            self.set_read_only()
    
    def mousePressEvent(self, event):
        """
        Handle mouse press event for window dragging.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move event for window dragging.
        """
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release event for window dragging.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    def set_read_only(self):
        """
        Set all inputs to read-only mode.
        """
        # Disable all input fields
        self.company_name_input.setReadOnly(True)
        self.contact_name_input.setReadOnly(True)
        self.email_input.setReadOnly(True)
        self.phone_input.setReadOnly(True)
        self.website_input.setReadOnly(True)
        self.address_line1_input.setReadOnly(True)
        self.address_line2_input.setReadOnly(True)
        self.city_input.setReadOnly(True)
        self.state_province_input.setReadOnly(True)
        self.postal_code_input.setReadOnly(True)
        self.country_input.setReadOnly(True)
        self.notes_input.setReadOnly(True)
        
        # Change the style of read-only inputs
        read_only_style = """
            QLineEdit {
                background-color: #1E293B;
                color: #94A3B8;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
            QTextEdit {
                background-color: #1E293B;
                color: #94A3B8;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
        """
        
        self.company_name_input.setStyleSheet(read_only_style)
        self.contact_name_input.setStyleSheet(read_only_style)
        self.email_input.setStyleSheet(read_only_style)
        self.phone_input.setStyleSheet(read_only_style)
        self.website_input.setStyleSheet(read_only_style)
        self.address_line1_input.setStyleSheet(read_only_style)
        self.address_line2_input.setStyleSheet(read_only_style)
        self.city_input.setStyleSheet(read_only_style)
        self.state_province_input.setStyleSheet(read_only_style)
        self.postal_code_input.setStyleSheet(read_only_style)
        self.country_input.setStyleSheet(read_only_style)
        self.notes_input.setStyleSheet(read_only_style)
        
        # Hide the save button, change cancel button to close
        self.save_btn.setVisible(False)
        self.cancel_btn.setText("Fermer")
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Custom title bar
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(0, 0, 0, 10)
        
        # Title
        title_label = QLabel("Voir Fournisseur" if self.read_only else f"{'Modifier' if self.is_edit_mode else 'Ajouter'} Fournisseur")
        title_label.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: bold;")
        
        # Close button
        close_btn = QPushButton("×")  # Unicode multiplication sign as close icon
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                font-size: 20px;
                font-weight: bold;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #F8FAFC;
            }
        """)
        close_btn.clicked.connect(self.reject)
        
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(close_btn)
        
        main_layout.addLayout(title_bar_layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Company name
        self.company_name_input = QLineEdit()
        form_layout.addRow("Nom de l'entreprise:", self.company_name_input)
        
        # Contact name
        self.contact_name_input = QLineEdit()
        form_layout.addRow("Nom du contact:", self.contact_name_input)
        
        # Email
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        form_layout.addRow("Téléphone:", self.phone_input)
        
        # Website
        self.website_input = QLineEdit()
        form_layout.addRow("Site web:", self.website_input)
        
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
        self.save_btn.clicked.connect(self.save_supplier)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def load_supplier_data(self):
        """
        Load supplier data into the form.
        """
        if not self.supplier:
            return
        
        self.company_name_input.setText(self.supplier.company_name)
        self.contact_name_input.setText(self.supplier.contact_name)
        self.email_input.setText(self.supplier.email)
        
        if self.supplier.phone:
            self.phone_input.setText(self.supplier.phone)
        
        if self.supplier.website:
            self.website_input.setText(self.supplier.website)
        
        if self.supplier.address_line1:
            self.address_line1_input.setText(self.supplier.address_line1)
        
        if self.supplier.address_line2:
            self.address_line2_input.setText(self.supplier.address_line2)
        
        if self.supplier.city:
            self.city_input.setText(self.supplier.city)
        
        if self.supplier.state_province:
            self.state_province_input.setText(self.supplier.state_province)
        
        if self.supplier.postal_code:
            self.postal_code_input.setText(self.supplier.postal_code)
        
        if self.supplier.country:
            self.country_input.setText(self.supplier.country)
        
        if self.supplier.notes:
            self.notes_input.setText(self.supplier.notes)
    
    def save_supplier(self):
        """
        Save the supplier data.
        """
        # Validate required fields
        company_name = self.company_name_input.text().strip()
        contact_name = self.contact_name_input.text().strip()
        email = self.email_input.text().strip()
        
        if not company_name:
            QMessageBox.warning(self, "Erreur de validation", "Le nom de l'entreprise est requis.")
            return
        
        if not contact_name:
            QMessageBox.warning(self, "Erreur de validation", "Le nom du contact est requis.")
            return
        
        if not email:
            QMessageBox.warning(self, "Erreur de validation", "L'email est requis.")
            return
        
        try:
            db = SessionLocal()
            
            # Check if email is already in use
            existing_supplier = db.query(Supplier).filter(Supplier.email == email).first()
            if existing_supplier and (not self.is_edit_mode or existing_supplier.id != self.supplier.id):
                QMessageBox.warning(self, "Erreur de validation", "Cet email est déjà utilisé.")
                return
            
            if self.is_edit_mode:
                # Update existing supplier
                supplier = db.query(Supplier).filter(Supplier.id == self.supplier.id).first()
                if not supplier:
                    QMessageBox.warning(self, "Erreur", "Fournisseur non trouvé.")
                    return
            else:
                # Create new supplier
                supplier = Supplier()
                supplier.created_at = datetime.datetime.utcnow()
                db.add(supplier)
            
            # Update supplier data
            supplier.company_name = company_name
            supplier.contact_name = contact_name
            supplier.email = email
            supplier.phone = self.phone_input.text().strip() or None
            supplier.website = self.website_input.text().strip() or None
            supplier.address_line1 = self.address_line1_input.text().strip() or None
            supplier.address_line2 = self.address_line2_input.text().strip() or None
            supplier.city = self.city_input.text().strip() or None
            supplier.state_province = self.state_province_input.text().strip() or None
            supplier.postal_code = self.postal_code_input.text().strip() or None
            supplier.country = self.country_input.text().strip() or None
            supplier.notes = self.notes_input.toPlainText().strip() or None
            supplier.updated_at = datetime.datetime.utcnow()
            
            db.commit()
            
            logging.info(f"Supplier {supplier.company_name} {'updated' if self.is_edit_mode else 'created'}")
            
            self.accept()
        except Exception as e:
            logging.error(f"Error saving supplier: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            db.close()


class SuppliersView(QWidget):
    """
    Suppliers view for the application.
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
        
        header_title = QLabel("Fournisseurs")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher des fournisseurs...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_suppliers)
        
        search_layout.addWidget(self.search_input)
        
        # Add supplier button
        self.add_btn = QPushButton("Ajouter un fournisseur")
        self.add_btn.setIcon(QIcon("src/resources/icons/add_2.png"))
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        self.add_btn.clicked.connect(self.add_supplier)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addLayout(search_layout)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(header_layout)
        
        # Suppliers table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(6)
        self.suppliers_table.setHorizontalHeaderLabels([
            "Entreprise", "Contact", "Email", "Téléphone", "Localisation", "Actions"
        ])
        self.suppliers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.suppliers_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.suppliers_table.verticalHeader().setVisible(False)
        self.suppliers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.suppliers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.suppliers_table.setAlternatingRowColors(True)
        self.suppliers_table.setStyleSheet("""
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
        
        main_layout.addWidget(self.suppliers_table)
        
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
        
        # Compose email button
        compose_btn = QPushButton("Nouveau message")
        compose_btn.setIcon(QIcon("src/resources/icons/email.png"))
        compose_btn.setCursor(Qt.PointingHandCursor)
        compose_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        compose_btn.clicked.connect(self.compose_email)
        
        messages_header.addWidget(messages_title)
        messages_header.addStretch()
        messages_header.addWidget(compose_btn)
        
        messages_layout.addLayout(messages_header)
        
        # Messages table
        self.messages_table = QTableWidget()
        self.messages_table.setColumnCount(5)
        self.messages_table.setHorizontalHeaderLabels([
            "Fournisseur", "Sujet", "Date", "Statut", "Actions"
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
        Refresh the suppliers data.
        """
        try:
            # Get all suppliers
            suppliers = self.db.query(Supplier).all()
            
            self.refresh_suppliers(suppliers)
            self.refresh_messages()
        except Exception as e:
            logging.error(f"Error refreshing suppliers data: {str(e)}")
    
    def refresh_suppliers(self, suppliers):
        """
        Refresh the suppliers table.
        
        Args:
            suppliers: List of suppliers to display.
        """
        try:
            # Populate suppliers table
            self.suppliers_table.setRowCount(len(suppliers))
            
            # Set row height for better icon visibility
            for i in range(len(suppliers)):
                self.suppliers_table.setRowHeight(i, 40)
                
            for i, supplier in enumerate(suppliers):
                # Company name
                company_name_item = QTableWidgetItem(supplier.company_name)
                self.suppliers_table.setItem(i, 0, company_name_item)
                
                # Contact name
                contact_name_item = QTableWidgetItem(supplier.contact_name)
                self.suppliers_table.setItem(i, 1, contact_name_item)
                
                # Email
                email_item = QTableWidgetItem(supplier.email)
                self.suppliers_table.setItem(i, 2, email_item)
                
                # Phone
                phone_item = QTableWidgetItem(supplier.phone or "")
                self.suppliers_table.setItem(i, 3, phone_item)
                
                # Location
                location_parts = []
                if supplier.city:
                    location_parts.append(supplier.city)
                if supplier.state_province:
                    location_parts.append(supplier.state_province)
                if supplier.country:
                    location_parts.append(supplier.country)
                
                location_text = ", ".join(location_parts) if location_parts else ""
                location_item = QTableWidgetItem(location_text)
                self.suppliers_table.setItem(i, 4, location_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 0, 5, 0)
                actions_layout.setSpacing(5)
                
                # Create a fixed copy of the supplier for this row
                supplier_id = supplier.id
                
                # View button
                view_btn = QPushButton()
                view_btn.setIcon(QIcon("src/resources/icons/view.png"))
                view_btn.setIconSize(QSize(24, 24))
                view_btn.setFixedSize(40, 40)
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
                view_btn.setToolTip("Voir le fournisseur")
                view_btn.clicked.connect(lambda checked=False, id=supplier_id: self.view_supplier_by_id(id))
                
                # Edit button
                edit_btn = QPushButton()
                edit_btn.setIcon(QIcon("src/resources/icons/edit.png"))
                edit_btn.setIconSize(QSize(24, 24))
                edit_btn.setFixedSize(40, 40)
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
                edit_btn.setToolTip("Modifier le fournisseur")
                edit_btn.clicked.connect(lambda checked=False, id=supplier_id: self.edit_supplier_by_id(id))
                
                # Delete button
                delete_btn = QPushButton()
                delete_btn.setIcon(QIcon("src/resources/icons/delete.png"))
                delete_btn.setIconSize(QSize(24, 24))
                delete_btn.setFixedSize(40, 40)
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
                delete_btn.setToolTip("Supprimer le fournisseur")
                delete_btn.clicked.connect(lambda checked=False, id=supplier_id: self.delete_supplier_by_id(id))
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                self.suppliers_table.setCellWidget(i, 5, actions_widget)
            
            logging.info("Suppliers view refreshed")
        except Exception as e:
            logging.error(f"Error refreshing suppliers data: {str(e)}")
    
    def filter_suppliers(self):
        """
        Filter suppliers based on search text.
        """
        search_text = self.search_input.text().lower()
        
        for i in range(self.suppliers_table.rowCount()):
            row_hidden = True
            
            # Check if search text is in any of the first 5 columns
            for j in range(5):
                item = self.suppliers_table.item(i, j)
                if item and search_text in item.text().lower():
                    row_hidden = False
                    break
            
            self.suppliers_table.setRowHidden(i, row_hidden)
    
    def add_supplier(self):
        """
        Open the add supplier dialog.
        """
        dialog = SupplierDetailsDialog(parent=self)
        if dialog.exec():
            # Refresh the view to show the new supplier
            self.refresh_data()
    
    def view_supplier(self, supplier):
        """
        Open the view supplier dialog in read-only mode.
        """
        dialog = SupplierDetailsDialog(supplier, self, read_only=True)
        dialog.exec()
    
    def edit_supplier(self, supplier):
        """
        Open the edit supplier dialog.
        """
        dialog = SupplierDetailsDialog(supplier, self)
        if dialog.exec():
            # Refresh the view to show the updated supplier
            self.refresh_data()
    
    def delete_supplier(self, supplier):
        """
        Delete a supplier.
        """
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirmer la suppression", 
            f"Êtes-vous sûr de vouloir supprimer le fournisseur '{supplier.company_name}' ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete supplier
                self.db.query(Supplier).filter(Supplier.id == supplier.id).delete()
                self.db.commit()
                
                logging.info(f"Supplier {supplier.company_name} deleted")
                
                # Refresh the view
                self.refresh_data()
            except Exception as e:
                logging.error(f"Error deleting supplier: {str(e)}")
                QMessageBox.warning(self, "Erreur", f"Une erreur est survenue : {str(e)}")
    
    def view_supplier_by_id(self, supplier_id):
        """
        Open the view supplier dialog in read-only mode using supplier ID.
        """
        try:
            supplier = self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
            if supplier:
                self.view_supplier(supplier)
            else:
                QMessageBox.warning(self, "Erreur", "Fournisseur non trouvé.")
        except Exception as e:
            logging.error(f"Error viewing supplier: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue : {str(e)}")
    
    def edit_supplier_by_id(self, supplier_id):
        """
        Open the edit supplier dialog using supplier ID.
        """
        try:
            supplier = self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
            if supplier:
                self.edit_supplier(supplier)
            else:
                QMessageBox.warning(self, "Erreur", "Fournisseur non trouvé.")
        except Exception as e:
            logging.error(f"Error editing supplier: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue : {str(e)}")
    
    def delete_supplier_by_id(self, supplier_id):
        """
        Delete a supplier using supplier ID.
        """
        try:
            supplier = self.db.query(Supplier).filter(Supplier.id == supplier_id).first()
            if supplier:
                self.delete_supplier(supplier)
            else:
                QMessageBox.warning(self, "Erreur", "Fournisseur non trouvé.")
        except Exception as e:
            logging.error(f"Error deleting supplier: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue : {str(e)}")
    
    def refresh_messages(self):
        """
        Refresh the messages table.
        """
        try:
            # Get all emails
            emails = self.db.query(SupplierEmail).order_by(SupplierEmail.received_at.desc()).limit(10).all()
            
            # Populate messages table
            self.messages_table.setRowCount(len(emails))
            
            # Set row height for better icon visibility
            for i in range(len(emails)):
                self.messages_table.setRowHeight(i, 40)
                
            for i, email in enumerate(emails):
                # Supplier
                supplier = self.db.query(Supplier).filter(Supplier.id == email.supplier_id).first()
                supplier_name = supplier.company_name if supplier else "Inconnu"
                supplier_item = QTableWidgetItem(supplier_name)
                
                # Make unread emails bold
                if email.status == EmailStatus.UNREAD:
                    font = supplier_item.font()
                    font.setBold(True)
                    supplier_item.setFont(font)
                
                self.messages_table.setItem(i, 0, supplier_item)
                
                # Subject
                subject_item = QTableWidgetItem(email.subject)
                
                # Make unread emails bold
                if email.status == EmailStatus.UNREAD:
                    font = subject_item.font()
                    font.setBold(True)
                    subject_item.setFont(font)
                
                self.messages_table.setItem(i, 1, subject_item)
                
                # Date
                date_item = QTableWidgetItem(email.received_at.strftime("%d %b %Y %H:%M"))
                self.messages_table.setItem(i, 2, date_item)
                
                # Status
                status_text = email.status.value.capitalize()
                if email.status == EmailStatus.UNREAD:
                    status_text = "Nouveau"
                
                status_item = QTableWidgetItem(status_text)
                self.messages_table.setItem(i, 3, status_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 0, 5, 0)
                actions_layout.setSpacing(5)
                
                # Create a fixed copy of the email for this row
                email_id = email.id
                
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
                view_btn.clicked.connect(lambda checked=False, id=email_id: self.view_message(id))
                
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
                reply_btn.clicked.connect(lambda checked=False, id=email_id: self.reply_to_message(id))
                
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
                delete_btn.setToolTip("Supprimer")
                delete_btn.clicked.connect(lambda checked=False, id=email_id: self.delete_message(id))
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(reply_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                self.messages_table.setCellWidget(i, 4, actions_widget)
            
            logging.info("Messages refreshed")
        except Exception as e:
            logging.error(f"Error refreshing messages: {str(e)}")
    
    def compose_email(self, supplier=None):
        """
        Open the compose email dialog.
        
        Args:
            supplier: Optional supplier to pre-fill the recipient field.
        """
        dialog = SupplierEmailComposeDialog(parent=self, supplier=supplier)
        if dialog.exec():
            # Refresh the view to show the new email
            self.refresh_messages()
    
    def view_message(self, email_id):
        """
        Open the email view dialog.
        
        Args:
            email_id: ID of the email to view.
        """
        try:
            email = self.db.query(SupplierEmail).filter(SupplierEmail.id == email_id).first()
            if email:
                dialog = SupplierEmailViewDialog(email, self)
                if dialog.exec():
                    # Refresh the view to show updated status
                    self.refresh_messages()
            else:
                QMessageBox.warning(self, "Erreur", "Message non trouvé.")
        except Exception as e:
            logging.error(f"Error viewing message: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue : {str(e)}")
    
    def reply_to_message(self, email_id):
        """
        Open the compose dialog to reply to an email.
        
        Args:
            email_id: ID of the email to reply to.
        """
        try:
            email = self.db.query(SupplierEmail).filter(SupplierEmail.id == email_id).first()
            if email:
                supplier = self.db.query(Supplier).filter(Supplier.id == email.supplier_id).first()
                if supplier:
                    dialog = SupplierEmailComposeDialog(
                        parent=self,
                        reply_to=email,
                        supplier=supplier
                    )
                    if dialog.exec():
                        # Refresh the view to show the new email
                        self.refresh_messages()
                else:
                    QMessageBox.warning(self, "Erreur", "Fournisseur non trouvé.")
            else:
                QMessageBox.warning(self, "Erreur", "Message non trouvé.")
        except Exception as e:
            logging.error(f"Error replying to message: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue : {str(e)}")
    
    def delete_message(self, email_id):
        """
        Delete an email.
        
        Args:
            email_id: ID of the email to delete.
        """
        try:
            email = self.db.query(SupplierEmail).filter(SupplierEmail.id == email_id).first()
            if email:
                # Confirm deletion
                reply = QMessageBox.question(
                    self, "Confirmer la suppression", 
                    "Êtes-vous sûr de vouloir supprimer ce message ?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.db.query(SupplierEmail).filter(SupplierEmail.id == email_id).delete()
                    self.db.commit()
                    
                    logging.info(f"Message deleted: {email.subject}")
                    
                    # Refresh the view
                    self.refresh_messages()
            else:
                QMessageBox.warning(self, "Erreur", "Message non trouvé.")
        except Exception as e:
            logging.error(f"Error deleting message: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue : {str(e)}")
