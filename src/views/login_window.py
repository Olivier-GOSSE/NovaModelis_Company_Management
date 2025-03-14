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
        super().__init__()
        
        self.setWindowTitle(config.APP_NAME)
        self.setMinimumSize(400, 500)
        self.setWindowIcon(QIcon("src/resources/icons/logo.png"))
        
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
        
        # Logo
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("src/resources/icons/logo.png")
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
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        # Username
        username_label = QLabel("Username")
        username_label.setStyleSheet("color: #94A3B8; font-weight: bold;")
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        
        # Password
        password_label = QLabel("Password")
        password_label.setStyleSheet("color: #94A3B8; font-weight: bold;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        self.password_input.returnPressed.connect(self.login)
        
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        self.login_btn.clicked.connect(self.login)
        
        # Add widgets to form layout
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(10)
        form_layout.addWidget(self.login_btn)
        
        main_layout.addWidget(form_frame)
        
        # Version
        version_label = QLabel(f"Version {config.APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #64748B; font-size: 12px;")
        main_layout.addWidget(version_label)
    
    def login(self):
        """
        Handle login button click.
        """
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return
        
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.username == username).first()
            
            if not user:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
                return
            
            # Check password
            if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
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
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        finally:
            db.close()
