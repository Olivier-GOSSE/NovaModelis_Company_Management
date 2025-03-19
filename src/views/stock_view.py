"""
Stock view for the application.
"""
import os
import sys
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QTabWidget, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QSpinBox, QDoubleSpinBox, QMessageBox, QDialog, QFormLayout
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont, QColor, QPainter

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

# Import models (these would need to be created)
# from models import Product, RawMaterial


class AddProductDialog(QDialog):
    """
    Dialog for adding a new finished product.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Ajouter un Produit Fini")
        self.setMinimumWidth(400)
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
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #3B82F6;
            }
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
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
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
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
        
        # Price
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 10000)
        self.price_input.setDecimals(2)
        self.price_input.setSuffix(" €")
        form_layout.addRow("Prix:", self.price_input)
        
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
    
    def get_product_data(self):
        """
        Get the product data from the form.
        
        Returns:
            dict: The product data.
        """
        return {
            "name": self.name_input.text(),
            "sku": self.sku_input.text(),
            "category": self.category_input.currentText(),
            "price": self.price_input.value(),
            "quantity": self.quantity_input.value(),
            "reorder_level": self.reorder_level_input.value(),
            "description": self.description_input.text()
        }


class AddRawMaterialDialog(QDialog):
    """
    Dialog for adding a new raw material.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Ajouter une Matière Première")
        self.setMinimumWidth(400)
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
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #3B82F6;
            }
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
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
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
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
    
    def get_material_data(self):
        """
        Get the material data from the form.
        
        Returns:
            dict: The material data.
        """
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


class StockView(QWidget):
    """
    Stock view for the application.
    """
    def __init__(self, db):
        super().__init__()
        
        self.db = db
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
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
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #0F172A;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1E293B;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #475569;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #64748B;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: #1E293B;
            }
        """)
        
        # Create a widget to hold all content
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_widget.setStyleSheet("""
            #contentWidget {
                background-color: #0F172A;
            }
        """)
        
        # Content layout
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_title = QLabel("Gestion des Stocks")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Rechercher...")
        search_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 4px;
                padding: 8px;
                max-width: 250px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        search_input.textChanged.connect(self.filter_tables)
        
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.setIcon(QIcon("src/resources/icons/refresh.png"))
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.load_data)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(search_input)
        header_layout.addWidget(refresh_btn)
        
        content_layout.addLayout(header_layout)
        
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
    
    def setup_products_tab(self):
        """
        Set up the finished products tab.
        """
        # Tab layout
        tab_layout = QVBoxLayout(self.products_tab)
        tab_layout.setContentsMargins(20, 20, 20, 20)
        tab_layout.setSpacing(20)
        
        # Header with actions
        header_layout = QHBoxLayout()
        
        add_product_btn = QPushButton("Ajouter un Produit")
        add_product_btn.setIcon(QIcon("src/resources/icons/add.png"))
        add_product_btn.setCursor(Qt.PointingHandCursor)
        add_product_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        add_product_btn.clicked.connect(self.add_product)
        
        export_btn = QPushButton("Exporter")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #64748B;
            }
        """)
        
        header_layout.addWidget(add_product_btn)
        header_layout.addStretch()
        header_layout.addWidget(export_btn)
        
        tab_layout.addLayout(header_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(8)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Nom", "SKU", "Catégorie", "Prix", "Quantité", "Seuil", "Actions"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID column
        self.products_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Actions column
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E293B;
                border-radius: 8px;
                border: none;
                gridline-color: #334155;
            }
            QHeaderView::section {
                background-color: #0F172A;
                color: #94A3B8;
                border: none;
                padding: 5px;
            }
            QTableWidget::item {
                color: #F8FAFC;
                border: none;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #334155;
            }
        """)
        
        tab_layout.addWidget(self.products_table)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.products_count_label = QLabel("0 produits")
        self.products_count_label.setStyleSheet("color: #94A3B8;")
        
        self.low_stock_label = QLabel("0 produits en stock faible")
        self.low_stock_label.setStyleSheet("color: #EF4444;")
        
        status_layout.addWidget(self.products_count_label)
        status_layout.addStretch()
        status_layout.addWidget(self.low_stock_label)
        
        tab_layout.addLayout(status_layout)
    
    def setup_materials_tab(self):
        """
        Set up the raw materials tab.
        """
        # Tab layout
        tab_layout = QVBoxLayout(self.materials_tab)
        tab_layout.setContentsMargins(20, 20, 20, 20)
        tab_layout.setSpacing(20)
        
        # Header with actions
        header_layout = QHBoxLayout()
        
        add_material_btn = QPushButton("Ajouter une Matière")
        add_material_btn.setIcon(QIcon("src/resources/icons/add.png"))
        add_material_btn.setCursor(Qt.PointingHandCursor)
        add_material_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        add_material_btn.clicked.connect(self.add_material)
        
        export_btn = QPushButton("Exporter")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #64748B;
            }
        """)
        
        header_layout.addWidget(add_material_btn)
        header_layout.addStretch()
        header_layout.addWidget(export_btn)
        
        tab_layout.addLayout(header_layout)
        
        # Materials table
        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(9)
        self.materials_table.setHorizontalHeaderLabels([
            "ID", "Nom", "Référence", "Type", "Unité", "Coût", "Quantité", "Seuil", "Actions"
        ])
        self.materials_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.materials_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID column
        self.materials_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Actions column
        self.materials_table.verticalHeader().setVisible(False)
        self.materials_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.materials_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.materials_table.setAlternatingRowColors(True)
        self.materials_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E293B;
                border-radius: 8px;
                border: none;
                gridline-color: #334155;
            }
            QHeaderView::section {
                background-color: #0F172A;
                color: #94A3B8;
                border: none;
                padding: 5px;
            }
            QTableWidget::item {
                color: #F8FAFC;
                border: none;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #334155;
            }
        """)
        
        tab_layout.addWidget(self.materials_table)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.materials_count_label = QLabel("0 matières")
        self.materials_count_label.setStyleSheet("color: #94A3B8;")
        
        self.low_materials_label = QLabel("0 matières en stock faible")
        self.low_materials_label.setStyleSheet("color: #EF4444;")
        
        status_layout.addWidget(self.materials_count_label)
        status_layout.addStretch()
        status_layout.addWidget(self.low_materials_label)
        
        tab_layout.addLayout(status_layout)
    
    def load_data(self):
        """
        Load data from the database.
        """
        # In a real application, this would load data from the database
        # For this demo, we'll just add some sample data
        
        # Clear tables
        self.products_table.setRowCount(0)
        self.materials_table.setRowCount(0)
        
        # Sample products data
        products_data = [
            (1, "Figurine Dragon", "FIG-DR-001", "Figurine", 49.99, 15, 5),
            (2, "Maquette Château", "MAQ-CH-002", "Maquette", 129.99, 8, 3),
            (3, "Figurine Chevalier", "FIG-CH-003", "Figurine", 39.99, 25, 10),
            (4, "Accessoire Peinture", "ACC-PT-004", "Accessoire", 19.99, 50, 20),
            (5, "Maquette Vaisseau", "MAQ-VS-005", "Maquette", 89.99, 12, 5),
            (6, "Figurine Elfe", "FIG-EL-006", "Figurine", 34.99, 18, 8)
        ]
        
        # Add products to table
        self.products_table.setRowCount(len(products_data))
        low_stock_count = 0
        
        for row, product in enumerate(products_data):
            # Check if product is low on stock
            if product[5] <= product[6]:
                low_stock_count += 1
            
            # Add product data to table
            for col, value in enumerate(product):
                if col == 4:  # Price column
                    item = QTableWidgetItem(f"{value:.2f} €")
                else:
                    item = QTableWidgetItem(str(value))
                
                # Highlight low stock items
                if col == 5 and product[5] <= product[6]:
                    item.setForeground(QColor("#EF4444"))  # Red text for low stock
                
                self.products_table.setItem(row, col, item)
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("src/resources/icons/edit.png"))
            edit_btn.setIconSize(QSize(16, 16))
            edit_btn.setFixedSize(30, 30)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #334155;
                    border-radius: 15px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #3B82F6;
                }
            """)
            edit_btn.setToolTip("Modifier")
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("src/resources/icons/delete.png"))
            delete_btn.setIconSize(QSize(16, 16))
            delete_btn.setFixedSize(30, 30)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #334155;
                    border-radius: 15px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #EF4444;
                }
            """)
            delete_btn.setToolTip("Supprimer")
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.products_table.setCellWidget(row, 7, actions_widget)
        
        # Update products status
        self.products_count_label.setText(f"{len(products_data)} produits")
        self.low_stock_label.setText(f"{low_stock_count} produits en stock faible")
        
        # Sample materials data
        materials_data = [
            (1, "Résine Epoxy", "RES-EP-001", "Résine", "kg", 25.99, 50.0, 10.0, "FournisseurA"),
            (2, "Plastique ABS", "PLA-ABS-002", "Plastique", "kg", 15.50, 100.0, 20.0, "FournisseurB"),
            (3, "Peinture Acrylique Rouge", "PNT-ACR-003", "Peinture", "l", 12.99, 5.0, 2.0, "FournisseurC"),
            (4, "Métal Aluminium", "MET-ALU-004", "Métal", "kg", 18.75, 30.0, 5.0, "FournisseurD"),
            (5, "Peinture Acrylique Bleue", "PNT-ACR-005", "Peinture", "l", 12.99, 1.5, 2.0, "FournisseurC")
        ]
        
        # Add materials to table
        self.materials_table.setRowCount(len(materials_data))
        low_materials_count = 0
        
        for row, material in enumerate(materials_data):
            # Check if material is low on stock
            if material[6] <= material[7]:
                low_materials_count += 1
            
            # Add material data to table
            for col, value in enumerate(material):
                if col == 5:  # Cost column
                    item = QTableWidgetItem(f"{value:.2f} €")
                elif col == 6 or col == 7:  # Quantity and reorder level columns
                    item = QTableWidgetItem(f"{value:.2f} {material[4]}")
                else:
                    item = QTableWidgetItem(str(value))
                
                # Highlight low stock items
                if col == 6 and material[6] <= material[7]:
                    item.setForeground(QColor("#EF4444"))  # Red text for low stock
                
                self.materials_table.setItem(row, col, item)
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("src/resources/icons/edit.png"))
            edit_btn.setIconSize(QSize(16, 16))
            edit_btn.setFixedSize(30, 30)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #334155;
                    border-radius: 15px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #3B82F6;
                }
            """)
            edit_btn.setToolTip("Modifier")
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("src/resources/icons/delete.png"))
            delete_btn.setIconSize(QSize(16, 16))
            delete_btn.setFixedSize(30, 30)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #334155;
                    border-radius: 15px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #EF4444;
                }
            """)
            delete_btn.setToolTip("Supprimer")
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.materials_table.setCellWidget(row, 8, actions_widget)
        
        # Update materials status
        self.materials_count_label.setText(f"{len(materials_data)} matières")
        self.low_materials_label.setText(f"{low_materials_count} matières en stock faible")
    
    def filter_tables(self, text):
        """
        Filter the tables based on search text.
        
        Args:
            text: The search text.
        """
        # Filter products table
        for row in range(self.products_table.rowCount()):
            match_found = False
            for col in range(1, 4):  # Search in name, SKU, and category columns
                item = self.products_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match_found = True
                    break
            
            self.products_table.setRowHidden(row, not match_found)
        
        # Filter materials table
        for row in range(self.materials_table.rowCount()):
            match_found = False
            for col in range(1, 5):  # Search in name, reference, type, and unit columns
                item = self.materials_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match_found = True
                    break
            
            self.materials_table.setRowHidden(row, not match_found)
    
    def add_product(self):
        """
        Add a new product to the inventory.
        """
        dialog = AddProductDialog(self)
        if dialog.exec():
            product_data = dialog.get_product_data()
            
            # In a real application, this would save to the database
            # For this demo, we'll just show a message
            QMessageBox.information(
                self,
                "Produit Ajouté",
                f"Le produit '{product_data['name']}' a été ajouté avec succès."
            )
            
            # Refresh the data to show the new product
            self.load_data()
    
    def add_material(self):
        """
        Add a new raw material to the inventory.
        """
        dialog = AddRawMaterialDialog(self)
        if dialog.exec():
            material_data = dialog.get_material_data()
            
            # In a real application, this would save to the database
            # For this demo, we'll just show a message
            QMessageBox.information(
                self,
                "Matière Première Ajoutée",
                f"La matière première '{material_data['name']}' a été ajoutée avec succès."
            )
            
            # Refresh the data to show the new material
            self.load_data()
