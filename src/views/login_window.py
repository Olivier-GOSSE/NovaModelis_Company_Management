"""
Login window for the application.
"""
import os
import sys
import logging
import datetime
import bcrypt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QFont

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal
from models import User
import config


class LoginWindow(QMainWindow):
    """
    Login window for the application.
    """
    # Signals
    login_successful = Signal(User)
    
    def __init__(self):
        # For window dragging
        self.dragging = False
        self.drag_position = None
        super().__init__()
        
        self.setWindowTitle(config.APP_NAME)
        self.setFixedSize(400, 600)  # Further increased height to ensure all elements are visible
        self.setWindowIcon(QIcon("src/resources/icons/Logo.png"))
        
        # Set window flags to remove the resize handles
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
        # Set rounded corners and transparency using stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F172A;
                border-radius: 15px;
                border: 1px solid #334155;
                opacity: 0.9;  /* 10% transparency (90% opacity) */
            }
        """)
        
        # Set window transparency
        self.setWindowOpacity(0.9)  # 10% transparency (90% opacity)
        
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Add close button at the top right
        close_btn_layout = QHBoxLayout()
        close_btn_layout.setContentsMargins(0, 0, 0, 0)
        close_btn_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
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
        close_btn.clicked.connect(self.close)
        
        close_btn_layout.addWidget(close_btn)
        main_layout.addLayout(close_btn_layout)
        
        # Logo
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("src/resources/icons/Logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        logo_layout.addWidget(logo_label)
        main_layout.addLayout(logo_layout)
        
        # Title
        title_label = QLabel(config.APP_NAME)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #F8FAFC; font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Login form
        form_frame = QFrame()
        form_frame.setObjectName("loginForm")
        form_frame.setStyleSheet("""
            #loginForm {
                background-color: rgba(30, 41, 59, 0.9); /* 10% transparency */
                border-radius: 12px;
            }
        """)
        
        # Main form layout
        main_form_layout = QVBoxLayout(form_frame)
        main_form_layout.setContentsMargins(20, 20, 20, 20)
        main_form_layout.setSpacing(20)
        
        # Username input - using only placeholder, no separate label
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 12px;
                padding: 10px;
                min-height: 55px;
                height: 55px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        main_form_layout.addWidget(self.username_input)
        
        # Add spacing between username and password
        main_form_layout.addSpacing(20)
        
        # Password input - using only placeholder, no separate label
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 12px;
                padding: 10px;
                min-height: 55px;
                height: 55px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        self.password_input.returnPressed.connect(self.login)
        main_form_layout.addWidget(self.password_input)
        
        # Add spacing before login button
        main_form_layout.addSpacing(30)
        
        # Login button
        self.login_btn = QPushButton("Connexion")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setFixedHeight(50)  # Ensure fixed height
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 10px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        self.login_btn.clicked.connect(self.login)
        main_form_layout.addWidget(self.login_btn)
        
        main_layout.addWidget(form_frame)
        
        # Version
        version_label = QLabel(f"Version {config.APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #64748B; font-size: 12px;")
        main_layout.addWidget(version_label)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press event.
        
        Args:
            event: The mouse press event.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move event.
        
        Args:
            event: The mouse move event.
        """
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release event.
        
        Args:
            event: The mouse release event.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    def login(self):
        """
        Handle login button click.
        """
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Échec de connexion", "Veuillez entrer votre nom d'utilisateur et votre mot de passe.")
            return
        
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.username == username).first()
            
            if not user:
                QMessageBox.warning(self, "Échec de connexion", "Nom d'utilisateur ou mot de passe invalide.")
                return
            
            # Check password
            if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
                QMessageBox.warning(self, "Échec de connexion", "Nom d'utilisateur ou mot de passe invalide.")
                return
            
            # Update last login
            user.last_login = datetime.datetime.utcnow()
            db.commit()
            
            # Emit login successful signal
            self.login_successful.emit(user)
            
            # Clear inputs
            self.username_input.clear()
            self.password_input.clear()
            
            logging.info(f"User {username} logged in successfully")
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            db.close()
