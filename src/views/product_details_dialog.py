"""
Product details dialog for the application.
"""
import os
import sys
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QLineEdit, QFormLayout,
    QComboBox, QMessageBox, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from models.raw_material import RawMaterial


class ProductComponentRow:
    """Class to hold a component row data."""
    def __init__(self, material=None, quantity=0, fabrication_time=0):
        self.material = material
        self.quantity = quantity
        self.fabrication_time = fabrication_time
        
    @property
    def cost(self):
        """Calculate the cost of this component."""
        if not self.material:
            return 0
        return self.material.cost * self.quantity


class ProductDetailsDialog(QDialog):
    """
    Dialog for adding product details (components, materials, suppliers, etc.).
    """
    def __init__(self, db, parent=None):
        # For window dragging
        self.dragging = False
        self.drag_position = None
        
        super().__init__(parent)
        
        self.db = db
        self.components = []  # List of ProductComponentRow objects
        
        # Remove window frame and title bar
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.9)  # 10% transparency
        
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
        self.load_materials()
    
    def mousePressEvent(self, event):
        """
        Handle mouse press event for window dragging.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move event for window dragging.
        """
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release event for window dragging.
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
        
        # Custom title bar
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(0, 0, 0, 10)
        
        # Title
        title_label = QLabel("Détails du Produit")
        title_label.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: bold;")
        
        # Close button
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
        close_btn.clicked.connect(self.reject)
        
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(close_btn)
        
        main_layout.addLayout(title_bar_layout)
        
        # Components section
        components_frame = QFrame()
        components_frame.setObjectName("componentsFrame")
        components_frame.setStyleSheet("""
            #componentsFrame {
                background-color: rgba(30, 41, 59, 0.9);
                border-radius: 12px;
            }
        """)
        
        components_layout = QVBoxLayout(components_frame)
        components_layout.setContentsMargins(15, 15, 15, 15)
        components_layout.setSpacing(15)
        
        # Components header
        components_header = QLabel("Composants du Produit")
        components_header.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        components_layout.addWidget(components_header)
        
        # Components table
        self.components_table = QTableWidget()
        self.components_table.setColumnCount(5)
        self.components_table.setHorizontalHeaderLabels([
            "Matière Première", "Fournisseur", "Quantité", "Temps de Fabrication (h)", "Actions"
        ])
        self.components_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.components_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.components_table.verticalHeader().setVisible(False)
        self.components_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.components_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.components_table.setAlternatingRowColors(True)
        self.components_table.setStyleSheet("""
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
        
        components_layout.addWidget(self.components_table)
        
        # Add component button
        add_component_btn = QPushButton("Ajouter un Composant")
        add_component_btn.setIcon(QIcon("src/resources/icons/add.png"))
        add_component_btn.setCursor(Qt.PointingHandCursor)
        add_component_btn.setStyleSheet("""
            QPushButton {
                background-color: #0F172A;
                color: #F8FAFC;
                border: 1px solid #1E293B;
                border-radius: 4px;
                padding: 8px 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1E293B;
            }
        """)
        # Ajuster la taille de l'icône
        add_component_btn.setIconSize(QSize(16, 16))
        add_component_btn.clicked.connect(self.add_component)
        
        components_layout.addWidget(add_component_btn)
        
        main_layout.addWidget(components_frame)
        
        # Production cost section
        cost_frame = QFrame()
        cost_frame.setObjectName("costFrame")
        cost_frame.setStyleSheet("""
            #costFrame {
                background-color: rgba(30, 41, 59, 0.9);
                border-radius: 12px;
            }
        """)
        
        cost_layout = QHBoxLayout(cost_frame)
        cost_layout.setContentsMargins(15, 15, 15, 15)
        cost_layout.setSpacing(15)
        
        cost_label = QLabel("Coût de Production Total:")
        cost_label.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        self.total_cost_label = QLabel("0.00 €")
        self.total_cost_label.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        cost_layout.addWidget(cost_label)
        cost_layout.addWidget(self.total_cost_label)
        cost_layout.addStretch()
        
        main_layout.addWidget(cost_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setStyleSheet("""
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
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.save_btn.clicked.connect(self.accept)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def load_materials(self):
        """
        Load raw materials from the database.
        """
        try:
            self.materials = self.db.query(RawMaterial).order_by(RawMaterial.name).all()
        except Exception as e:
            logging.error(f"Error loading materials: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les matières premières: {e}")
            self.materials = []
    
    def add_component(self):
        """
        Add a new component row to the table.
        """
        if not self.materials:
            QMessageBox.warning(self, "Avertissement", "Aucune matière première disponible.")
            return
        
        # Create a dialog for adding a component
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un Composant")
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setWindowOpacity(0.9)
        dialog.setMinimumWidth(400)
        
        # Main layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Custom title bar
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(0, 0, 0, 10)
        
        # Title
        title_label = QLabel("Ajouter un Composant")
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
        close_btn.clicked.connect(dialog.reject)
        
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(close_btn)
        
        layout.addLayout(title_bar_layout)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Material selection
        material_combo = QComboBox()
        for material in self.materials:
            material_combo.addItem(material.name, material.id)
        form_layout.addRow("Matière Première:", material_combo)
        
        # Quantity
        quantity_spin = QDoubleSpinBox()
        quantity_spin.setRange(0.01, 1000)
        quantity_spin.setDecimals(2)
        quantity_spin.setValue(1)
        quantity_spin.setSuffix(f" {self.materials[0].unit}" if self.materials else "")
        
        # Update unit when material changes
        def update_unit(index):
            material_id = material_combo.itemData(index)
            material = next((m for m in self.materials if m.id == material_id), None)
            if material:
                quantity_spin.setSuffix(f" {material.unit}")
        
        material_combo.currentIndexChanged.connect(update_unit)
        form_layout.addRow("Quantité:", quantity_spin)
        
        # Fabrication time
        time_spin = QDoubleSpinBox()
        time_spin.setRange(0, 100)
        time_spin.setDecimals(2)
        time_spin.setValue(0)
        time_spin.setSuffix(" h")
        form_layout.addRow("Temps de Fabrication:", time_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(dialog.reject)
        
        add_btn = QPushButton("Ajouter")
        add_btn.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(add_btn)
        
        layout.addLayout(buttons_layout)
        
        # Apply styles
        dialog.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
            }
            QLabel {
                color: #94A3B8;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid #475569;
                border-radius: 12px;
                padding: 8px;
            }
            QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
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
        
        # Show the dialog
        if dialog.exec():
            # Get the selected material
            material_id = material_combo.currentData()
            material = next((m for m in self.materials if m.id == material_id), None)
            
            if material:
                # Create a new component
                component = ProductComponentRow(
                    material=material,
                    quantity=quantity_spin.value(),
                    fabrication_time=time_spin.value()
                )
                
                # Add to the list
                self.components.append(component)
                
                # Update the table
                self.update_components_table()
                
                # Update the total cost
                self.update_total_cost()
    
    def update_components_table(self):
        """
        Update the components table with current data.
        """
        self.components_table.setRowCount(0)
        
        for i, component in enumerate(self.components):
            row = self.components_table.rowCount()
            self.components_table.insertRow(row)
            
            # Material name
            item = QTableWidgetItem(component.material.name)
            self.components_table.setItem(row, 0, item)
            
            # Supplier
            item = QTableWidgetItem(component.material.supplier)
            self.components_table.setItem(row, 1, item)
            
            # Quantity
            item = QTableWidgetItem(f"{component.quantity} {component.material.unit}")
            self.components_table.setItem(row, 2, item)
            
            # Fabrication time
            item = QTableWidgetItem(f"{component.fabrication_time} h")
            self.components_table.setItem(row, 3, item)
            
            # Actions - Create a delete button directly
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("src/resources/icons/delete.png"))
            delete_btn.setToolTip("Supprimer")
            delete_btn.setFixedSize(30, 30)
            delete_btn.setCursor(Qt.PointingHandCursor)
            # Store the index in the button's property
            delete_btn.setProperty("component_index", i)
            delete_btn.clicked.connect(self.on_delete_clicked)
            
            # Set the button directly as the cell widget
            self.components_table.setCellWidget(row, 4, delete_btn)
    
    def on_delete_clicked(self):
        """
        Handle click on delete button.
        """
        # Get the sender button
        button = self.sender()
        if button:
            # Get the component index from the button's property
            index = button.property("component_index")
            if index is not None and 0 <= index < len(self.components):
                del self.components[index]
                self.update_components_table()
                self.update_total_cost()
    
    def update_total_cost(self):
        """
        Update the total production cost.
        """
        total_cost = sum(component.cost for component in self.components)
        self.total_cost_label.setText(f"{total_cost:.2f} €")
    
    def get_production_data(self):
        """
        Get the production data.
        
        Returns:
            Dictionary with production data.
        """
        total_cost = sum(component.cost for component in self.components)
        total_time = sum(component.fabrication_time for component in self.components)
        
        return {
            "components": self.components,
            "production_cost": total_cost,
            "production_time": total_time
        }
