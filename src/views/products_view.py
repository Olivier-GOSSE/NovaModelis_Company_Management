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
    QFrame, QGridLayout, QScrollArea, QLineEdit, QDialog,
    QComboBox, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal
from models.product import Product


class ProductDetailsDialog(QDialog):
    """
    Dialog for displaying product details.
    """
    def __init__(self, product, parent=None):
        # Pour le glissement de la fenêtre
        self.dragging = False
        self.drag_position = None
        
        super().__init__(parent)
        
        self.product = product
        
        # Supprimer le cadre et la barre de titre de la fenêtre
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        # Définir la transparence de la fenêtre
        self.setWindowOpacity(0.9)  # 10% de transparence
        
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
    
    def mousePressEvent(self, event):
        """
        Gérer l'événement de pression de la souris pour le glissement de la fenêtre.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """
        Gérer l'événement de déplacement de la souris pour le glissement de la fenêtre.
        """
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """
        Gérer l'événement de relâchement de la souris pour le glissement de la fenêtre.
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
        
        # Barre de titre personnalisée
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(0, 0, 0, 10)
        
        # Titre
        title_label = QLabel(f"Détails du produit: {self.product.name}")
        title_label.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: bold;")
        
        # Bouton de fermeture
        close_btn = QPushButton("×")  # Signe de multiplication Unicode comme icône de fermeture
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
        
        # Product header
        header_layout = QHBoxLayout()
        
        # Product image
        self.image_frame = QFrame()
        self.image_frame.setObjectName("imageFrame")
        self.image_frame.setStyleSheet("""
            #imageFrame {
                background-color: rgba(30, 41, 59, 0.9);
                border-radius: 12px;
                border: 1px solid #334155;
            }
        """)
        self.image_frame.setFixedSize(200, 200)
        
        image_layout = QVBoxLayout(self.image_frame)
        image_layout.setContentsMargins(10, 10, 10, 10)
        image_layout.setSpacing(0)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(180, 180)
        
        # Load image
        if self.product.image_path and os.path.exists(self.product.image_path):
            pixmap = QPixmap(self.product.image_path)
        else:
            # Use placeholder image
            pixmap = QPixmap("src/resources/icons/product_placeholder.png")
        
        self.image_label.setPixmap(pixmap)
        
        image_layout.addWidget(self.image_label)
        
        # Product info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        
        self.name_label = QLabel(self.product.name)
        self.name_label.setStyleSheet("color: #F8FAFC; font-size: 24px; font-weight: bold;")
        
        self.description_label = QLabel(self.product.description or "Aucune description disponible")
        self.description_label.setStyleSheet("color: #94A3B8;")
        self.description_label.setWordWrap(True)
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.description_label)
        info_layout.addStretch()
        
        header_layout.addWidget(self.image_frame)
        header_layout.addSpacing(20)
        header_layout.addLayout(info_layout)
        
        main_layout.addLayout(header_layout)
        
        # Product details
        details_frame = QFrame()
        details_frame.setObjectName("detailsFrame")
        details_frame.setStyleSheet("""
            #detailsFrame {
                background-color: rgba(30, 41, 59, 0.9);
                border-radius: 12px;
            }
        """)
        
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(20, 20, 20, 20)
        details_layout.setSpacing(15)
        
        details_title = QLabel("Détails du produit")
        details_title.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: bold;")
        
        # Details grid
        details_grid = QGridLayout()
        details_grid.setColumnStretch(1, 1)
        details_grid.setSpacing(10)
        
        # Production time
        details_grid.addWidget(QLabel("Temps de production:"), 0, 0)
        self.production_time_label = QLabel(f"{self.product.production_time} heures")
        self.production_time_label.setStyleSheet("color: #F8FAFC;")
        details_grid.addWidget(self.production_time_label, 0, 1)
        
        # Production cost
        details_grid.addWidget(QLabel("Coût de production:"), 1, 0)
        self.production_cost_label = QLabel(f"{self.product.production_cost} €")
        self.production_cost_label.setStyleSheet("color: #F8FAFC;")
        details_grid.addWidget(self.production_cost_label, 1, 1)
        
        # Initial quantity
        details_grid.addWidget(QLabel("Quantité initiale:"), 2, 0)
        self.initial_quantity_label = QLabel(f"{self.product.initial_quantity}")
        self.initial_quantity_label.setStyleSheet("color: #F8FAFC;")
        details_grid.addWidget(self.initial_quantity_label, 2, 1)
        
        # Total sales
        details_grid.addWidget(QLabel("Ventes totales:"), 3, 0)
        self.total_sales_label = QLabel(f"{self.product.total_sales}")
        self.total_sales_label.setStyleSheet("color: #F8FAFC;")
        details_grid.addWidget(self.total_sales_label, 3, 1)
        
        # Countries
        details_grid.addWidget(QLabel("Pays:"), 4, 0)
        countries_text = ", ".join([country.name for country in self.product.countries]) if self.product.countries else "Aucun pays"
        self.countries_label = QLabel(countries_text)
        self.countries_label.setStyleSheet("color: #F8FAFC;")
        details_grid.addWidget(self.countries_label, 4, 1)
        
        details_layout.addWidget(details_title)
        details_layout.addLayout(details_grid)
        
        main_layout.addWidget(details_frame)
        
        # Tabs for sales data
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: rgba(30, 41, 59, 0.9);
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
                background-color: rgba(30, 41, 59, 0.9);
                color: #F8FAFC;
            }
            QTabBar::tab:hover:!selected {
                background-color: rgba(30, 41, 59, 0.9);
                color: #F8FAFC;
            }
        """)
        
        # Sales by country tab
        self.sales_tab = QWidget()
        self.setup_sales_tab()
        self.tabs.addTab(self.sales_tab, "Ventes par pays")
        
        main_layout.addWidget(self.tabs)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
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
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def setup_sales_tab(self):
        """
        Set up the sales by country tab.
        """
        tab_layout = QVBoxLayout(self.sales_tab)
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.setSpacing(15)
        
        # Sales table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(2)
        self.sales_table.setHorizontalHeaderLabels(["Pays", "Quantité vendue"])
        self.sales_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.sales_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.sales_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(30, 41, 59, 0.9);
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
            }
            QHeaderView::section {
                background-color: #334155;
                color: #F8FAFC;
                border: none;
                padding: 5px;
            }
            QTableWidget::item {
                border: none;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3B82F6;
            }
        """)
        
        # Populate sales table
        sales_by_country = self.product.sales_by_country
        self.sales_table.setRowCount(len(sales_by_country))
        
        for i, (country, quantity) in enumerate(sales_by_country.items()):
            country_item = QTableWidgetItem(country)
            country_item.setFlags(country_item.flags() & ~Qt.ItemIsEditable)
            self.sales_table.setItem(i, 0, country_item)
            
            quantity_item = QTableWidgetItem(str(quantity))
            quantity_item.setFlags(quantity_item.flags() & ~Qt.ItemIsEditable)
            quantity_item.setTextAlignment(Qt.AlignCenter)
            self.sales_table.setItem(i, 1, quantity_item)
        
        tab_layout.addWidget(self.sales_table)


class ProductThumbnail(QWidget):
    """
    Widget for displaying a product thumbnail.
    """
    clicked = Signal(object)  # Signal émis lorsqu'on clique sur le thumbnail
    
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
        self.name_label.setCursor(Qt.PointingHandCursor)  # Utiliser setCursor au lieu de CSS
        self.name_label.setWordWrap(True)
        self.name_label.setFixedHeight(20)  # Hauteur réduite pour le nom
        
        # Rendre le label cliquable
        self.name_label.mousePressEvent = self.on_name_clicked
        
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
        self.image_frame.setCursor(Qt.PointingHandCursor)  # Utiliser setCursor au lieu de CSS
        self.image_frame.setFixedSize(150, 150)
        
        # Rendre le frame cliquable
        self.image_frame.mousePressEvent = self.on_image_clicked
        
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
    
    def on_name_clicked(self, event):
        """
        Handle click on product name.
        """
        self.clicked.emit(self.product)
    
    def on_image_clicked(self, event):
        """
        Handle click on product image.
        """
        self.clicked.emit(self.product)


class ProductsView(QWidget):
    """
    Products view for the application.
    """
    def __init__(self, db):
        super().__init__()
        
        self.db = db
        self.all_products = []  # Liste de tous les produits pour la recherche
        
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
        
        header_title = QLabel("Produits")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        # Search layout
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher des produits...")
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
        
        # Search category dropdown
        self.category_filter = QComboBox()
        self.category_filter.addItem("Tous", None)
        self.category_filter.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(src/resources/icons/dropdown.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                selection-background-color: #3B82F6;
            }
        """)
        self.category_filter.currentIndexChanged.connect(self.filter_products)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.category_filter)
        
        # Add product button
        self.add_btn = QPushButton("Ajouter un produit")
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
            self.all_products = self.db.query(Product).all()
            
            # Update category filter
            self.update_category_filter()
            
            # Add products to layout horizontalement
            for product in self.all_products:
                thumbnail = ProductThumbnail(product)
                thumbnail.clicked.connect(self.show_product_details)
                self.products_layout.addWidget(thumbnail)
            
            # Ajouter un stretch à la fin pour que les produits restent alignés à gauche
            self.products_layout.addStretch()
            
            logging.info("Products view refreshed")
        except Exception as e:
            logging.error(f"Error refreshing products data: {str(e)}")
    
    def update_category_filter(self):
        """
        Update the category filter with available countries.
        """
        # Save current selection
        current_data = self.category_filter.currentData()
        
        # Clear and re-add "All" option
        self.category_filter.clear()
        self.category_filter.addItem("Tous les pays", None)
        
        # Get all unique countries from products
        countries = set()
        for product in self.all_products:
            for country in product.countries:
                countries.add((country.name, country.id))
        
        # Add countries to filter
        for country_name, country_id in sorted(countries):
            self.category_filter.addItem(country_name, country_id)
        
        # Restore selection if possible
        if current_data is not None:
            index = self.category_filter.findData(current_data)
            if index >= 0:
                self.category_filter.setCurrentIndex(index)
    
    def show_product_details(self, product):
        """
        Show product details dialog.
        
        Args:
            product: The product to show details for.
        """
        dialog = ProductDetailsDialog(product, self)
        dialog.exec()
    
    def filter_products(self):
        """
        Filter products based on search text and category.
        """
        search_text = self.search_input.text().lower()
        selected_country_id = self.category_filter.currentData()
        
        # Hide/show products based on search text and category
        for i in range(self.products_layout.count()):
            widget = self.products_layout.itemAt(i).widget()
            if isinstance(widget, ProductThumbnail):
                product = widget.product
                product_name = product.name.lower()
                
                # Check if product matches search text
                name_match = search_text in product_name
                
                # Check if product matches selected country
                country_match = True
                if selected_country_id is not None:
                    country_match = any(country.id == selected_country_id for country in product.countries)
                
                # Show widget if both conditions are met
                widget.setVisible(name_match and country_match)
