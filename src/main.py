"""
Main entry point for the application.

This module initializes the application, sets up the database,
loads translations, and shows the login window.
"""
import sys
import os
import logging
import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from database.base import init_db
from database.init_db import setup_database
from views.login_window import LoginWindow
from views.main_window import MainWindow
from utils.logger import logger
from utils.error_handlers import install_global_exception_handler
from utils.i18n import load_translations, set_language
from utils.performance import optimize_imports, Timer
import config


def create_resources_dirs():
    """
    Create resources directories if they don't exist.
    """
    with Timer("create_resources_dirs"):
        # Create resources directory
        resources_dir = os.path.join("src", "resources")
        os.makedirs(resources_dir, exist_ok=True)
        
        # Create icons directory
        icons_dir = os.path.join(resources_dir, "icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        # Create translations directory
        translations_dir = os.path.join(resources_dir, "translations")
        os.makedirs(translations_dir, exist_ok=True)
        
        # Check if Logo.png exists, if not create a placeholder
        logo_path = os.path.join(icons_dir, "Logo.png")
        if not os.path.exists(logo_path):
            try:
                # Try to create a simple placeholder logo
                from PIL import Image, ImageDraw
                
                # Create a 128x128 image with a blue background
                img = Image.new('RGB', (128, 128), color=(59, 130, 246))
                d = ImageDraw.Draw(img)
                
                # Draw a white "N" in the center
                d.text((50, 50), "N", fill=(255, 255, 255))
                
                # Save the image
                img.save(logo_path)
                
                logger.info(f"Created placeholder logo at {logo_path}")
            except Exception as e:
                logger.warning(f"Could not create placeholder logo: {str(e)}")
        
        # Create other icon files if they don't exist
        icon_files = [
            "dashboard.png", "printer.png", "customer.png", "order.png", 
            "settings.png", "user.png", "logout.png", "add.png", 
            "edit.png", "delete.png", "view.png", "refresh.png", 
            "save.png", "email.png", "reply.png", "revenue.png",
            "products.png", "suppliers.png"
        ]
        
        for icon_file in icon_files:
            icon_path = os.path.join(icons_dir, icon_file)
            if not os.path.exists(icon_path):
                try:
                    # Create a simple colored square as a placeholder
                    from PIL import Image
                    
                    # Choose color based on icon name
                    colors = {
                        "dashboard.png": (59, 130, 246),  # Blue
                        "printer.png": (239, 68, 68),     # Red
                        "customer.png": (245, 158, 11),   # Amber
                        "order.png": (59, 130, 246),      # Blue
                        "settings.png": (107, 114, 128),  # Gray
                        "user.png": (16, 185, 129),       # Emerald
                        "logout.png": (239, 68, 68),      # Red
                        "add.png": (16, 185, 129),        # Emerald
                        "edit.png": (245, 158, 11),       # Amber
                        "delete.png": (239, 68, 68),      # Red
                        "view.png": (59, 130, 246),       # Blue
                        "refresh.png": (16, 185, 129),    # Emerald
                        "save.png": (16, 185, 129),       # Emerald
                        "email.png": (59, 130, 246),      # Blue
                        "reply.png": (245, 158, 11),      # Amber
                        "revenue.png": (16, 185, 129),    # Emerald
                    }
                    
                    color = colors.get(icon_file, (107, 114, 128))  # Default to gray
                    
                    # Create a 32x32 image with the chosen color
                    img = Image.new('RGB', (32, 32), color=color)
                    
                    # Save the image
                    img.save(icon_path)
                    
                    logger.info(f"Created placeholder icon at {icon_path}")
                except Exception as e:
                    logger.warning(f"Could not create placeholder icon {icon_file}: {str(e)}")


def initialize_app():
    """
    Initialize the application.
    
    This function sets up the application, loads translations,
    and installs the global exception handler.
    """
    with Timer("initialize_app"):
        # Install global exception handler
        install_global_exception_handler()
        
        # Create resources directories
        create_resources_dirs()
        
        # Set up database
        setup_database()
        
        # Load translations
        translations_dir = os.path.join("src", "resources", "translations")
        load_translations(translations_dir)
        
        # Set language from config
        set_language(config.DEFAULT_LANGUAGE)
        
        # Preload commonly used modules
        optimize_imports()
        
        logger.info("Application initialized successfully")


def main():
    """
    Main function.
    """
    start_time = datetime.datetime.now()
    logger.info(f"Application starting at {start_time}")
    
    try:
        # Initialize the application
        initialize_app()
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName(config.APP_NAME)
        app.setApplicationVersion(config.APP_VERSION)
        app.setWindowIcon(QIcon("src/resources/icons/logo.png"))
        
        # Set application style
        app.setStyle("Fusion")
        
        # Create login window
        login_window = LoginWindow()
        
        # Connect login successful signal
        login_window.login_successful.connect(lambda user: show_main_window(login_window, user))
        
        # Show login window
        login_window.show()
        
        # Log startup time
        end_time = datetime.datetime.now()
        startup_duration = (end_time - start_time).total_seconds()
        logger.info(f"Application started in {startup_duration:.2f} seconds")
        
        # Run application
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise


def show_main_window(login_window, user):
    """
    Show the main window.
    
    Args:
        login_window: The login window to hide.
        user: The logged in user.
    """
    with Timer("show_main_window"):
        # Hide login window
        login_window.hide()
        
        # Create main window
        main_window = MainWindow(user)
        
        # Show main window
        main_window.show()
        
        logger.info(f"Main window shown for user {user.username}")


if __name__ == "__main__":
    main()
