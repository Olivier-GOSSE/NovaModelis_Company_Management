"""
Email view for the application.
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
    QTabWidget, QSplitter, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QFont, QColor, QPainter

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal
from models import Customer, CustomerEmail, EmailStatus
import config


class EmailViewDialog(QDialog):
    """
    Dialog for viewing an email.
    """
    def __init__(self, email=None, parent=None):
        # For window dragging
        self.dragging = False
        self.drag_position = None
        
        super().__init__(parent)
        
        self.email = email
        
        # Remove window frame and title bar
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        # Set window transparency
        self.setWindowOpacity(0.9)  # 10% transparency
        
        self.setMinimumSize(700, 500)
        
        self.setup_ui()
        
        if self.email:
            self.load_email_data()
    
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
        title_label = QLabel("Voir Email")
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
        
        # Email header
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet("""
            #headerFrame {
                background-color: rgba(30, 41, 59, 0.9); /* 10% transparency */
                border-radius: 12px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 15, 15, 15)
        header_layout.setSpacing(10)
        
        # Subject
        self.subject_label = QLabel()
        self.subject_label.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.subject_label)
        
        # From/To
        from_to_layout = QHBoxLayout()
        
        self.from_label = QLabel()
        self.from_label.setStyleSheet("color: #94A3B8;")
        
        self.to_label = QLabel()
        self.to_label.setStyleSheet("color: #94A3B8;")
        
        from_to_layout.addWidget(self.from_label)
        from_to_layout.addStretch()
        from_to_layout.addWidget(self.to_label)
        
        header_layout.addLayout(from_to_layout)
        
        # Date
        date_layout = QHBoxLayout()
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("color: #94A3B8;")
        
        date_layout.addWidget(self.date_label)
        date_layout.addStretch()
        
        header_layout.addLayout(date_layout)
        
        main_layout.addWidget(header_frame)
        
        # Email content
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_frame.setStyleSheet("""
            #contentFrame {
                background-color: rgba(30, 41, 59, 0.9); /* 10% transparency */
                border-radius: 12px;
            }
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)
        
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 41, 59, 0.9); /* 10% transparency */
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
            }
        """)
        
        content_layout.addWidget(self.content_text)
        
        main_layout.addWidget(content_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.reply_btn = QPushButton("Répondre")
        self.reply_btn.setIcon(QIcon("src/resources/icons/reply.png"))
        self.reply_btn.setCursor(Qt.PointingHandCursor)
        self.reply_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.reply_btn.clicked.connect(self.reply_to_email)
        
        self.close_btn = QPushButton("Fermer")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #64748B;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.reply_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def load_email_data(self):
        """
        Load email data into the view.
        """
        if not self.email:
            return
        
        # Set subject
        self.subject_label.setText(self.email.subject)
        
        # Set from/to
        try:
            db = SessionLocal()
            customer = db.query(Customer).filter(Customer.id == self.email.customer_id).first()
            customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Inconnu"
            
            if self.email.is_incoming:
                self.from_label.setText(f"De: {customer_name} <{customer.email}>")
                self.to_label.setText(f"À: {self.email.to_email}")
            else:
                self.from_label.setText(f"De: {self.email.from_email}")
                self.to_label.setText(f"À: {customer_name} <{customer.email}>")
        except Exception as e:
            logging.error(f"Error loading customer data: {str(e)}")
        finally:
            db.close()
        
        # Set date
        self.date_label.setText(f"Date: {self.email.received_at.strftime('%d %b %Y %H:%M')}")
        
        # Set content
        self.content_text.setHtml(self.email.body)
        
        # Update email status to read if it's unread
        if self.email.is_incoming and self.email.status == EmailStatus.UNREAD:
            try:
                db = SessionLocal()
                email = db.query(CustomerEmail).filter(CustomerEmail.id == self.email.id).first()
                if email:
                    email.status = EmailStatus.READ
                    db.commit()
            except Exception as e:
                logging.error(f"Error updating email status: {str(e)}")
            finally:
                db.close()
    
    def reply_to_email(self):
        """
        Open the compose dialog to reply to this email.
        """
        if not self.email:
            return
        
        try:
            db = SessionLocal()
            customer = db.query(Customer).filter(Customer.id == self.email.customer_id).first()
            
            if customer:
                compose_dialog = EmailComposeDialog(
                    parent=self.parent(),
                    reply_to=self.email,
                    customer=customer
                )
                compose_dialog.exec()
        except Exception as e:
            logging.error(f"Error preparing reply: {str(e)}")
        finally:
            db.close()


class EmailComposeDialog(QDialog):
    """
    Dialog for composing an email.
    """
    def __init__(self, parent=None, reply_to=None, customer=None):
        # For window dragging
        self.dragging = False
        self.drag_position = None
        
        super().__init__(parent)
        
        self.reply_to = reply_to
        self.customer = customer
        
        # Remove window frame and title bar
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        # Set window transparency
        self.setWindowOpacity(0.9)  # 10% transparency
        
        self.setFixedSize(700, 600)
        
        self.setup_ui()
        
        if reply_to and customer:
            self.prepare_reply()
    
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
        title_label = QLabel("Répondre à l'email" if self.reply_to else "Nouveau Email")
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
        
        # Form layout for header fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # From field (email account selection)
        self.from_combo = QComboBox()
        self.load_email_accounts()
        form_layout.addRow("De:", self.from_combo)
        
        # To field
        self.to_input = QLineEdit()
        # If customer is provided, pre-fill the recipient field
        if self.customer and not self.reply_to:
            self.to_input.setText(self.customer.email)
        form_layout.addRow("À:", self.to_input)
        
        # Subject field
        self.subject_input = QLineEdit()
        form_layout.addRow("Sujet:", self.subject_input)
        
        main_layout.addLayout(form_layout)
        
        # Email content
        self.content_text = QTextEdit()
        self.content_text.setMinimumHeight(300)
        self.content_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 41, 59, 0.9); /* 10% transparency */
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 8px;
            }
        """)
        
        main_layout.addWidget(self.content_text)
        
        # Attachments
        attachments_layout = QHBoxLayout()
        
        self.attach_btn = QPushButton("Joindre un fichier")
        self.attach_btn.setIcon(QIcon("src/resources/icons/attachment.png"))
        self.attach_btn.setCursor(Qt.PointingHandCursor)
        self.attach_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        self.attach_btn.clicked.connect(self.attach_file)
        
        attachments_layout.addWidget(self.attach_btn)
        attachments_layout.addStretch()
        
        main_layout.addLayout(attachments_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.send_btn = QPushButton("Envoyer")
        self.send_btn.setIcon(QIcon("src/resources/icons/send.png"))
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.send_btn.clicked.connect(self.send_email)
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #64748B;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.send_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def load_email_accounts(self):
        """
        Load email accounts into the combo box.
        """
        # In a real application, this would load from a configuration or database
        # For this demo, we'll add some sample accounts
        self.from_combo.addItem("contact@novamodelisapp.com", "contact@novamodelisapp.com")
        self.from_combo.addItem("support@novamodelisapp.com", "support@novamodelisapp.com")
        self.from_combo.addItem("sales@novamodelisapp.com", "sales@novamodelisapp.com")
    
    def attach_file(self):
        """
        Open a file dialog to select a file to attach to the email.
        """
        # In a real application, this would open a file dialog and attach the selected file
        # For this demo, we'll just show a message
        QMessageBox.information(self, "Joindre un fichier", "Fonctionnalité de pièce jointe à implémenter.")
    
    def prepare_reply(self):
        """
        Prepare the reply to an email.
        """
        if not self.reply_to or not self.customer:
            return
        
        # Set recipient
        self.to_input.setText(self.customer.email)
        self.to_input.setReadOnly(True)
        
        # Set subject with Re: prefix if not already present
        subject = self.reply_to.subject
        if not subject.startswith("Re:"):
            subject = f"Re: {subject}"
        self.subject_input.setText(subject)
        
        # Set content with quote of original email
        original_date = self.reply_to.received_at.strftime("%d %b %Y %H:%M")
        quoted_content = f"<br><br>Le {original_date}, {self.customer.first_name} {self.customer.last_name} a écrit:<br>"
        quoted_content += f"<blockquote style='border-left: 2px solid #3B82F6; padding-left: 10px; color: #94A3B8;'>"
        quoted_content += f"{self.reply_to.body}"
        quoted_content += "</blockquote>"
        
        self.content_text.setHtml(quoted_content)
        
        # Set cursor at the beginning for the reply
        cursor = self.content_text.textCursor()
        cursor.setPosition(0)
        self.content_text.setTextCursor(cursor)
        self.content_text.setFocus()
    
    def send_email(self):
        """
        Send the email.
        """
        # Validate required fields
        from_email = self.from_combo.currentData()
        to_email = self.to_input.text().strip()
        subject = self.subject_input.text().strip()
        content = self.content_text.toHtml()
        
        if not to_email:
            QMessageBox.warning(self, "Erreur de validation", "Le destinataire est requis.")
            return
        
        if not subject:
            QMessageBox.warning(self, "Erreur de validation", "Le sujet est requis.")
            return
        
        if not content:
            QMessageBox.warning(self, "Erreur de validation", "Le contenu est requis.")
            return
        
        try:
            db = SessionLocal()
            
            # Get customer ID
            customer_id = None
            if self.customer:
                customer_id = self.customer.id
            else:
                # Try to find customer by email
                customer = db.query(Customer).filter(Customer.email == to_email).first()
                if customer:
                    customer_id = customer.id
            
            # Create new email
            email = CustomerEmail()
            email.customer_id = customer_id
            email.from_email = from_email
            email.to_email = to_email
            email.subject = subject
            email.body = content
            email.is_incoming = False
            email.status = EmailStatus.SENT
            email.received_at = datetime.datetime.utcnow()
            email.created_at = datetime.datetime.utcnow()
            
            db.add(email)
            db.commit()
            
            logging.info(f"Email sent to {to_email}")
            
            QMessageBox.information(self, "Email envoyé", "L'email a été envoyé avec succès.")
            
            self.accept()
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            db.close()


class EmailView(QWidget):
    """
    Email view for the application.
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
        
        header_title = QLabel("Emails")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher des emails...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(30, 41, 59, 0.9); /* 10% transparency */
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 8px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_emails)
        
        search_layout.addWidget(self.search_input)
        
        # Compose button
        self.compose_btn = QPushButton("Nouveau Email")
        self.compose_btn.setIcon(QIcon("src/resources/icons/email.png"))
        self.compose_btn.setCursor(Qt.PointingHandCursor)
        self.compose_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.compose_btn.clicked.connect(self.compose_email)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addLayout(search_layout)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.compose_btn)
        
        main_layout.addLayout(header_layout)
        
        # Email tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: rgba(30, 41, 59, 0.9); /* 10% transparency */
                border-radius: 12px;
                border: none;
            }
            QTabBar::tab {
                background-color: #0F172A;
                color: #94A3B8;
                border: none;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: rgba(30, 41, 59, 0.9); /* Match the pane */
                color: #F8FAFC;
            }
            QTabBar::tab:hover:!selected {
                background-color: rgba(30, 41, 59, 0.9); /* Match the pane */
                color: #F8FAFC;
            }
        """)
        
        # Inbox tab
        self.inbox_tab = QWidget()
        self.setup_inbox_tab()
        self.tabs.addTab(self.inbox_tab, "Boîte de réception")
        
        # Sent tab
        self.sent_tab = QWidget()
        self.setup_sent_tab()
        self.tabs.addTab(self.sent_tab, "Envoyés")
        
        main_layout.addWidget(self.tabs)
    
    def setup_inbox_tab(self):
        """
        Set up the inbox tab.
        """
        # Tab layout
        tab_layout = QVBoxLayout(self.inbox_tab)
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.setSpacing(10)
        
        # Emails table
        self.inbox_table = QTableWidget()
        self.inbox_table.setColumnCount(5)
        self.inbox_table.setHorizontalHeaderLabels([
            "Expéditeur", "Sujet", "Date", "Statut", "Actions"
        ])
        self.inbox_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inbox_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.inbox_table.verticalHeader().setVisible(False)
        self.inbox_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.inbox_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.inbox_table.setAlternatingRowColors(True)
        self.inbox_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(30, 41, 59, 0.9); /* 10% transparency */
                border-radius: 12px;
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
        
        tab_layout.addWidget(self.inbox_table)
    
    def setup_sent_tab(self):
        """
        Set up the sent tab.
        """
        # Tab layout
        tab_layout = QVBoxLayout(self.sent_tab)
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.setSpacing(10)
        
        # Emails table
        self.sent_table = QTableWidget()
        self.sent_table.setColumnCount(4)
        self.sent_table.setHorizontalHeaderLabels([
            "Destinataire", "Sujet", "Date", "Actions"
        ])
        self.sent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sent_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.sent_table.verticalHeader().setVisible(False)
        self.sent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sent_table.setAlternatingRowColors(True)
        self.sent_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(30, 41, 59, 0.9); /* 10% transparency */
                border-radius: 12px;
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
        
        tab_layout.addWidget(self.sent_table)
    
    def refresh_data(self):
        """
        Refresh the emails data.
        """
        self.refresh_inbox()
        self.refresh_sent()
    
    def refresh_inbox(self):
        """
        Refresh the inbox data.
        """
        try:
            # Get incoming emails
            emails = self.db.query(CustomerEmail).filter(
                CustomerEmail.is_incoming == True
            ).order_by(CustomerEmail.received_at.desc()).all()
            
            # Populate inbox table
            self.inbox_table.setRowCount(len(emails))
            
            # Set row height for better icon visibility
            for i in range(len(emails)):
                self.inbox_table.setRowHeight(i, 40)
                
            for i, email in enumerate(emails):
                # From
                customer = self.db.query(Customer).filter(Customer.id == email.customer_id).first()
                from_text = f"{customer.first_name} {customer.last_name}" if customer else "Inconnu"
                from_item = QTableWidgetItem(from_text)
                
                # Make unread emails bold
                if email.status == EmailStatus.UNREAD:
                    font = from_item.font()
                    font.setBold(True)
                    from_item.setFont(font)
                
                self.inbox_table.setItem(i, 0, from_item)
                
                # Subject
                subject_item = QTableWidgetItem(email.subject)
                
                # Make unread emails bold
                if email.status == EmailStatus.UNREAD:
                    font = subject_item.font()
                    font.setBold(True)
                    subject_item.setFont(font)
                
                self.inbox_table.setItem(i, 1, subject_item)
                
                # Date
                date_item = QTableWidgetItem(email.received_at.strftime("%d %b %Y %H:%M"))
                self.inbox_table.setItem(i, 2, date_item)
                
                # Status
                status_text = email.status.value.capitalize()
                if email.status == EmailStatus.UNREAD:
                    status_text = "Nouveau"
                
                status_item = QTableWidgetItem(status_text)
                self.inbox_table.setItem(i, 3, status_item)
                
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
                view_btn.setToolTip("Voir l'email")
                view_btn.clicked.connect(lambda checked, e=email: self.view_email(e))
                
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
                reply_btn.clicked.connect(lambda checked, e=email: self.reply_to_email(e))
                
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
                delete_btn.clicked.connect(lambda checked, e=email: self.delete_email(e))
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(reply_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                self.inbox_table.setCellWidget(i, 4, actions_widget)
            
            logging.info("Inbox refreshed")
        except Exception as e:
            logging.error(f"Error refreshing inbox: {str(e)}")
    
    def refresh_sent(self):
        """
        Refresh the sent emails data.
        """
        try:
            # Get outgoing emails
            emails = self.db.query(CustomerEmail).filter(
                CustomerEmail.is_incoming == False
            ).order_by(CustomerEmail.received_at.desc()).all()
            
            # Populate sent table
            self.sent_table.setRowCount(len(emails))
            
            # Set row height for better icon visibility
            for i in range(len(emails)):
                self.sent_table.setRowHeight(i, 40)
                
            for i, email in enumerate(emails):
                # To
                customer = self.db.query(Customer).filter(Customer.id == email.customer_id).first()
                to_text = f"{customer.first_name} {customer.last_name}" if customer else email.to_email
                to_item = QTableWidgetItem(to_text)
                self.sent_table.setItem(i, 0, to_item)
                
                # Subject
                subject_item = QTableWidgetItem(email.subject)
                self.sent_table.setItem(i, 1, subject_item)
                
                # Date
                date_item = QTableWidgetItem(email.received_at.strftime("%d %b %Y %H:%M"))
                self.sent_table.setItem(i, 2, date_item)
                
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
                view_btn.setToolTip("Voir l'email")
                view_btn.clicked.connect(lambda checked, e=email: self.view_email(e))
                
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
                delete_btn.clicked.connect(lambda checked, e=email: self.delete_email(e))
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                self.sent_table.setCellWidget(i, 3, actions_widget)
            
            logging.info("Sent emails refreshed")
        except Exception as e:
            logging.error(f"Error refreshing sent emails: {str(e)}")
    
    def filter_emails(self):
        """
        Filter emails based on search text.
        """
        search_text = self.search_input.text().lower()
        
        # Filter inbox
        for i in range(self.inbox_table.rowCount()):
            row_hidden = True
            
            # Check if search text is in any of the first 3 columns
            for j in range(3):
                item = self.inbox_table.item(i, j)
                if item and search_text in item.text().lower():
                    row_hidden = False
                    break
            
            self.inbox_table.setRowHidden(i, row_hidden)
        
        # Filter sent
        for i in range(self.sent_table.rowCount()):
            row_hidden = True
            
            # Check if search text is in any of the first 3 columns
            for j in range(3):
                item = self.sent_table.item(i, j)
                if item and search_text in item.text().lower():
                    row_hidden = False
                    break
            
            self.sent_table.setRowHidden(i, row_hidden)
    
    def view_email(self, email):
        """
        Open the email view dialog.
        """
        dialog = EmailViewDialog(email, self)
        if dialog.exec():
            # Refresh the view to show updated status
            self.refresh_data()
    
    def reply_to_email(self, email):
        """
        Open the compose dialog to reply to an email.
        """
        try:
            db = SessionLocal()
            customer = db.query(Customer).filter(Customer.id == email.customer_id).first()
            
            if customer:
                compose_dialog = EmailComposeDialog(
                    parent=self,
                    reply_to=email,
                    customer=customer
                )
                if compose_dialog.exec():
                    # Refresh the view to show the new email
                    self.refresh_data()
        except Exception as e:
            logging.error(f"Error preparing reply: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            db.close()
    
    def delete_email(self, email):
        """
        Delete an email.
        """
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirmer la suppression", 
            "Êtes-vous sûr de vouloir supprimer cet email ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db = SessionLocal()
                db.query(CustomerEmail).filter(CustomerEmail.id == email.id).delete()
                db.commit()
                
                logging.info(f"Email deleted: {email.subject}")
                
                # Refresh the view
                self.refresh_data()
            except Exception as e:
                logging.error(f"Error deleting email: {str(e)}")
                QMessageBox.warning(self, "Erreur", f"Une erreur est survenue: {str(e)}")
            finally:
                db.close()
    
    def compose_email(self, customer=None):
        """
        Open the compose email dialog.
        
        Args:
            customer: Optional customer to pre-fill the recipient field.
        """
        dialog = EmailComposeDialog(parent=self, customer=customer)
        if dialog.exec():
            # Refresh the view to show the new email
            self.refresh_data()
