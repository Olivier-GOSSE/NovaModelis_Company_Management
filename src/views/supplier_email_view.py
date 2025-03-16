"""
Supplier email view for the application.
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
from models import Supplier, SupplierEmail, EmailStatus
import config


class SupplierEmailViewDialog(QDialog):
    """
    Dialog for viewing a supplier email.
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
            supplier = db.query(Supplier).filter(Supplier.id == self.email.supplier_id).first()
            supplier_name = f"{supplier.company_name}" if supplier else "Inconnu"
            
            if self.email.is_incoming:
                self.from_label.setText(f"De: {supplier_name} <{supplier.email}>")
                self.to_label.setText(f"À: NovaModelis")
            else:
                self.from_label.setText(f"De: NovaModelis")
                self.to_label.setText(f"À: {supplier_name} <{supplier.email}>")
        except Exception as e:
            logging.error(f"Error loading supplier data: {str(e)}")
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
                email = db.query(SupplierEmail).filter(SupplierEmail.id == self.email.id).first()
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
            supplier = db.query(Supplier).filter(Supplier.id == self.email.supplier_id).first()
            
            if supplier:
                compose_dialog = SupplierEmailComposeDialog(
                    parent=self.parent(),
                    reply_to=self.email,
                    supplier=supplier
                )
                compose_dialog.exec()
        except Exception as e:
            logging.error(f"Error preparing reply: {str(e)}")
        finally:
            db.close()


class SupplierEmailComposeDialog(QDialog):
    """
    Dialog for composing a supplier email.
    """
    def __init__(self, parent=None, reply_to=None, supplier=None):
        # For window dragging
        self.dragging = False
        self.drag_position = None
        
        super().__init__(parent)
        
        self.reply_to = reply_to
        self.supplier = supplier
        
        # Remove window frame and title bar
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        # Set window transparency
        self.setWindowOpacity(0.9)  # 10% transparency
        
        self.setFixedSize(700, 600)
        
        self.setup_ui()
        
        if reply_to and supplier:
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
        # If supplier is provided, pre-fill the recipient field
        if self.supplier and not self.reply_to:
            self.to_input.setText(self.supplier.email)
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
        self.from_combo.addItem("purchasing@novamodelisapp.com", "purchasing@novamodelisapp.com")
    
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
        if not self.reply_to or not self.supplier:
            return
        
        # Set recipient
        self.to_input.setText(self.supplier.email)
        self.to_input.setReadOnly(True)
        
        # Set subject with Re: prefix if not already present
        subject = self.reply_to.subject
        if not subject.startswith("Re:"):
            subject = f"Re: {subject}"
        self.subject_input.setText(subject)
        
        # Set content with quote of original email
        original_date = self.reply_to.received_at.strftime("%d %b %Y %H:%M")
        quoted_content = f"<br><br>Le {original_date}, {self.supplier.company_name} a écrit:<br>"
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
            
            # Get supplier ID
            supplier_id = None
            if self.supplier:
                supplier_id = self.supplier.id
            else:
                # Try to find supplier by email
                supplier = db.query(Supplier).filter(Supplier.email == to_email).first()
                if supplier:
                    supplier_id = supplier.id
            
            # Create new email
            email = SupplierEmail()
            email.supplier_id = supplier_id
            email.subject = subject
            email.body = content
            email.is_incoming = False
            email.status = EmailStatus.SENT
            email.received_at = datetime.datetime.utcnow()
            email.created_at = datetime.datetime.utcnow()
            email.updated_at = datetime.datetime.utcnow()
            
            db.add(email)
            db.commit()
            
            logging.info(f"Email sent to supplier {to_email}")
            
            QMessageBox.information(self, "Email envoyé", "L'email a été envoyé avec succès.")
            
            self.accept()
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            db.close()
