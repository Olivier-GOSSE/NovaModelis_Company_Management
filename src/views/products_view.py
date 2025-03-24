"""
Products view for the application.
"""
import os
import sys
import logging
import datetime
import csv
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal
from models.product import Product


class ProductThumbnail(QWidget):
    """
    Widget for displaying a product thumbnail.
    """
    def __init__(self, product, parent=None):
        super().__init__(parent)
        
        self.product = product
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)  # Réduire l'espacement entre les éléments
        main_layout.setAlignment(Qt.AlignCenter)  # Centrer horizontalement
        
        # Product name
        self.name_label = QLabel(self.product.name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: #F8FAFC; font-weight: bold;")
        self.name_label.setWordWrap(True)
        self.name_label.setFixedHeight(20)  # Hauteur réduite pour le nom
        
        # Image frame
        self.image_frame = QFrame()
        self.image_frame.setObjectName("imageFrame")
        self.image_frame.setStyleSheet("""
            #imageFrame {
                background-color: #1E293B;
                border-radius: 8px;
                border: 1px solid #334155;
            }
        """)
        self.image_frame.setFixedSize(150, 150)
        
        image_layout = QVBoxLayout(self.image_frame)
        image_layout.setContentsMargins(5, 5, 5, 5)
        image_layout.setSpacing(0)
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(140, 140)
        
        # Load image
        if self.product.image_path and os.path.exists(self.product.image_path):
            pixmap = QPixmap(self.product.image_path)
        else:
            # Use placeholder image
            pixmap = QPixmap("src/resources/icons/product_placeholder.png")
        
        self.image_label.setPixmap(pixmap)
        
        image_layout.addWidget(self.image_label)
        
        # Réorganisation pour mettre le nom au-dessus de l'image
        main_layout.addWidget(self.name_label)
        main_layout.addWidget(self.image_frame)


class ProductsView(QWidget):
    """
    Products view for the application.
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
        
        header_title = QLabel("Products")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_products)
        
        search_layout.addWidget(self.search_input)
        
        # Add product button
        self.add_btn = QPushButton("Add Product")
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
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addLayout(search_layout)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(header_layout)
        
        # Products flow layout
        self.products_scroll = QScrollArea()
        self.products_scroll.setWidgetResizable(True)
        self.products_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #0F172A;
                border: none;
            }
        """)
        
        self.products_widget = QWidget()
        self.products_widget.setStyleSheet("background-color: #0F172A;")
        
        # Utiliser un QHBoxLayout au lieu de QGridLayout pour aligner les produits horizontalement
        self.products_layout = QHBoxLayout(self.products_widget)
        self.products_layout.setContentsMargins(10, 10, 10, 10)
        self.products_layout.setSpacing(20)
        self.products_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # Aligner en haut à gauche
        
        self.products_scroll.setWidget(self.products_widget)
        
        main_layout.addWidget(self.products_scroll)
    
    def refresh_data(self):
        """
        Refresh the products data.
        """
        try:
            # Clear products layout
            for i in reversed(range(self.products_layout.count())):
                widget = self.products_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # Get products
            products = self.db.query(Product).all()
            
            # Add products to layout horizontalement
            for product in products:
                thumbnail = ProductThumbnail(product)
                self.products_layout.addWidget(thumbnail)
            
            # Ajouter un stretch à la fin pour que les produits restent alignés à gauche
            self.products_layout.addStretch()
            
            logging.info("Products view refreshed")
        except Exception as e:
            logging.error(f"Error refreshing products data: {str(e)}")
    
    def filter_products(self):
        """
        Filter products based on search text.
        """
        search_text = self.search_input.text().lower()
        
        # Hide/show products based on search text
        for i in range(self.products_layout.count()):
            widget = self.products_layout.itemAt(i).widget()
            if isinstance(widget, ProductThumbnail):
                product_name = widget.product.name.lower()
                widget.setVisible(search_text in product_name)
