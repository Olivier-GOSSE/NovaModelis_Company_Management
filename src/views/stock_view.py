"""
Stock view for the application.
"""
import os
import sys
import logging
import csv
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QTabWidget, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QSpinBox, QDoubleSpinBox, QMessageBox, QDialog, QFormLayout,
    QFileDialog
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont, QColor, QPainter

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from models.product import Product
from models.raw_material import RawMaterial


class AddProductDialog(QDialog):
    """Dialog for adding a new finished product."""
    def __init__(self, db, parent=None):
        # For window dragging
        self.dragging = False
        self.drag_position = None
        
        super().__init__(parent)
        
        self.db = db
        self.production_data = None
        
        # Remove window frame and title bar
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.9)  # 10% transparency
        self.setMinimumWidth(400)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Custom title bar
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(0, 0, 0, 10)
        
        # Title
        title_label = QLabel("Ajouter un Produit Fini")
        title_label.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: bold;")
        
        # Close button
        close_btn = QPushButton("×")
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
        
        layout.addLayout(title_bar_layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Product name
        self.name_input = QLineEdit()
        form_layout.addRow("Nom du produit:", self.name_input)
        
        # SKU
        self.sku_input = QLineEdit()
        form_layout.addRow("SKU:", self.sku_input)
        
        # Category
        self.category_input = QComboBox()
        self.category_input.addItems(["Figurine", "Maquette", "Accessoire", "Autre"])
        self.category_input.setEditable(True)
        form_layout.addRow("Catégorie:", self.category_input)
        
        # Production cost
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 10000)
        self.price_input.setDecimals(2)
        self.price_input.setSuffix(" €")
        self.price_input.setReadOnly(True)
        
        # Details button
        details_btn = QPushButton("Détails")
        details_btn.setCursor(Qt.PointingHandCursor)
        details_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        details_btn.clicked.connect(self.show_details)
        
        # Cost layout with button
        cost_layout = QHBoxLayout()
        cost_layout.addWidget(self.price_input)
        cost_layout.addWidget(details_btn)
        
        form_layout.addRow("Coût de production:", cost_layout)
        
        # Quantity
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 10000)
        form_layout.addRow("Quantité en stock:", self.quantity_input)
        
        # Reorder level
        self.reorder_level_input = QSpinBox()
        self.reorder_level_input.setRange(0, 1000)
        form_layout.addRow("Seuil de réapprovisionnement:", self.reorder_level_input)
        
        # Description
        self.description_input = QLineEdit()
        form_layout.addRow("Description:", self.description_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)
        
        # Apply styles
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
            }
            QLabel {
                color: #94A3B8;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 12px;
                padding: 8px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #3B82F6;
            }
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
            QPushButton#cancelBtn {
                background-color: #475569;
            }
            QPushButton#cancelBtn:hover {
                background-color: #64748B;
            }
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press event for window dragging."""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move event for window dragging."""
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event for window dragging."""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    def show_details(self):
        """Show the product details dialog."""
        from views.product_details_dialog import ProductDetailsDialog
        
        dialog = ProductDetailsDialog(self.db, self)
        
        # If we already have production data, load it into the dialog
        if self.production_data:
            # TODO: Load existing production data into the dialog
            pass
        
        if dialog.exec():
            # Get the production data
            self.production_data = dialog.get_production_data()
            
            # Update the price input
            self.price_input.setValue(self.production_data["production_cost"])
    
    def get_product_data(self):
        """Get the product data from the form."""
        production_time = 0
        if self.production_data:
            production_time = self.production_data["production_time"]
            
        return {
            "name": self.name_input.text(),
            "sku": self.sku_input.text(),
            "category": self.category_input.currentText(),
            "price": self.price_input.value(),
            "quantity": self.quantity_input.value(),
            "reorder_level": self.reorder_level_input.value(),
            "description": self.description_input.text(),
            "production_time": production_time,
            "components": self.production_data["components"] if self.production_data else []
        }


class AddRawMaterialDialog(QDialog):
    """Dialog for adding a new raw material."""
    def __init__(self, parent=None):
        # For window dragging
        self.dragging = False
        self.drag_position = None
        
        super().__init__(parent)
        
        # Remove window frame and title bar
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.9)  # 10% transparency
        self.setMinimumWidth(400)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Custom title bar
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(0, 0, 0, 10)
        
        # Title
        title_label = QLabel("Ajouter une Matière Première")
        title_label.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: bold;")
        
        # Close button
        close_btn = QPushButton("×")
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
        
        layout.addLayout(title_bar_layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Material name
        self.name_input = QLineEdit()
        form_layout.addRow("Nom de la matière:", self.name_input)
        
        # Reference code
        self.ref_code_input = QLineEdit()
        form_layout.addRow("Code de référence:", self.ref_code_input)
        
        # Type
        self.type_input = QComboBox()
        self.type_input.addItems(["Résine", "Plastique", "Métal", "Peinture", "Autre"])
        self.type_input.setEditable(True)
        form_layout.addRow("Type:", self.type_input)
        
        # Unit
        self.unit_input = QComboBox()
        self.unit_input.addItems(["kg", "g", "l", "ml", "unité", "m", "cm"])
        form_layout.addRow("Unité:", self.unit_input)
        
        # Cost per unit
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 10000)
        self.cost_input.setDecimals(2)
        self.cost_input.setSuffix(" €")
        form_layout.addRow("Coût par unité:", self.cost_input)
        
        # Quantity
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0, 100000)
        self.quantity_input.setDecimals(2)
        form_layout.addRow("Quantité en stock:", self.quantity_input)
        
        # Reorder level
        self.reorder_level_input = QDoubleSpinBox()
        self.reorder_level_input.setRange(0, 10000)
        self.reorder_level_input.setDecimals(2)
        form_layout.addRow("Seuil de réapprovisionnement:", self.reorder_level_input)
        
        # Supplier
        self.supplier_input = QLineEdit()
        form_layout.addRow("Fournisseur:", self.supplier_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)
        
        # Apply styles
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
            }
            QLabel {
                color: #94A3B8;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 12px;
                padding: 8px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #3B82F6;
            }
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
            QPushButton#cancelBtn {
                background-color: #475569;
            }
            QPushButton#cancelBtn:hover {
                background-color: #64748B;
            }
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press event for window dragging."""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move event for window dragging."""
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event for window dragging."""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    def get_material_data(self):
        """Get the material data from the form."""
        return {
            "name": self.name_input.text(),
            "ref_code": self.ref_code_input.text(),
            "type": self.type_input.currentText(),
            "unit": self.unit_input.currentText(),
            "cost": self.cost_input.value(),
            "quantity": self.quantity_input.value(),
            "reorder_level": self.reorder_level_input.value(),
            "supplier": self.supplier_input.text()
        }


class ExportDialog(QDialog):
    """Dialog for exporting data."""
    def __init__(self, title="Exporter les données", parent=None):
        # For window dragging
        self.dragging = False
        self.drag_position = None
        
        super().__init__(parent)
        
        # Remove window frame and title bar
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.9)  # 10% transparency
        self.setMinimumWidth(400)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Custom title bar
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(0, 0, 0, 10)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: bold;")
        
        # Close button
        close_btn = QPushButton("×")
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
        
        layout.addLayout(title_bar_layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # File path
        self.path_input = QLineEdit()
        self.path_input.setText("C:/Users/Documents/export.csv")
        form_layout.addRow("Chemin du fichier:", self.path_input)
        
        # File format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV (.csv)", "Excel (.xlsx)", "PDF (.pdf)", "JSON (.json)"])
        form_layout.addRow("Format:", self.format_combo)
        
        layout.addLayout(form_layout)
        
        # Browse button
        browse_btn = QPushButton("Parcourir...")
        browse_btn.setStyleSheet("""
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
        browse_btn.clicked.connect(self.browse_path)
        layout.addWidget(browse_btn)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.export_btn = QPushButton("Exporter")
        self.export_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.export_btn)
        
        layout.addLayout(buttons_layout)
        
        # Apply styles
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
            }
            QLabel {
                color: #94A3B8;
            }
            QLineEdit, QComboBox {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 12px;
                padding: 8px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3B82F6;
            }
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
            QPushButton#cancelBtn {
                background-color: #475569;
            }
            QPushButton#cancelBtn:hover {
                background-color: #64748B;
            }
        """)
    
    def browse_path(self):
        """Open a file dialog to select the export path."""
        file_format = self.format_combo.currentText()
        extension = file_format.split("(")[1].split(")")[0]
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le fichier",
            self.path_input.text(),
            f"Fichiers {file_format};;Tous les fichiers (*)"
        )
        
        if file_path:
            self.path_input.setText(file_path)
    
    def get_export_data(self):
        """Get the export data from the form."""
        return {
            "path": self.path_input.text(),
            "format": self.format_combo.currentText()
        }
    
    def mousePressEvent(self, event):
        """Handle mouse press event for window dragging."""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move event for window dragging."""
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event for window dragging."""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()


class StockView(QWidget):
    """Stock view for the application."""
    def __init__(self, db):
        super().__init__()
        
        self.db = db
        self.products_data = []
        self.materials_data = []
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for the entire view
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create a widget to hold all content
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        
        # Content layout
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_title = QLabel("Gestion des Stocks")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.setIcon(QIcon("src/resources/icons/refresh.png"))
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_data)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(refresh_btn)
        
        content_layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Finished products tab
        self.products_tab = QWidget()
        self.setup_products_tab()
        self.tab_widget.addTab(self.products_tab, "Produits Finis")
        
        # Raw materials tab
        self.materials_tab = QWidget()
        self.setup_materials_tab()
        self.tab_widget.addTab(self.materials_tab, "Matières Premières")
        
        content_layout.addWidget(self.tab_widget)
        
        # Set the scroll area content
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        
        # Connect signals after UI setup
        self.search_input.textChanged.connect(self.filter_tables)
    
    def setup_products_tab(self):
        """Set up the finished products tab."""
        # Tab layout
        tab_layout = QVBoxLayout(self.products_tab)
        tab_layout.setContentsMargins(20, 20, 20, 20)
        tab_layout.setSpacing(20)
        
        # Header with actions
        header_layout = QHBoxLayout()
        
        # Note: Products can only be added from product_view as per requirements
        
        self.products_export_btn = QPushButton("Exporter")
        self.products_export_btn.setIcon(QIcon("src/resources/icons/export.png"))
        self.products_export_btn.setCursor(Qt.PointingHandCursor)
        self.products_export_btn.clicked.connect(self.export_products)
        
        header_layout.addStretch()
        header_layout.addWidget(self.products_export_btn)
        
        tab_layout.addLayout(header_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(8)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Nom", "SKU", "Catégorie", "Prix", "Quantité", "Seuil", "Actions"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setAlternatingRowColors(True)
        
        tab_layout.addWidget(self.products_table)
    
    def setup_materials_tab(self):
        """Set up the raw materials tab."""
        # Tab layout
        tab_layout = QVBoxLayout(self.materials_tab)
        tab_layout.setContentsMargins(20, 20, 20, 20)
        tab_layout.setSpacing(20)
        
        # Header with actions
        header_layout = QHBoxLayout()
        
        add_material_btn = QPushButton("Ajouter une Matière Première")
        add_material_btn.setIcon(QIcon("src/resources/icons/add.png"))
        add_material_btn.setCursor(Qt.PointingHandCursor)
        add_material_btn.clicked.connect(self.add_material)
        
        self.materials_export_btn = QPushButton("Exporter")
        self.materials_export_btn.setIcon(QIcon("src/resources/icons/export.png"))
        self.materials_export_btn.setCursor(Qt.PointingHandCursor)
        self.materials_export_btn.clicked.connect(self.export_materials)
        
        header_layout.addWidget(add_material_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.materials_export_btn)
        
        tab_layout.addLayout(header_layout)
        
        # Materials table
        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(9)
        self.materials_table.setHorizontalHeaderLabels([
            "ID", "Nom", "Référence", "Type", "Unité", "Coût", "Quantité", "Seuil", "Actions"
        ])
        self.materials_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.materials_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.materials_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.materials_table.verticalHeader().setVisible(False)
        self.materials_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.materials_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.materials_table.setAlternatingRowColors(True)
        
        tab_layout.addWidget(self.materials_table)
    
    def load_data(self):
        """Load data from the database."""
        try:
            # Load products
            products = self.db.query(Product).order_by(Product.name).all()
            self.products_data = products
            self.update_products_table()
            
            # Load raw materials
            materials = self.db.query(RawMaterial).order_by(RawMaterial.name).all()
            self.materials_data = materials
            self.update_materials_table()
            
        except Exception as e:
            logging.error(f"Error loading stock data: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les données: {e}")
    
    def update_products_table(self):
        """Update the products table with current data."""
        self.products_table.setRowCount(0)
        
        for product in self.products_data:
            row = self.products_table.rowCount()
            self.products_table.insertRow(row)
            
            # Add data cells
            # ID
            item = QTableWidgetItem(str(product.id))
            self.products_table.setItem(row, 0, item)
            
            # Name
            item = QTableWidgetItem(product.name)
            self.products_table.setItem(row, 1, item)
            
            # SKU (using a placeholder since it's not in the model)
            item = QTableWidgetItem("SKU-" + str(product.id))
            self.products_table.setItem(row, 2, item)
            
            # Category (using a placeholder since it's not in the model)
            item = QTableWidgetItem("Produit")
            self.products_table.setItem(row, 3, item)
            
            # Price (using production_cost from the model)
            item = QTableWidgetItem(str(product.production_cost))
            self.products_table.setItem(row, 4, item)
            
            # Quantity (using initial_quantity from the model)
            item = QTableWidgetItem(str(product.initial_quantity))
            self.products_table.setItem(row, 5, item)
            
            # Reorder level (using a placeholder since it's not in the model)
            item = QTableWidgetItem("5")
            self.products_table.setItem(row, 6, item)
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("src/resources/icons/edit.png"))
            edit_btn.setToolTip("Modifier")
            edit_btn.setFixedSize(30, 30)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.clicked.connect(lambda checked=False, pid=product.id: self.edit_product(pid))
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("src/resources/icons/delete.png"))
            delete_btn.setToolTip("Supprimer")
            delete_btn.setFixedSize(30, 30)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.clicked.connect(lambda checked=False, pid=product.id: self.delete_product(pid))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.products_table.setCellWidget(row, 7, actions_widget)
    
    def update_materials_table(self):
        """Update the materials table with current data."""
        self.materials_table.setRowCount(0)
        
        for material in self.materials_data:
            row = self.materials_table.rowCount()
            self.materials_table.insertRow(row)
            
            # Add data cells
            # ID
            item = QTableWidgetItem(str(material.id))
            self.materials_table.setItem(row, 0, item)
            
            # Name
            item = QTableWidgetItem(material.name)
            self.materials_table.setItem(row, 1, item)
            
            # Reference code
            item = QTableWidgetItem(material.reference_code)
            self.materials_table.setItem(row, 2, item)
            
            # Type
            item = QTableWidgetItem(material.type)
            self.materials_table.setItem(row, 3, item)
            
            # Unit
            item = QTableWidgetItem(material.unit)
            self.materials_table.setItem(row, 4, item)
            
            # Cost
            item = QTableWidgetItem(str(material.cost))
            self.materials_table.setItem(row, 5, item)
            
            # Quantity
            item = QTableWidgetItem(str(material.quantity))
            self.materials_table.setItem(row, 6, item)
            
            # Reorder level
            item = QTableWidgetItem(str(material.reorder_level))
            self.materials_table.setItem(row, 7, item)
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("src/resources/icons/edit.png"))
            edit_btn.setToolTip("Modifier")
            edit_btn.setFixedSize(30, 30)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.clicked.connect(lambda checked=False, mid=material.id: self.edit_material(mid))
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("src/resources/icons/delete.png"))
            delete_btn.setToolTip("Supprimer")
            delete_btn.setFixedSize(30, 30)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.clicked.connect(lambda checked=False, mid=material.id: self.delete_material(mid))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.materials_table.setCellWidget(row, 8, actions_widget)
    
    def filter_tables(self):
        """Filter tables based on search input."""
        search_text = self.search_input.text().lower()
        
        # Filter products table
        for row in range(self.products_table.rowCount()):
            match = False
            for col in range(1, 7):  # Skip ID column and actions column
                item = self.products_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            
            self.products_table.setRowHidden(row, not match)
        
        # Filter materials table
        for row in range(self.materials_table.rowCount()):
            match = False
            for col in range(1, 8):  # Skip ID column and actions column
                item = self.materials_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            
            self.materials_table.setRowHidden(row, not match)
    
    def add_product(self):
        """Add a new product."""
        dialog = AddProductDialog(self.db, self)
        if dialog.exec():
            try:
                product_data = dialog.get_product_data()
                
                # Create a new Product object
                new_product = Product(
                    name=product_data["name"],
                    description=product_data["description"],
                    production_cost=product_data["price"],
                    initial_quantity=product_data["quantity"],
                    production_time=product_data["production_time"]
                )
                
                # Add to database
                self.db.add(new_product)
                self.db.commit()
                
                # Refresh the data
                self.load_data()
                
                QMessageBox.information(self, "Succès", "Produit ajouté avec succès.")
                
            except Exception as e:
                self.db.rollback()
                logging.error(f"Error adding product: {e}")
                QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter le produit: {e}")
    
    def edit_product(self, product_id):
        """Edit an existing product."""
        try:
            # Get the product from the database
            product = self.db.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                QMessageBox.warning(self, "Avertissement", "Produit non trouvé.")
                return
            
            # Create and populate the dialog
            dialog = AddProductDialog(self.db, self)
            dialog.setWindowTitle("Modifier un Produit")
            dialog.name_input.setText(product.name)
            dialog.sku_input.setText("SKU-" + str(product.id))  # Using placeholder
            dialog.category_input.setCurrentText("Produit")  # Using placeholder
            dialog.price_input.setValue(float(product.production_cost))
            dialog.quantity_input.setValue(int(product.initial_quantity))
            dialog.reorder_level_input.setValue(5)  # Using placeholder
            dialog.description_input.setText(product.description or "")
            
            if dialog.exec():
                updated_data = dialog.get_product_data()
                
                # Update product in database
                product.name = updated_data["name"]
                product.description = updated_data["description"]
                product.production_cost = updated_data["price"]
                product.initial_quantity = updated_data["quantity"]
                # Keep the existing production_time value
                
                self.db.commit()
                self.load_data()  # Refresh the data
                
                QMessageBox.information(self, "Succès", "Produit mis à jour avec succès.")
                
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error editing product: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de modifier le produit: {e}")
    
    def delete_product(self, product_id):
        """Delete a product."""
        confirm = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer ce produit ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Get the product from the database
                product = self.db.query(Product).filter(Product.id == product_id).first()
                
                if not product:
                    QMessageBox.warning(self, "Avertissement", "Produit non trouvé.")
                    return
                
                # Delete the product
                self.db.delete(product)
                self.db.commit()
                
                # Refresh the data
                self.load_data()
                
                QMessageBox.information(self, "Succès", "Produit supprimé avec succès.")
                
            except Exception as e:
                self.db.rollback()
                logging.error(f"Error deleting product: {e}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer le produit: {e}")
    
    def add_material(self):
        """Add a new raw material."""
        dialog = AddRawMaterialDialog(self)
        if dialog.exec():
            try:
                material_data = dialog.get_material_data()
                
                # Create a new RawMaterial object
                new_material = RawMaterial(
                    name=material_data["name"],
                    reference_code=material_data["ref_code"],
                    type=material_data["type"],
                    unit=material_data["unit"],
                    cost=material_data["cost"],
                    quantity=material_data["quantity"],
                    reorder_level=material_data["reorder_level"],
                    supplier=material_data["supplier"]
                )
                
                # Add to database
                self.db.add(new_material)
                self.db.commit()
                
                # Refresh the data
                self.load_data()
                
                QMessageBox.information(self, "Succès", "Matière première ajoutée avec succès.")
                
            except Exception as e:
                self.db.rollback()
                logging.error(f"Error adding material: {e}")
                QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter la matière première: {e}")
    
    def edit_material(self, material_id):
        """Edit an existing raw material."""
        try:
            # Get the material from the database
            material = self.db.query(RawMaterial).filter(RawMaterial.id == material_id).first()
            
            if not material:
                QMessageBox.warning(self, "Avertissement", "Matière première non trouvée.")
                return
            
            # Create and populate the dialog
            dialog = AddRawMaterialDialog(self)
            dialog.setWindowTitle("Modifier une Matière Première")
            dialog.name_input.setText(material.name)
            dialog.ref_code_input.setText(material.reference_code)
            dialog.type_input.setCurrentText(material.type)
            dialog.unit_input.setCurrentText(material.unit)
            dialog.cost_input.setValue(float(material.cost))
            dialog.quantity_input.setValue(float(material.quantity))
            dialog.reorder_level_input.setValue(float(material.reorder_level))
            dialog.supplier_input.setText(material.supplier)
            
            if dialog.exec():
                updated_data = dialog.get_material_data()
                
                # Update material in database
                material.name = updated_data["name"]
                material.reference_code = updated_data["ref_code"]
                material.type = updated_data["type"]
                material.unit = updated_data["unit"]
                material.cost = updated_data["cost"]
                material.quantity = updated_data["quantity"]
                material.reorder_level = updated_data["reorder_level"]
                material.supplier = updated_data["supplier"]
                
                self.db.commit()
                self.load_data()  # Refresh the data
                
                QMessageBox.information(self, "Succès", "Matière première mise à jour avec succès.")
                
        except Exception as e:
            self.db.rollback()
            logging.error(f"Error editing material: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de modifier la matière première: {e}")
    
    def delete_material(self, material_id):
        """Delete a raw material."""
        confirm = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer cette matière première ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Get the material from the database
                material = self.db.query(RawMaterial).filter(RawMaterial.id == material_id).first()
                
                if not material:
                    QMessageBox.warning(self, "Avertissement", "Matière première non trouvée.")
                    return
                
                # Delete the material
                self.db.delete(material)
                self.db.commit()
                
                # Refresh the data
                self.load_data()
                
                QMessageBox.information(self, "Succès", "Matière première supprimée avec succès.")
                
            except Exception as e:
                self.db.rollback()
                logging.error(f"Error deleting material: {e}")
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer la matière première: {e}")
    
    def export_products(self):
        """Export products data."""
        dialog = ExportDialog("Exporter les Produits", self)
        if dialog.exec():
            try:
                export_data = dialog.get_export_data()
                file_path = export_data["path"]
                file_format = export_data["format"]
                
                # Get the data to export using SQLAlchemy
                products_query = self.db.query(Product).order_by(Product.name).all()
                
                # Convert to a list of lists for export
                products = []
                for product in products_query:
                    products.append([
                        product.id,
                        product.name,
                        f"SKU-{product.id}",  # Placeholder
                        "Produit",  # Placeholder
                        product.production_cost,
                        product.initial_quantity,
                        5,  # Placeholder for reorder level
                        product.description or ""
                    ])
                
                # Headers for the export
                headers = ["ID", "Nom", "SKU", "Catégorie", "Prix", "Quantité", "Seuil", "Description"]
                
                # Export based on the selected format
                if "CSV" in file_format:
                    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(headers)
                        writer.writerows(products)
                
                elif "Excel" in file_format:
                    try:
                        import pandas as pd
                        df = pd.DataFrame(products, columns=headers)
                        df.to_excel(file_path, index=False)
                    except ImportError:
                        QMessageBox.warning(self, "Avertissement", "Module pandas non trouvé. Exportation en CSV à la place.")
                        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow(headers)
                            writer.writerows(products)
                
                elif "PDF" in file_format:
                    try:
                        from reportlab.lib import colors
                        from reportlab.lib.pagesizes import letter
                        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
                        
                        doc = SimpleDocTemplate(file_path, pagesize=letter)
                        elements = []
                        
                        data = [headers] + [list(product) for product in products]
                        t = Table(data)
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        
                        elements.append(t)
                        doc.build(elements)
                    except ImportError:
                        QMessageBox.warning(self, "Avertissement", "Module reportlab non trouvé. Exportation en CSV à la place.")
                        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow(headers)
                            writer.writerows(products)
                
                elif "JSON" in file_format:
                    products_list = []
                    for product in products:
                        products_list.append({
                            headers[i]: product[i] for i in range(len(headers))
                        })
                    
                    with open(file_path, 'w', encoding='utf-8') as jsonfile:
                        json.dump(products_list, jsonfile, indent=4, ensure_ascii=False)
                
                QMessageBox.information(self, "Succès", f"Données exportées avec succès vers {file_path}")
                
            except Exception as e:
                logging.error(f"Error exporting products: {e}")
                QMessageBox.critical(self, "Erreur", f"Impossible d'exporter les données: {e}")
    
    def export_materials(self):
        """Export materials data."""
        dialog = ExportDialog("Exporter les Matières Premières", self)
        if dialog.exec():
            try:
                export_data = dialog.get_export_data()
                file_path = export_data["path"]
                file_format = export_data["format"]
                
                # Get the data to export using SQLAlchemy
                materials_query = self.db.query(RawMaterial).order_by(RawMaterial.name).all()
                
                # Convert to a list of lists for export
                materials = []
                for material in materials_query:
                    materials.append([
                        material.id,
                        material.name,
                        material.reference_code,
                        material.type,
                        material.unit,
                        material.cost,
                        material.quantity,
                        material.reorder_level,
                        material.supplier
                    ])
                
                # Headers for the export
                headers = ["ID", "Nom", "Référence", "Type", "Unité", "Coût", "Quantité", "Seuil", "Fournisseur"]
                
                # Export based on the selected format
                if "CSV" in file_format:
                    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(headers)
                        writer.writerows(materials)
                
                elif "Excel" in file_format:
                    try:
                        import pandas as pd
                        df = pd.DataFrame(materials, columns=headers)
                        df.to_excel(file_path, index=False)
                    except ImportError:
                        QMessageBox.warning(self, "Avertissement", "Module pandas non trouvé. Exportation en CSV à la place.")
                        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow(headers)
                            writer.writerows(materials)
                
                elif "PDF" in file_format:
                    try:
                        from reportlab.lib import colors
                        from reportlab.lib.pagesizes import letter
                        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
                        
                        doc = SimpleDocTemplate(file_path, pagesize=letter)
                        elements = []
                        
                        data = [headers] + [list(material) for material in materials]
                        t = Table(data)
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        
                        elements.append(t)
                        doc.build(elements)
                    except ImportError:
                        QMessageBox.warning(self, "Avertissement", "Module reportlab non trouvé. Exportation en CSV à la place.")
                        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow(headers)
                            writer.writerows(materials)
                
                elif "JSON" in file_format:
                    materials_list = []
                    for material in materials:
                        materials_list.append({
                            headers[i]: material[i] for i in range(len(headers))
                        })
                    
                    with open(file_path, 'w', encoding='utf-8') as jsonfile:
                        json.dump(materials_list, jsonfile, indent=4, ensure_ascii=False)
                
                QMessageBox.information(self, "Succès", f"Données exportées avec succès vers {file_path}")
                
            except Exception as e:
                logging.error(f"Error exporting materials: {e}")
                QMessageBox.critical(self, "Erreur", f"Impossible d'exporter les données: {e}")
