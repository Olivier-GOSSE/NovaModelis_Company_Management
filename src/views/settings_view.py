"""
Settings view for the application.
"""
import os
import sys
import logging
import datetime
import bcrypt
from utils.translations import set_language, get_current_language, _, AVAILABLE_LANGUAGES
"""
Settings view for the application.
"""
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
        
        # Sales channels tab
        self.sales_channels_tab = QWidget()
        self.setup_sales_channels_tab()
        self.tab_widget.addTab(self.sales_channels_tab, "Sales Channels")
        
        # Email accounts tab
        self.email_accounts_tab = QWidget()
        self.setup_email_accounts_tab()
        self.tab_widget.addTab(self.email_accounts_tab, "Email Accounts")
        
        # Financial settings tab
        self.financial_tab = QWidget()
        self.setup_financial_tab()
        self.tab_widget.addTab(self.financial_tab, "Paramètres Financiers")
        
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
        
        # Theme and appearance settings
        appearance_frame = QFrame()
        appearance_frame.setObjectName("appearanceFrame")
        appearance_frame.setStyleSheet("""
            #appearanceFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        appearance_layout = QVBoxLayout(appearance_frame)
        appearance_layout.setContentsMargins(20, 20, 20, 20)
        appearance_layout.setSpacing(15)
        
        appearance_title = QLabel("Appearance Settings")
        appearance_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        appearance_layout.addWidget(appearance_title)
        
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
        
        appearance_layout.addLayout(dark_mode_layout)
        
        # Language selection
        language_layout = QHBoxLayout()
        
        language_label = QLabel("Language:")
        language_label.setStyleSheet("color: #94A3B8;")
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("English")
        self.language_combo.addItem("Français")
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 1px solid #3B82F6;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #475569;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow {
                image: url(src/resources/icons/down.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                selection-background-color: #3B82F6;
                selection-color: #F8FAFC;
            }
        """)
        
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()
        
        appearance_layout.addLayout(language_layout)
        
        # Currency selection
        currency_layout = QHBoxLayout()
        
        currency_label = QLabel("Currency:")
        currency_label.setStyleSheet("color: #94A3B8;")
        
        self.currency_combo = QComboBox()
        self.currency_combo.addItem("€ (Euro)")
        self.currency_combo.addItem("$ (US Dollar)")
        self.currency_combo.addItem("£ (British Pound)")
        self.currency_combo.setStyleSheet("""
            QComboBox {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 1px solid #3B82F6;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #475569;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow {
                image: url(src/resources/icons/down.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                selection-background-color: #3B82F6;
                selection-color: #F8FAFC;
            }
        """)
        
        currency_layout.addWidget(currency_label)
        currency_layout.addWidget(self.currency_combo)
        currency_layout.addStretch()
        
        appearance_layout.addLayout(currency_layout)
        
        tab_layout.addWidget(appearance_frame)
        
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
        language = self.language_combo.currentText()
        currency = self.currency_combo.currentText().split(' ')[0]  # Get just the symbol
        is_dark_mode = self.dark_mode_check.isChecked()
        
        # Log the settings that would be saved
        logging.info(f"Saving settings - Language: {language}, Currency: {currency}, " +
                     f"Dark Mode: {is_dark_mode}, Refresh Interval: {auto_refresh_interval}s")
        
        # In a real application, this would update the config file
        # For this demo, we'll just show a message
        settings_message = (f"Settings updated successfully:\n\n"
                           f"• Language: {language}\n"
                           f"• Currency: {currency}\n"
                           f"• Dark Mode: {'Enabled' if is_dark_mode else 'Disabled'}\n"
                           f"• Refresh Interval: {auto_refresh_interval} seconds")
        
        QMessageBox.information(self, "Success", settings_message)
        
        logging.info("Application settings updated")
    
    def setup_sales_channels_tab(self):
        """
        Set up the sales channels tab with e-commerce platform connections.
        """
        # Tab layout with scroll area for multiple platforms
        tab_layout = QVBoxLayout(self.sales_channels_tab)
        tab_layout.setContentsMargins(20, 20, 20, 20)
        tab_layout.setSpacing(20)
        
        # Scroll area for platforms
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # Header with title and add button
        header_layout = QHBoxLayout()
        
        header_title = QLabel("E-Commerce Platform Connections")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: bold;")
        
        add_platform_btn = QPushButton("Add Platform")
        add_platform_btn.setCursor(Qt.PointingHandCursor)
        add_platform_btn.setIcon(QIcon("src/resources/icons/add.png"))
        add_platform_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        add_platform_btn.clicked.connect(self.add_new_platform)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(add_platform_btn)
        
        scroll_layout.addLayout(header_layout)
        
        # Shopify connection
        shopify_frame = self.create_platform_frame("Shopify", "shopify")
        scroll_layout.addWidget(shopify_frame)
        
        # Amazon connection
        amazon_frame = self.create_platform_frame("Amazon", "amazon")
        scroll_layout.addWidget(amazon_frame)
        
        # eBay connection
        ebay_frame = self.create_platform_frame("eBay", "ebay")
        scroll_layout.addWidget(ebay_frame)
        
        # Cdiscount connection
        cdiscount_frame = self.create_platform_frame("Cdiscount", "cdiscount")
        scroll_layout.addWidget(cdiscount_frame)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)
    
    def create_platform_frame(self, platform_name, platform_id):
        """
        Create a frame for a specific e-commerce platform.
        
        Args:
            platform_name: The display name of the platform.
            platform_id: The identifier for the platform.
            
        Returns:
            QFrame: The configured frame for the platform.
        """
        platform_frame = QFrame()
        platform_frame.setObjectName(f"{platform_id}Frame")
        platform_frame.setStyleSheet(f"""
            #{platform_id}Frame {{
                background-color: #1E293B;
                border-radius: 8px;
            }}
        """)
        
        platform_layout = QVBoxLayout(platform_frame)
        platform_layout.setContentsMargins(20, 20, 20, 20)
        platform_layout.setSpacing(15)
        
        # Header with platform name and toggle
        header_layout = QHBoxLayout()
        
        platform_title = QLabel(platform_name)
        platform_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        enabled_check = QCheckBox("Enabled")
        enabled_check.setStyleSheet("color: #94A3B8;")
        
        header_layout.addWidget(platform_title)
        header_layout.addStretch()
        header_layout.addWidget(enabled_check)
        
        platform_layout.addLayout(header_layout)
        
        # Form for connection details
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # API Key / Client ID
        api_key_label = QLabel("API Key / Client ID:")
        api_key_label.setStyleSheet("color: #94A3B8;")
        
        api_key_input = QLineEdit()
        api_key_input.setStyleSheet("""
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
        
        form_layout.addRow(api_key_label, api_key_input)
        
        # API Secret / Client Secret
        api_secret_label = QLabel("API Secret / Client Secret:")
        api_secret_label.setStyleSheet("color: #94A3B8;")
        
        api_secret_input = QLineEdit()
        api_secret_input.setEchoMode(QLineEdit.Password)
        api_secret_input.setStyleSheet("""
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
        
        form_layout.addRow(api_secret_label, api_secret_input)
        
        # Store URL / Endpoint
        store_url_label = QLabel("Store URL / Endpoint:")
        store_url_label.setStyleSheet("color: #94A3B8;")
        
        store_url_input = QLineEdit()
        store_url_input.setStyleSheet("""
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
        
        form_layout.addRow(store_url_label, store_url_input)
        
        # Additional fields specific to the platform
        if platform_id == "shopify":
            # Shopify specific - Access Token
            access_token_label = QLabel("Access Token:")
            access_token_label.setStyleSheet("color: #94A3B8;")
            
            access_token_input = QLineEdit()
            access_token_input.setStyleSheet("""
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
            
            form_layout.addRow(access_token_label, access_token_input)
        
        elif platform_id == "amazon":
            # Amazon specific - Marketplace ID
            marketplace_label = QLabel("Marketplace ID:")
            marketplace_label.setStyleSheet("color: #94A3B8;")
            
            marketplace_input = QLineEdit()
            marketplace_input.setStyleSheet("""
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
            
            form_layout.addRow(marketplace_label, marketplace_input)
            
            # Amazon specific - Seller ID
            seller_id_label = QLabel("Seller ID:")
            seller_id_label.setStyleSheet("color: #94A3B8;")
            
            seller_id_input = QLineEdit()
            seller_id_input.setStyleSheet("""
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
            
            form_layout.addRow(seller_id_label, seller_id_input)
        
        platform_layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        test_btn = QPushButton("Test Connection")
        test_btn.setCursor(Qt.PointingHandCursor)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #64748B;
            }
            QPushButton:pressed {
                background-color: #334155;
            }
        """)
        
        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        
        remove_btn = QPushButton("Remove")
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
        """)
        
        buttons_layout.addWidget(test_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(remove_btn)
        
        platform_layout.addLayout(buttons_layout)
        
        return platform_frame
    
    def add_new_platform(self):
        """
        Add a new e-commerce platform connection.
        """
        # In a real application, this would show a dialog to select a platform type
        # and then add a new platform frame to the scroll area
        # For this demo, we'll just show a message
        QMessageBox.information(self, "Add Platform", "This would allow adding a new e-commerce platform connection.")
    
    def setup_email_accounts_tab(self):
        """
        Set up the email accounts tab with email connection settings.
        """
        # Tab layout with scroll area for multiple email accounts
        tab_layout = QVBoxLayout(self.email_accounts_tab)
        tab_layout.setContentsMargins(20, 20, 20, 20)
        tab_layout.setSpacing(20)
        
        # Scroll area for email accounts
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # Header with title and add button
        header_layout = QHBoxLayout()
        
        header_title = QLabel("Email Account Connections")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: bold;")
        
        add_email_btn = QPushButton("Add Email Account")
        add_email_btn.setCursor(Qt.PointingHandCursor)
        add_email_btn.setIcon(QIcon("src/resources/icons/add.png"))
        add_email_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        add_email_btn.clicked.connect(self.add_new_email_account)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(add_email_btn)
        
        scroll_layout.addLayout(header_layout)
        
        # Company main email
        company_email_frame = self.create_email_account_frame("Company Main", "company_main", "IMAP/POP3")
        scroll_layout.addWidget(company_email_frame)
        
        # Support email
        support_email_frame = self.create_email_account_frame("Support", "support", "IMAP/POP3")
        scroll_layout.addWidget(support_email_frame)
        
        # Sales email
        sales_email_frame = self.create_email_account_frame("Sales", "sales", "IMAP/POP3")
        scroll_layout.addWidget(sales_email_frame)
        
        # Gmail account
        gmail_frame = self.create_email_account_frame("Gmail", "gmail", "OAuth2")
        scroll_layout.addWidget(gmail_frame)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)
    
    def create_email_account_frame(self, account_name, account_id, auth_type):
        """
        Create a frame for a specific email account.
        
        Args:
            account_name: The display name of the email account.
            account_id: The identifier for the email account.
            auth_type: The authentication type (IMAP/POP3 or OAuth2).
            
        Returns:
            QFrame: The configured frame for the email account.
        """
        email_frame = QFrame()
        email_frame.setObjectName(f"{account_id}Frame")
        email_frame.setStyleSheet(f"""
            #{account_id}Frame {{
                background-color: #1E293B;
                border-radius: 8px;
            }}
        """)
        
        email_layout = QVBoxLayout(email_frame)
        email_layout.setContentsMargins(20, 20, 20, 20)
        email_layout.setSpacing(15)
        
        # Header with account name and toggle
        header_layout = QHBoxLayout()
        
        account_title = QLabel(account_name)
        account_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        enabled_check = QCheckBox("Enabled")
        enabled_check.setStyleSheet("color: #94A3B8;")
        
        header_layout.addWidget(account_title)
        header_layout.addStretch()
        header_layout.addWidget(enabled_check)
        
        email_layout.addLayout(header_layout)
        
        # Form for connection details
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Email address
        email_label = QLabel("Email Address:")
        email_label.setStyleSheet("color: #94A3B8;")
        
        email_input = QLineEdit()
        email_input.setStyleSheet("""
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
        
        form_layout.addRow(email_label, email_input)
        
        # Display name
        display_name_label = QLabel("Display Name:")
        display_name_label.setStyleSheet("color: #94A3B8;")
        
        display_name_input = QLineEdit()
        display_name_input.setStyleSheet("""
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
        
        form_layout.addRow(display_name_label, display_name_input)
        
        if auth_type == "IMAP/POP3":
            # Password
            password_label = QLabel("Password:")
            password_label.setStyleSheet("color: #94A3B8;")
            
            password_input = QLineEdit()
            password_input.setEchoMode(QLineEdit.Password)
            password_input.setStyleSheet("""
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
            
            form_layout.addRow(password_label, password_input)
            
            # Incoming server
            incoming_server_label = QLabel("Incoming Server:")
            incoming_server_label.setStyleSheet("color: #94A3B8;")
            
            incoming_server_input = QLineEdit()
            incoming_server_input.setStyleSheet("""
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
            
            form_layout.addRow(incoming_server_label, incoming_server_input)
            
            # Incoming port
            incoming_port_label = QLabel("Incoming Port:")
            incoming_port_label.setStyleSheet("color: #94A3B8;")
            
            incoming_port_input = QSpinBox()
            incoming_port_input.setRange(1, 65535)
            incoming_port_input.setValue(993)  # Default IMAP SSL port
            incoming_port_input.setStyleSheet("""
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
            
            form_layout.addRow(incoming_port_label, incoming_port_input)
            
            # Outgoing server
            outgoing_server_label = QLabel("Outgoing Server:")
            outgoing_server_label.setStyleSheet("color: #94A3B8;")
            
            outgoing_server_input = QLineEdit()
            outgoing_server_input.setStyleSheet("""
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
            
            form_layout.addRow(outgoing_server_label, outgoing_server_input)
            
            # Outgoing port
            outgoing_port_label = QLabel("Outgoing Port:")
            outgoing_port_label.setStyleSheet("color: #94A3B8;")
            
            outgoing_port_input = QSpinBox()
            outgoing_port_input.setRange(1, 65535)
            outgoing_port_input.setValue(587)  # Default SMTP TLS port
            outgoing_port_input.setStyleSheet("""
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
            
            form_layout.addRow(outgoing_port_label, outgoing_port_input)
            
            # SSL/TLS
            ssl_label = QLabel("Use SSL/TLS:")
            ssl_label.setStyleSheet("color: #94A3B8;")
            
            ssl_check = QCheckBox()
            ssl_check.setChecked(True)
            
            form_layout.addRow(ssl_label, ssl_check)
        
        elif auth_type == "OAuth2":
            # Client ID
            client_id_label = QLabel("Client ID:")
            client_id_label.setStyleSheet("color: #94A3B8;")
            
            client_id_input = QLineEdit()
            client_id_input.setStyleSheet("""
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
            
            form_layout.addRow(client_id_label, client_id_input)
            
            # Client Secret
            client_secret_label = QLabel("Client Secret:")
            client_secret_label.setStyleSheet("color: #94A3B8;")
            
            client_secret_input = QLineEdit()
            client_secret_input.setEchoMode(QLineEdit.Password)
            client_secret_input.setStyleSheet("""
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
            
            form_layout.addRow(client_secret_label, client_secret_input)
            
            # Refresh Token
            refresh_token_label = QLabel("Refresh Token:")
            refresh_token_label.setStyleSheet("color: #94A3B8;")
            
            refresh_token_input = QLineEdit()
            refresh_token_input.setEchoMode(QLineEdit.Password)
            refresh_token_input.setStyleSheet("""
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
            
            form_layout.addRow(refresh_token_label, refresh_token_input)
            
            # Authorize button
            authorize_btn = QPushButton("Authorize")
            authorize_btn.setCursor(Qt.PointingHandCursor)
            authorize_btn.setStyleSheet("""
                QPushButton {
                    background-color: #475569;
                    color: #F8FAFC;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 12px;
                }
                QPushButton:hover {
                    background-color: #64748B;
                }
                QPushButton:pressed {
                    background-color: #334155;
                }
            """)
            
            form_layout.addRow("", authorize_btn)
        
        email_layout.addLayout(form_layout)
        
        # Check frequency
        check_freq_layout = QHBoxLayout()
        
        check_freq_label = QLabel("Check Frequency (minutes):")
        check_freq_label.setStyleSheet("color: #94A3B8;")
        
        check_freq_input = QSpinBox()
        check_freq_input.setRange(1, 60)
        check_freq_input.setValue(5)  # Default to 5 minutes
        check_freq_input.setStyleSheet("""
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
        
        check_freq_layout.addWidget(check_freq_label)
        check_freq_layout.addWidget(check_freq_input)
        check_freq_layout.addStretch()
        
        email_layout.addLayout(check_freq_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        test_btn = QPushButton("Test Connection")
        test_btn.setCursor(Qt.PointingHandCursor)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #64748B;
            }
            QPushButton:pressed {
                background-color: #334155;
            }
        """)
        
        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        
        remove_btn = QPushButton("Remove")
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
        """)
        
        buttons_layout.addWidget(test_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(remove_btn)
        
        email_layout.addLayout(buttons_layout)
        
        return email_frame
    
    def add_new_email_account(self):
        """
        Add a new email account connection.
        """
        # In a real application, this would show a dialog to select an email account type
        # and then add a new email account frame to the scroll area
        # For this demo, we'll just show a message
        QMessageBox.information(self, "Add Email Account", "This would allow adding a new email account connection.")
    
    def setup_financial_tab(self):
        """
        Set up the financial settings tab with tax and margin parameters.
        """
        # Tab layout
        tab_layout = QVBoxLayout(self.financial_tab)
        tab_layout.setContentsMargins(20, 20, 20, 20)
        tab_layout.setSpacing(20)
        
        # Tax settings frame
        tax_frame = QFrame()
        tax_frame.setObjectName("taxFrame")
        tax_frame.setStyleSheet("""
            #taxFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        tax_layout = QVBoxLayout(tax_frame)
        tax_layout.setContentsMargins(20, 20, 20, 20)
        tax_layout.setSpacing(15)
        
        tax_title = QLabel("Paramètres de Taxes")
        tax_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        tax_layout.addWidget(tax_title)
        
        # Tax form
        tax_form_layout = QFormLayout()
        tax_form_layout.setSpacing(12)
        
        # TVA (Value Added Tax)
        vat_label = QLabel("TVA (%):")
        vat_label.setStyleSheet("color: #94A3B8;")
        
        self.vat_input = QSpinBox()
        self.vat_input.setRange(0, 100)
        self.vat_input.setValue(20)  # Default to 20% (common in many countries)
        self.vat_input.setSuffix("%")
        self.vat_input.setStyleSheet("""
            QSpinBox {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
                min-width: 100px;
            }
            QSpinBox:focus {
                border: 1px solid #3B82F6;
            }
        """)
        
        tax_form_layout.addRow(vat_label, self.vat_input)
        
        # IS (Corporate Tax)
        is_label = QLabel("IS (%):")
        is_label.setStyleSheet("color: #94A3B8;")
        
        self.is_input = QSpinBox()
        self.is_input.setRange(0, 100)
        self.is_input.setValue(25)  # Default to 25% (common corporate tax rate)
        self.is_input.setSuffix("%")
        self.is_input.setStyleSheet("""
            QSpinBox {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
                min-width: 100px;
            }
            QSpinBox:focus {
                border: 1px solid #3B82F6;
            }
        """)
        
        tax_form_layout.addRow(is_label, self.is_input)
        
        tax_layout.addLayout(tax_form_layout)
        
        tab_layout.addWidget(tax_frame)
        
        # Margin settings frame
        margin_frame = QFrame()
        margin_frame.setObjectName("marginFrame")
        margin_frame.setStyleSheet("""
            #marginFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        margin_layout = QVBoxLayout(margin_frame)
        margin_layout.setContentsMargins(20, 20, 20, 20)
        margin_layout.setSpacing(15)
        
        # Header with title and add button
        margin_header = QHBoxLayout()
        
        margin_title = QLabel("Paramètres de Marge")
        margin_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        add_param_btn = QPushButton("Ajouter un paramètre")
        add_param_btn.setCursor(Qt.PointingHandCursor)
        add_param_btn.setIcon(QIcon("src/resources/icons/add.png"))
        add_param_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        add_param_btn.clicked.connect(self.add_margin_parameter)
        
        margin_header.addWidget(margin_title)
        margin_header.addStretch()
        margin_header.addWidget(add_param_btn)
        
        margin_layout.addLayout(margin_header)
        
        # Default margin
        margin_form_layout = QFormLayout()
        margin_form_layout.setSpacing(12)
        
        # Default margin percentage
        default_margin_label = QLabel("Marge par défaut (%):")
        default_margin_label.setStyleSheet("color: #94A3B8;")
        
        self.default_margin_input = QSpinBox()
        self.default_margin_input.setRange(0, 1000)
        self.default_margin_input.setValue(30)  # Default to 30%
        self.default_margin_input.setSuffix("%")
        self.default_margin_input.setStyleSheet("""
            QSpinBox {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
                min-width: 100px;
            }
            QSpinBox:focus {
                border: 1px solid #3B82F6;
            }
        """)
        
        margin_form_layout.addRow(default_margin_label, self.default_margin_input)
        
        margin_layout.addLayout(margin_form_layout)
        
        # Additional margin parameters (container)
        self.additional_params_container = QWidget()
        additional_params_layout = QVBoxLayout(self.additional_params_container)
        additional_params_layout.setContentsMargins(0, 0, 0, 0)
        additional_params_layout.setSpacing(10)
        
        # Add a few example parameters
        param1_layout = self.create_margin_parameter_layout("Frais de livraison", 5)
        additional_params_layout.addLayout(param1_layout)
        
        param2_layout = self.create_margin_parameter_layout("Frais de marketing", 3)
        additional_params_layout.addLayout(param2_layout)
        
        margin_layout.addWidget(self.additional_params_container)
        
        # Save button
        save_btn = QPushButton("Enregistrer les modifications")
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
        save_btn.clicked.connect(self.save_financial_settings)
        
        margin_layout.addWidget(save_btn)
        
        tab_layout.addWidget(margin_frame)
        tab_layout.addStretch()
    
    def create_margin_parameter_layout(self, param_name="", param_value=0):
        """
        Create a layout for a margin parameter with name, value, and remove button.
        
        Args:
            param_name: The name of the parameter.
            param_value: The value of the parameter.
            
        Returns:
            QHBoxLayout: The layout containing the parameter controls.
        """
        param_layout = QHBoxLayout()
        param_layout.setSpacing(10)
        
        # Parameter name
        name_input = QLineEdit()
        name_input.setText(param_name)
        name_input.setPlaceholderText("Nom du paramètre")
        name_input.setStyleSheet("""
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
        
        # Parameter value
        value_input = QSpinBox()
        value_input.setRange(0, 100)
        value_input.setValue(param_value)
        value_input.setSuffix("%")
        value_input.setStyleSheet("""
            QSpinBox {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
                min-width: 80px;
            }
            QSpinBox:focus {
                border: 1px solid #3B82F6;
            }
        """)
        
        # Remove button
        remove_btn = QPushButton()
        remove_btn.setIcon(QIcon("src/resources/icons/delete.png"))
        remove_btn.setIconSize(QSize(16, 16))
        remove_btn.setFixedSize(36, 36)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #EF4444;
            }
        """)
        remove_btn.setToolTip("Supprimer ce paramètre")
        remove_btn.clicked.connect(lambda: self.remove_margin_parameter(param_layout))
        
        param_layout.addWidget(name_input, 3)  # 3 parts for name
        param_layout.addWidget(value_input, 1)  # 1 part for value
        param_layout.addWidget(remove_btn, 0)  # Fixed width for button
        
        return param_layout
    
    def add_margin_parameter(self):
        """
        Add a new margin parameter to the list.
        """
        # Get the layout of the additional parameters container
        container_layout = self.additional_params_container.layout()
        
        # Create a new parameter layout
        new_param_layout = self.create_margin_parameter_layout()
        
        # Add it to the container
        container_layout.addLayout(new_param_layout)
    
    def remove_margin_parameter(self, param_layout):
        """
        Remove a margin parameter from the list.
        
        Args:
            param_layout: The layout containing the parameter to remove.
        """
        # Remove all widgets from the layout
        while param_layout.count():
            item = param_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Delete the layout itself
        param_layout.deleteLater()
    
    def save_financial_settings(self):
        """
        Save the financial settings.
        """
        # Get the values from the form
        vat = self.vat_input.value()
        corporate_tax = self.is_input.value()
        default_margin = self.default_margin_input.value()
        
        # Collect additional parameters
        additional_params = []
        container_layout = self.additional_params_container.layout()
        
        for i in range(container_layout.count()):
            param_layout = container_layout.itemAt(i)
            if param_layout and param_layout.layout():
                # Get the name input (first widget)
                name_input = param_layout.layout().itemAt(0).widget()
                # Get the value input (second widget)
                value_input = param_layout.layout().itemAt(1).widget()
                
                if name_input and value_input and name_input.text().strip():
                    additional_params.append({
                        "name": name_input.text().strip(),
                        "value": value_input.value()
                    })
        
        # In a real application, this would save to a database or config file
        # For this demo, we'll just show a message
        settings_message = (f"Paramètres financiers enregistrés :\n\n"
                           f"• TVA : {vat}%\n"
                           f"• IS : {corporate_tax}%\n"
                           f"• Marge par défaut : {default_margin}%\n")
        
        if additional_params:
            settings_message += "\nParamètres additionnels :\n"
            for param in additional_params:
                settings_message += f"• {param['name']} : {param['value']}%\n"
        
        QMessageBox.information(self, "Succès", settings_message)
        
        logging.info("Financial settings updated")
    
    def on_dark_mode_changed(self, state):
        """
        Handle dark mode toggle.
        
        Args:
            state: The checkbox state.
        """
        is_dark_mode = state == Qt.Checked
        self.theme_changed.emit(is_dark_mode)
