"""
Main window for the application.
"""
import os
import sys
import logging
import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon, QFont

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal
from models import User
from views.dashboard_view import DashboardView
from views.printers_view import PrintersView
from views.customers_view import CustomersView
from views.orders_view import OrdersView
from views.settings_view import SettingsView
import config


class MainWindow(QMainWindow):
    """
    Main window for the application.
    """
    def __init__(self, user):
        super().__init__()
        
        self.user = user
        self.db = SessionLocal()
        
        self.setWindowTitle(config.APP_NAME)
        self.setWindowIcon(QIcon("src/resources/icons/logo.png"))
        
        # Rendre la fenêtre non redimensionnable et en plein écran
        self.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)
        self.showFullScreen()
        
        self.setup_ui()
        self.setup_refresh_timer()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet("""
            #sidebar {
                background-color: #0F172A;
                border-right: 1px solid #1E293B;
            }
        """)
        sidebar.setFixedWidth(220)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo and title
        logo_frame = QFrame()
        logo_frame.setStyleSheet("background-color: #0F172A;")
        logo_frame.setFixedHeight(60)
        
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(15, 0, 15, 0)
        
        logo_label = QLabel()
        logo_label.setPixmap(QIcon("src/resources/icons/logo.png").pixmap(QSize(24, 24)))
        
        title_label = QLabel("NovaModelis")
        title_label.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        logo_layout.addStretch()
        
        sidebar_layout.addWidget(logo_frame)
        
        # Navigation buttons
        nav_frame = QFrame()
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(5)
        
        # Dashboard button
        self.dashboard_btn = QPushButton("Tableau de bord")
        self.dashboard_btn.setIcon(QIcon("src/resources/icons/dashboard.png"))
        self.dashboard_btn.setIconSize(QSize(18, 18))
        self.dashboard_btn.setCursor(Qt.PointingHandCursor)
        self.dashboard_btn.setCheckable(True)
        self.dashboard_btn.setChecked(True)
        self.dashboard_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 4px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1E293B;
                color: #F8FAFC;
            }
            QPushButton:checked {
                background-color: #3B82F6;
                color: #F8FAFC;
            }
        """)
        self.dashboard_btn.clicked.connect(lambda: self.switch_view(0))
        
        # Printers button
        self.printers_btn = QPushButton("Imprimantes")
        self.printers_btn.setIcon(QIcon("src/resources/icons/printer.png"))
        self.printers_btn.setIconSize(QSize(18, 18))
        self.printers_btn.setCursor(Qt.PointingHandCursor)
        self.printers_btn.setCheckable(True)
        self.printers_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 4px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1E293B;
                color: #F8FAFC;
            }
            QPushButton:checked {
                background-color: #3B82F6;
                color: #F8FAFC;
            }
        """)
        self.printers_btn.clicked.connect(lambda: self.switch_view(1))
        
        # Customers button
        self.customers_btn = QPushButton("Clients")
        self.customers_btn.setIcon(QIcon("src/resources/icons/customer.png"))
        self.customers_btn.setIconSize(QSize(18, 18))
        self.customers_btn.setCursor(Qt.PointingHandCursor)
        self.customers_btn.setCheckable(True)
        self.customers_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 4px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1E293B;
                color: #F8FAFC;
            }
            QPushButton:checked {
                background-color: #3B82F6;
                color: #F8FAFC;
            }
        """)
        self.customers_btn.clicked.connect(lambda: self.switch_view(2))
        
        # Orders button
        self.orders_btn = QPushButton("Commandes")
        self.orders_btn.setIcon(QIcon("src/resources/icons/order.png"))
        self.orders_btn.setIconSize(QSize(18, 18))
        self.orders_btn.setCursor(Qt.PointingHandCursor)
        self.orders_btn.setCheckable(True)
        self.orders_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 4px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1E293B;
                color: #F8FAFC;
            }
            QPushButton:checked {
                background-color: #3B82F6;
                color: #F8FAFC;
            }
        """)
        self.orders_btn.clicked.connect(lambda: self.switch_view(3))
        
        # Settings button
        self.settings_btn = QPushButton("Paramètres")
        self.settings_btn.setIcon(QIcon("src/resources/icons/settings.png"))
        self.settings_btn.setIconSize(QSize(18, 18))
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setCheckable(True)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 4px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1E293B;
                color: #F8FAFC;
            }
            QPushButton:checked {
                background-color: #3B82F6;
                color: #F8FAFC;
            }
        """)
        self.settings_btn.clicked.connect(lambda: self.switch_view(4))
        
        nav_layout.addWidget(self.dashboard_btn)
        nav_layout.addWidget(self.printers_btn)
        nav_layout.addWidget(self.customers_btn)
        nav_layout.addWidget(self.orders_btn)
        nav_layout.addStretch()
        
        sidebar_layout.addWidget(nav_frame)
        
        # Settings button in its own frame
        settings_frame = QFrame()
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(10, 0, 10, 0)
        settings_layout.addWidget(self.settings_btn)
        
        sidebar_layout.addWidget(settings_frame)
        
        # User info
        user_frame = QFrame()
        user_frame.setStyleSheet("background-color: #0F172A;")
        user_frame.setFixedHeight(60)
        
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(15, 0, 15, 0)
        
        user_icon = QLabel()
        user_icon.setPixmap(QIcon("src/resources/icons/user.png").pixmap(QSize(24, 24)))
        
        user_label = QLabel(self.user.full_name)
        user_label.setStyleSheet("color: #F8FAFC;")
        
        logout_btn = QPushButton()
        logout_btn.setIcon(QIcon("src/resources/icons/logout.png"))
        logout_btn.setIconSize(QSize(16, 16))
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #1E293B;
            }
        """)
        logout_btn.setToolTip("Déconnexion")
        logout_btn.clicked.connect(self.logout)
        
        user_layout.addWidget(user_icon)
        user_layout.addWidget(user_label)
        user_layout.addStretch()
        user_layout.addWidget(logout_btn)
        
        sidebar_layout.addWidget(user_frame)
        
        # Content area
        content_area = QFrame()
        content_area.setObjectName("contentArea")
        content_area.setStyleSheet("""
            #contentArea {
                background-color: #0F172A;
            }
        """)
        
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Create views
        self.dashboard_view = DashboardView(self.db)
        self.printers_view = PrintersView(self.db)
        self.customers_view = CustomersView(self.db)
        self.orders_view = OrdersView(self.db)
        self.settings_view = SettingsView(self.db, self.user)
        
        # Connect settings view theme changed signal
        self.settings_view.theme_changed.connect(self.on_theme_changed)
        
        # Add views to stacked widget
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.printers_view)
        self.stacked_widget.addWidget(self.customers_view)
        self.stacked_widget.addWidget(self.orders_view)
        self.stacked_widget.addWidget(self.settings_view)
        
        content_layout.addWidget(self.stacked_widget)
        
        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)
    
    def switch_view(self, index):
        """
        Switch to the specified view.
        
        Args:
            index (int): The index of the view to switch to.
        """
        # Update button states
        self.dashboard_btn.setChecked(index == 0)
        self.printers_btn.setChecked(index == 1)
        self.customers_btn.setChecked(index == 2)
        self.orders_btn.setChecked(index == 3)
        self.settings_btn.setChecked(index == 4)
        
        # Switch view
        self.stacked_widget.setCurrentIndex(index)
        
        # Refresh data in the current view
        current_view = self.stacked_widget.currentWidget()
        if hasattr(current_view, 'refresh_data'):
            current_view.refresh_data()
    
    def setup_refresh_timer(self):
        """
        Set up a timer to refresh data periodically.
        """
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_current_view)
        self.refresh_timer.start(config.AUTO_REFRESH_INTERVAL * 1000)  # Convert to milliseconds
    
    def refresh_current_view(self):
        """
        Refresh data in the current view.
        """
        current_view = self.stacked_widget.currentWidget()
        if hasattr(current_view, 'refresh_data'):
            current_view.refresh_data()
    
    def on_theme_changed(self, is_dark_mode):
        """
        Handle theme change.
        
        Args:
            is_dark_mode (bool): True for dark mode, False for light mode.
        """
        # In a real application, this would update the application's theme
        # For this demo, we'll just show a message
        theme_name = "Sombre" if is_dark_mode else "Clair"
        QMessageBox.information(self, "Thème modifié", f"Thème changé en mode {theme_name}.")
    
    def logout(self):
        """
        Handle logout button click.
        """
        reply = QMessageBox.question(
            self, "Déconnexion", "Êtes-vous sûr de vouloir vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()
    
    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        Args:
            event: The key press event.
        """
        # Quitter le mode plein écran avec la touche Échap
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event: The close event.
        """
        # Clean up resources
        self.refresh_timer.stop()
        self.db.close()
        
        # Accept the event
        event.accept()
