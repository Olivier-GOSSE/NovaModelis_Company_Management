"""
Settings view for the application.
"""
import os
import sys
import logging
import datetime
import bcrypt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QTabWidget, QLineEdit,
    QFormLayout, QCheckBox, QSpinBox, QMessageBox, QComboBox,
    QFileDialog, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont, QColor, QPainter

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal
from models import User
import config


class SettingsView(QWidget):
    """
    Settings view for the application.
    """
    # Signals
    theme_changed = Signal(bool)  # True for dark mode, False for light mode
    
    def __init__(self, db, user):
        super().__init__()
        
        self.db = db
        self.user = user
        
        self.setup_ui()
    
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
        
        header_title = QLabel("Settings")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background-color: #1E293B;
                border-radius: 8px;
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
                background-color: #1E293B;
                color: #F8FAFC;
            }
            QTabBar::tab:hover:!selected {
                background-color: #1E293B;
                color: #F8FAFC;
            }
        """)
        
        # User profile tab
        self.profile_tab = QWidget()
        self.setup_profile_tab()
        self.tab_widget.addTab(self.profile_tab, "User Profile")
        
        # Application settings tab
        self.app_settings_tab = QWidget()
        self.setup_app_settings_tab()
        self.tab_widget.addTab(self.app_settings_tab, "Application Settings")
        
        main_layout.addWidget(self.tab_widget)
    
    def setup_profile_tab(self):
        """
        Set up the user profile tab.
        """
        # Tab layout
        tab_layout = QVBoxLayout(self.profile_tab)
        tab_layout.setContentsMargins(20, 20, 20, 20)
        tab_layout.setSpacing(20)
        
        # User info form
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_frame.setStyleSheet("""
            #formFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        # Username
        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: #94A3B8;")
        
        self.username_input = QLineEdit()
        self.username_input.setText(self.user.username)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        
        form_layout.addRow(username_label, self.username_input)
        
        # Email
        email_label = QLabel("Email:")
        email_label.setStyleSheet("color: #94A3B8;")
        
        self.email_input = QLineEdit()
        self.email_input.setText(self.user.email)
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        
        form_layout.addRow(email_label, self.email_input)
        
        # Full name
        full_name_label = QLabel("Full Name:")
        full_name_label.setStyleSheet("color: #94A3B8;")
        
        self.full_name_input = QLineEdit()
        self.full_name_input.setText(self.user.full_name)
        self.full_name_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        
        form_layout.addRow(full_name_label, self.full_name_input)
        
        # Change password
        password_label = QLabel("New Password:")
        password_label.setStyleSheet("color: #94A3B8;")
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        
        form_layout.addRow(password_label, self.password_input)
        
        # Confirm password
        confirm_password_label = QLabel("Confirm Password:")
        confirm_password_label.setStyleSheet("color: #94A3B8;")
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        
        form_layout.addRow(confirm_password_label, self.confirm_password_input)
        
        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self.save_profile)
        
        form_layout.addRow("", save_btn)
        
        tab_layout.addWidget(form_frame)
        tab_layout.addStretch()
    
    def setup_app_settings_tab(self):
        """
        Set up the application settings tab.
        """
        # Tab layout
        tab_layout = QVBoxLayout(self.app_settings_tab)
        tab_layout.setContentsMargins(20, 20, 20, 20)
        tab_layout.setSpacing(20)
        
        # Theme settings
        theme_frame = QFrame()
        theme_frame.setObjectName("themeFrame")
        theme_frame.setStyleSheet("""
            #themeFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        theme_layout = QVBoxLayout(theme_frame)
        theme_layout.setContentsMargins(20, 20, 20, 20)
        theme_layout.setSpacing(15)
        
        theme_title = QLabel("Theme Settings")
        theme_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        theme_layout.addWidget(theme_title)
        
        # Dark mode toggle
        dark_mode_layout = QHBoxLayout()
        
        dark_mode_label = QLabel("Dark Mode:")
        dark_mode_label.setStyleSheet("color: #94A3B8;")
        
        self.dark_mode_check = QCheckBox()
        self.dark_mode_check.setChecked(True)  # Default to dark mode
        self.dark_mode_check.stateChanged.connect(self.on_dark_mode_changed)
        
        dark_mode_layout.addWidget(dark_mode_label)
        dark_mode_layout.addWidget(self.dark_mode_check)
        dark_mode_layout.addStretch()
        
        theme_layout.addLayout(dark_mode_layout)
        
        tab_layout.addWidget(theme_frame)
        
        # Auto-refresh settings
        refresh_frame = QFrame()
        refresh_frame.setObjectName("refreshFrame")
        refresh_frame.setStyleSheet("""
            #refreshFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        refresh_layout = QVBoxLayout(refresh_frame)
        refresh_layout.setContentsMargins(20, 20, 20, 20)
        refresh_layout.setSpacing(15)
        
        refresh_title = QLabel("Auto-Refresh Settings")
        refresh_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        refresh_layout.addWidget(refresh_title)
        
        # Auto-refresh interval
        interval_layout = QHBoxLayout()
        
        interval_label = QLabel("Refresh Interval (seconds):")
        interval_label.setStyleSheet("color: #94A3B8;")
        
        self.interval_input = QSpinBox()
        self.interval_input.setRange(10, 300)
        self.interval_input.setValue(config.AUTO_REFRESH_INTERVAL)
        self.interval_input.setStyleSheet("""
            QSpinBox {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
            }
            QSpinBox:focus {
                border: 1px solid #3B82F6;
            }
        """)
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_input)
        interval_layout.addStretch()
        
        refresh_layout.addLayout(interval_layout)
        
        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self.save_app_settings)
        
        refresh_layout.addWidget(save_btn)
        
        tab_layout.addWidget(refresh_frame)
        tab_layout.addStretch()
    
    def save_profile(self):
        """
        Save user profile changes.
        """
        # Get form values
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        full_name = self.full_name_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validate required fields
        if not username:
            QMessageBox.warning(self, "Validation Error", "Username is required.")
            return
        
        if not email:
            QMessageBox.warning(self, "Validation Error", "Email is required.")
            return
        
        if not full_name:
            QMessageBox.warning(self, "Validation Error", "Full name is required.")
            return
        
        # Validate password
        if password:
            if password != confirm_password:
                QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
                return
            
            if len(password) < 6:
                QMessageBox.warning(self, "Validation Error", "Password must be at least 6 characters.")
                return
        
        try:
            db = SessionLocal()
            
            # Check if username is already in use
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user and existing_user.id != self.user.id:
                QMessageBox.warning(self, "Validation Error", "Username is already in use.")
                return
            
            # Check if email is already in use
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user and existing_user.id != self.user.id:
                QMessageBox.warning(self, "Validation Error", "Email is already in use.")
                return
            
            # Update user
            user = db.query(User).filter(User.id == self.user.id).first()
            
            user.username = username
            user.email = email
            user.full_name = full_name
            
            if password:
                hashed_password = bcrypt.hashpw(
                    password.encode('utf-8'), 
                    bcrypt.gensalt()
                ).decode('utf-8')
                user.hashed_password = hashed_password
            
            user.updated_at = datetime.datetime.utcnow()
            
            db.commit()
            
            # Update local user object
            self.user = user
            
            QMessageBox.information(self, "Success", "Profile updated successfully.")
            
            logging.info(f"User {user.username} profile updated")
        except Exception as e:
            logging.error(f"Error updating profile: {str(e)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
        finally:
            db.close()
    
    def save_app_settings(self):
        """
        Save application settings.
        """
        # Get form values
        auto_refresh_interval = self.interval_input.value()
        
        # In a real application, this would update the config file
        # For this demo, we'll just show a message
        QMessageBox.information(self, "Success", "Settings updated successfully.")
        
        logging.info("Application settings updated")
    
    def on_dark_mode_changed(self, state):
        """
        Handle dark mode toggle.
        
        Args:
            state: The checkbox state.
        """
        is_dark_mode = state == Qt.Checked
        self.theme_changed.emit(is_dark_mode)
