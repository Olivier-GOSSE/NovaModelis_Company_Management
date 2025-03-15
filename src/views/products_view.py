"""
Products view for the application.
"""
import os
import sys
import logging
import datetime
import csv
import io
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QDialog, QLineEdit, QFormLayout,
    QComboBox, QMessageBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsSceneWheelEvent, QGraphicsSceneMouseEvent, QMenu, QAction,
    QTabWidget, QToolBar, QToolButton, QSlider, QCheckBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QRectF, QPointF, QTimer, QBuffer, QIODevice, QByteArray
from PySide6.QtGui import (
    QIcon, QFont, QColor, QPainter, QPixmap, QImage, QPen, QBrush, 
    QTransform, QCursor, QPainterPath, QLinearGradient, QRadialGradient
)
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal
from models.product import Product, Country, Sale
import config


class ProductThumbnail(QWidget):
    """
    Widget for displaying a product thumbnail with hover effect.
    """
    clicked = Signal(Product)
    
    def __init__(self, product, parent=None):
        super().__init__(parent)
        
        self.product = product
        self.is_hovered = False
        self.zoom_factor = 1.5
        
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
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
        
        self.original_pixmap = pixmap
        self.image_label.setPixmap(pixmap)
        
        image_layout.addWidget(self.image_label)
        
        # Product name
        self.name_label = QLabel(self.product.name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: #F8FAFC; font-weight: bold;")
        self.name_label.setWordWrap(True)
        
        main_layout.addWidget(self.image_frame)
        main_layout.addWidget(self.name_label)
        
        # Set up hover effect
        self.setMouseTracking(True)
        self.image_frame.setMouseTracking(True)
        self.image_label.setMouseTracking(True)
    
    def enterEvent(self, event):
        """
        Handle mouse enter event.
        """
        self.is_hovered = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """
        Handle mouse leave event.
        """
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press event.
        """
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.product)
        super().mousePressEvent(event)
    
    def paintEvent(self, event):
        """
        Paint the widget.
        """
        super().paintEvent(event)
        
        if self.is_hovered:
            # Create a larger version of the image for hover effect
            enlarged_pixmap = self.original_pixmap.scaled(
                int(self.image_label.width() * self.zoom_factor),
                int(self.image_label.height() * self.zoom_factor),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # Calculate position to center the enlarged image
            x_offset = (enlarged_pixmap.width() - self.image_label.width()) // 2
            y_offset = (enlarged_pixmap.height() - self.image_label.height()) // 2
            
            # Create a painter for the image label
            painter = QPainter(self.image_label.pixmap())
            painter.drawPixmap(-x_offset, -y_offset, enlarged_pixmap)
            painter.end()
            
            # Update the image label
            self.image_label.update()


class WorldMapWidget(QWidget):
    """
    Widget for displaying an interactive world map with sales data.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.countries_data = {}  # {country_code: sales_count}
        self.max_sales = 0
        self.min_sales = 0
        
        self.zoom_level = 1.0
        self.pan_offset = QPointF(0, 0)
        self.last_pan_pos = None
        self.is_panning = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Map view
        self.map_view = QGraphicsView()
        self.map_view.setRenderHint(QPainter.Antialiasing)
        self.map_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.map_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.map_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.map_view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.map_view.setStyleSheet("""
            QGraphicsView {
                background-color: #0F172A;
                border: none;
            }
        """)
        
        # Map scene
        self.map_scene = QGraphicsScene()
        self.map_view.setScene(self.map_scene)
        
        # Load world map
        self.world_map = QPixmap("src/resources/images/world_map.png")
        if self.world_map.isNull():
            # Create a placeholder map
            self.world_map = QPixmap(800, 400)
            self.world_map.fill(QColor("#1E293B"))
            
            painter = QPainter(self.world_map)
            painter.setPen(QPen(QColor("#334155"), 2))
            painter.drawText(QRectF(0, 0, 800, 400), Qt.AlignCenter, "World Map Placeholder")
            painter.end()
        
        self.map_item = self.map_scene.addPixmap(self.world_map)
        self.map_scene.setSceneRect(self.map_item.boundingRect())
        
        # Add controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 10, 10, 10)
        controls_layout.setSpacing(10)
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(5)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedSize(30, 30)
        zoom_out_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #F8FAFC;
                border-radius: 15px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(100)
        self.zoom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #334155;
                margin: 0px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #3B82F6;
                border: none;
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::add-page:horizontal {
                background: #334155;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #3B82F6;
                border-radius: 2px;
            }
        """)
        self.zoom_slider.valueChanged.connect(self.zoom_slider_changed)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(30, 30)
        zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #F8FAFC;
                border-radius: 15px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        zoom_in_btn.clicked.connect(self.zoom_in)
        
        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.addWidget(zoom_in_btn)
        
        # Reset view button
        reset_btn = QPushButton("Reset View")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #F8FAFC;
                border-radius: 4px;
                border: none;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        reset_btn.clicked.connect(self.reset_view)
        
        controls_layout.addLayout(zoom_layout)
        controls_layout.addStretch()
        controls_layout.addWidget(reset_btn)
        
        main_layout.addWidget(self.map_view)
        main_layout.addLayout(controls_layout)
        
        # Set up legend
        self.setup_legend()
    
    def setup_legend(self):
        """
        Set up the color legend.
        """
        legend_layout = QHBoxLayout()
        legend_layout.setContentsMargins(10, 0, 10, 10)
        legend_layout.setSpacing(5)
        
        # Min sales label
        min_label = QLabel("Min")
        min_label.setStyleSheet("color: #94A3B8;")
        
        # Color gradient
        gradient_frame = QFrame()
        gradient_frame.setFixedSize(200, 20)
        gradient_frame.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #DBEAFE, stop:1 #1E40AF);
            border-radius: 2px;
        """)
        
        # Max sales label
        max_label = QLabel("Max")
        max_label.setStyleSheet("color: #94A3B8;")
        
        legend_layout.addWidget(min_label)
        legend_layout.addWidget(gradient_frame)
        legend_layout.addWidget(max_label)
        legend_layout.addStretch()
        
        # Sales count label
        self.sales_label = QLabel()
        self.sales_label.setStyleSheet("color: #94A3B8;")
        legend_layout.addWidget(self.sales_label)
        
        self.layout().addLayout(legend_layout)
    
    def update_map(self, countries_data):
        """
        Update the map with new countries data.
        
        Args:
            countries_data: Dictionary of {country_code: sales_count}
        """
        self.countries_data = countries_data
        
        if countries_data:
            self.max_sales = max(countries_data.values())
            self.min_sales = min(countries_data.values())
        else:
            self.max_sales = 0
            self.min_sales = 0
        
        # Clear previous overlays
        for item in self.map_scene.items():
            if item != self.map_item:
                self.map_scene.removeItem(item)
        
        # Add country overlays
        for country_code, sales_count in countries_data.items():
            # Get country position and size (this would be a lookup in a real implementation)
            # For this example, we'll use placeholder positions
            country_rect = self.get_country_rect(country_code)
            
            if country_rect:
                # Calculate color based on sales count
                color_intensity = 0
                if self.max_sales > self.min_sales:
                    color_intensity = (sales_count - self.min_sales) / (self.max_sales - self.min_sales)
                
                # Create a color gradient from light blue to dark blue
                color = QColor(
                    int(219 * (1 - color_intensity) + 30 * color_intensity),  # R
                    int(234 * (1 - color_intensity) + 64 * color_intensity),  # G
                    int(254 * (1 - color_intensity) + 175 * color_intensity)  # B
                )
                
                # Create country overlay
                country_path = QPainterPath()
                country_path.addRect(country_rect)
                
                country_item = self.map_scene.addPath(
                    country_path,
                    QPen(Qt.NoPen),
                    QBrush(color)
                )
                country_item.setOpacity(0.7)
                country_item.setData(0, country_code)
                country_item.setData(1, sales_count)
                
                # Make the country item interactive
                country_item.setAcceptHoverEvents(True)
        
        self.update()
    
    def get_country_rect(self, country_code):
        """
        Get the rectangle for a country on the map.
        
        In a real implementation, this would use a lookup table or GeoJSON data.
        For this example, we'll use placeholder positions.
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code
        
        Returns:
            QRectF: Rectangle for the country on the map
        """
        # Placeholder positions for some countries
        country_positions = {
            'US': QRectF(150, 120, 100, 60),   # United States
            'CA': QRectF(150, 80, 100, 40),    # Canada
            'MX': QRectF(150, 180, 60, 40),    # Mexico
            'BR': QRectF(250, 250, 80, 60),    # Brazil
            'AR': QRectF(230, 320, 40, 60),    # Argentina
            'GB': QRectF(400, 120, 20, 15),    # United Kingdom
            'FR': QRectF(420, 130, 25, 20),    # France
            'DE': QRectF(440, 120, 25, 20),    # Germany
            'IT': QRectF(440, 140, 20, 25),    # Italy
            'ES': QRectF(410, 150, 25, 20),    # Spain
            'RU': QRectF(500, 100, 150, 60),   # Russia
            'CN': QRectF(600, 150, 80, 60),    # China
            'IN': QRectF(580, 180, 60, 50),    # India
            'JP': QRectF(680, 150, 30, 40),    # Japan
            'AU': QRectF(650, 300, 60, 50),    # Australia
        }
        
        return country_positions.get(country_code)
    
    def zoom_in(self):
        """
        Zoom in on the map.
        """
        self.zoom_level *= 1.2
        self.zoom_level = min(self.zoom_level, 5.0)
        self.update_transform()
        self.zoom_slider.setValue(int(self.zoom_level * 100))
    
    def zoom_out(self):
        """
        Zoom out on the map.
        """
        self.zoom_level /= 1.2
        self.zoom_level = max(self.zoom_level, 0.1)
        self.update_transform()
        self.zoom_slider.setValue(int(self.zoom_level * 100))
    
    def zoom_slider_changed(self, value):
        """
        Handle zoom slider value change.
        """
        self.zoom_level = value / 100.0
        self.update_transform()
    
    def update_transform(self):
        """
        Update the view transform based on zoom level and pan offset.
        """
        transform = QTransform()
        transform.scale(self.zoom_level, self.zoom_level)
        transform.translate(self.pan_offset.x(), self.pan_offset.y())
        self.map_view.setTransform(transform)
    
    def reset_view(self):
        """
        Reset the view to the original state.
        """
        self.zoom_level = 1.0
        self.pan_offset = QPointF(0, 0)
        self.update_transform()
        self.zoom_slider.setValue(100)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press event.
        """
        if event.button() == Qt.MiddleButton:
            self.is_panning = True
            self.last_pan_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move event.
        """
        if self.is_panning and self.last_pan_pos:
            delta = event.position() - self.last_pan_pos
            self.pan_offset += QPointF(delta.x() / self.zoom_level, delta.y() / self.zoom_level)
            self.last_pan_pos = event.position()
            self.update_transform()
        
        # Update sales label based on mouse position
        pos = self.map_view.mapToScene(event.position().toPoint())
        item = self.map_scene.itemAt(pos, QTransform())
        
        if item and item != self.map_item:
            country_code = item.data(0)
            sales_count = item.data(1)
            
            if country_code and sales_count is not None:
                self.sales_label.setText(f"{country_code}: {sales_count} sales")
            else:
                self.sales_label.clear()
        else:
            self.sales_label.clear()
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release event.
        """
        if event.button() == Qt.MiddleButton:
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        """
        Handle wheel event for zooming.
        """
        zoom_factor = 1.1
        
        if event.angleDelta().y() > 0:
            # Zoom in
            self.zoom_level *= zoom_factor
            self.zoom_level = min(self.zoom_level, 5.0)
        else:
            # Zoom out
            self.zoom_level /= zoom_factor
            self.zoom_level = max(self.zoom_level, 0.1)
        
        self.update_transform()
        self.zoom_slider.setValue(int(self.zoom_level * 100))
        
        event.accept()


class ProductDetailsDialog(QDialog):
    """
    Dialog for viewing product details.
    """
    def __init__(self, product, parent=None):
        super().__init__(parent)
        
        self.product = product
        
        self.setWindowTitle(f"Product Details: {product.name}")
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
        self.load_product_data()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Product header
        header_layout = QHBoxLayout()
        
        # Product image
        self.image_frame = QFrame()
        self.image_frame.setObjectName("imageFrame")
        self.image_frame.setStyleSheet("""
            #imageFrame {
                background-color: #1E293B;
                border-radius: 8px;
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
        
        image_layout.addWidget(self.image_label)
        
        # Product info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        
        self.name_label = QLabel()
        self.name_label.setStyleSheet("color: #F8FAFC; font-size: 24px; font-weight: bold;")
        
        self.description_label = QLabel()
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
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(20, 20, 20, 20)
        details_layout.setSpacing(15)
        
        details_title = QLabel("Product Details")
        details_title.setStyleSheet("color: #F8FAFC; font-size: 18px; font-weight: bold;")
        
        # Details grid
        details_grid = QGridLayout()
        details_grid.setColumnStretch(1, 1)
        details_grid.setSpacing(10)
        
        # Production time
        details_grid.addWidget(QLabel("Production Time:"), 0, 0)
        self.production_time_label = QLabel()
        self.production_time_label.setStyleSheet("color: #F8FAFC;")
        details_grid.addWidget(self.production_time_label, 0, 1)
        
        # Production cost
        details_grid.addWidget(QLabel("Production Cost:"), 1, 0)
        self.production_cost_label = QLabel()
        self.production_cost_label.setStyleSheet("color: #F8FAFC;")
        details_grid.addWidget(self.production_cost_label, 1, 1)
        
        # Initial quantity
        details_grid.addWidget(QLabel("Initial Quantity:"), 2, 0)
        self.initial_quantity_label = QLabel()
        self.initial_quantity_label.setStyleSheet("color: #F8FAFC;")
        details_grid.addWidget(self.initial_quantity_label, 2, 1)
        
        # Total sales
        details_grid.addWidget(QLabel("Total Sales:"), 3, 0)
        self.total_sales_label = QLabel()
        self.total_sales_label.setStyleSheet("color: #F8FAFC;")
        details_grid.addWidget(self.total_sales_label, 3, 1)
        
        details_layout.addWidget(details_title)
        details_layout.addLayout(details_grid)
        
        main_layout.addWidget(details_frame)
        
        # Tabs for sales data
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
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
        
        # World map tab
        self.map_tab = QWidget()
        self.setup_map_tab()
        self.tabs.addTab(self.map_tab, "World Map")
        
        # Sales by country tab
        self.sales_tab = QWidget()
        self.setup_sales_tab()
        self.tabs.addTab(self.sales_tab, "Sales by Country")
        
        main_layout.addWidget(self.tabs)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet("""
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
        self.close_btn.clicked.connect(self.reject)
        
        self.export_btn = QPushButton("Export Data")
        self.export_btn.setIcon(QIcon("src/resources/icons/export.png"))
        self.export_btn.setStyleSheet("""
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
        self.export_btn.clicked.connect(self.export_data)
        
        buttons_layout.addWidget(self.export_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def setup_map_tab(self):
        """
        Set up the world map tab.
        """
        tab_layout = QVBoxLayout(self.map_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        self.world_map = WorldMapWidget()
        tab_layout.addWidget(self.world_map)
    
    def setup_sales_tab(self):
        """
        Set up the sales by country tab.
        """
        tab_layout = QVBoxLayout(self.sales_tab)
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.setSpacing(15)
        
        # Table toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search countries...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_countries)
        
        search_layout.addWidget(self.search_input)
        
        # Sort options
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Sort by Sales (High to Low)", "sales_desc")
        self.sort_combo.addItem("Sort by Sales (Low to High)", "sales_asc")
        self.sort_combo.addItem("Sort by Country (A to Z)", "country_asc")
        self.sort_combo.addItem("Sort by Country (Z to A)", "country_desc")
        self.sort_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
                min-width: 200px;
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
        self.sort_combo.currentIndexChanged.connect(self.sort_countries)
        
        toolbar_layout.addLayout(search_layout)
        toolbar_layout.addWidget(self.sort_combo)
        toolbar_layout.addStretch()
        
        # Export button
        export_btn = QPushButton("Export CSV")
        export_btn.setIcon(QIcon("src/resources/icons/export.png"))
        export_btn.setStyleSheet("""
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
        export_btn.clicked.connect(self.export_data)
        
        toolbar_layout.addWidget(export_btn)
        
        tab_layout.addLayout(toolbar_layout)
        
        # Countries table
        self.countries_table = QTableWidget()
        self.countries_table.setColumnCount(3)
        self.countries_table.setHorizontalHeaderLabels([
            "Country", "Country Code", "Sales"
        ])
        self.countries_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.countries_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.countries_table.verticalHeader().setVisible(False)
        self.countries_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.countries_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.countries_table.setAlternatingRowColors(True)
        self.countries_table.setStyleSheet("""
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
        
        tab_layout.addWidget(self.countries_table)
    
    def load_product_data(self):
        """
        Load product data into the dialog.
        """
        # Set product image
        if self.product.image_path and os.path.exists(self.product.image_path):
            pixmap = QPixmap(self.product.image_path)
        else:
            # Use placeholder image
            pixmap = QPixmap("src/resources/icons/product_placeholder.png")
        
        self.image_label.setPixmap(pixmap)
        
        # Set product info
        self.name_label.setText(self.product.name)
        self.description_label.setText(self.product.description or "No description available.")
        
        # Set product details
        self.production_time_label.setText(f"{self.product.production_time} hours")
        self.production_cost_label.setText(f"${self.product.production_cost:.2f}")
        self.initial_quantity_label.setText(str(self.product.initial_quantity))
        self.total_sales_label.setText(str(self.product.total_sales))
        
        # Load sales data
        self.load_sales_data()
    
    def load_sales_data(self):
        """
        Load sales data into the dialog.
        """
        # Get sales by country
        sales_by_country = self.product.sales_by_country
        
        # Convert to format for world map
        countries_data = {}
        
        try:
            db = SessionLocal()
            
            # Get country codes
            for country_name, sales_count in sales_by_country.items():
                country = db.query(Country).filter(Country.name == country_name).first()
                if country:
                    countries_data[country.code] = sales_count
            
            # Update world map
            self.world_map.update_map(countries_data)
            
            # Update countries table
            self.update_countries_table(sales_by_country)
        except Exception as e:
            logging.error(f"Error loading sales data: {str(e)}")
        finally:
            db.close()
    
    def update_countries_table(self, sales_by_country):
        """
        Update the countries table with sales data.
        """
        # Clear table
        self.countries_table.setRowCount(0)
        
        try:
            db = SessionLocal()
            
            # Get countries with sales
            countries_with_sales = []
            
            for country_name, sales_count in sales_by_country.items():
                country = db.query(Country).filter(Country.name == country_name).first()
                if country:
                    countries_with_sales.append({
                        'name': country.name,
                        'code': country.code,
                        'sales': sales_count
                    })
            
            # Sort countries
            self.sort_countries_data(countries_with_sales)
            
            # Populate table
            self.countries_table.setRowCount(len(countries_with_sales))
            
            for i, country_data in enumerate(countries_with_sales):
                # Country name
                name_item = QTableWidgetItem(country_data['name'])
                self.countries_table.setItem(i, 0, name_item)
                
                # Country code
                code_item = QTableWidgetItem(country_data['code'])
                self.countries_table.setItem(i, 1, code_item)
                
                # Sales count
                sales_item = QTableWidgetItem(str(country_data['sales']))
                sales_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.countries_table.setItem(i, 2, sales_item)
        except Exception as e:
            logging.error(f"Error updating countries table: {str(e)}")
        finally:
            db.close()
    
    def sort_countries_data(self, countries_data):
        """
        Sort the countries data based on the selected sort option.
        """
        sort_option = self.sort_combo.currentData()
        
        if sort_option == "sales_desc":
            countries_data.sort(key=lambda x: x['sales'], reverse=True)
        elif sort_option == "sales_asc":
            countries_data.sort(key=lambda x: x['sales'])
        elif sort_option == "country_asc":
            countries_data.sort(key=lambda x: x['name'])
        elif sort_option == "country_desc":
            countries_data.sort(key=lambda x: x['name'], reverse=True)
    
    def sort_countries(self):
        """
        Sort the countries table based on the selected sort option.
        """
        # Reload sales data to apply new sort
        self.load_sales_data()
    
    def filter_countries(self):
        """
        Filter the countries table based on the search text.
        """
        search_text = self.search_input.text().lower()
        
        for i in range(self.countries_table.rowCount()):
            row_hidden = True
            
            # Check if search text is in country name or code
            for j in range(2):
                item = self.countries_table.item(i, j)
                if item and search_text in item.text().lower():
                    row_hidden = False
                    break
            
            self.countries_table.setRowHidden(i, row_hidden)
    
    def export_data(self):
        """
        Export the sales data to a CSV file.
        """
        # Get file path
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["Country", "Country Code", "Sales"])
                
                # Write data
                for i in range(self.countries_table.rowCount()):
                    if not self.countries_table.isRowHidden(i):
                        country = self.countries_table.item(i, 0).text()
                        code = self.countries_table.item(i, 1).text()
                        sales = self.countries_table.item(i, 2).text()
                        
                        writer.writerow([country, code, sales])
            
            QMessageBox.information(self, "Export Successful", f"Data exported to {file_path}")
        except Exception as e:
            logging.error(f"Error exporting data: {str(e)}")
            QMessageBox.warning(self, "Export Error", f"An error occurred: {str(e)}")


class ProductDialog(QDialog):
    """
    Dialog for adding or editing a product.
    """
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        
        self.product = product
        self.is_edit_mode = product is not None
        self.image_path = product.image_path if product else None
        
        self.setWindowTitle(f"{'Edit' if self.is_edit_mode else 'Add'} Product")
        self.setMinimumSize(600, 500)
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_product_data()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Product image
        image_layout = QHBoxLayout()
        
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
        
        image_inner_layout = QVBoxLayout(self.image_frame)
        image_inner_layout.setContentsMargins(5, 5, 5, 5)
        image_inner_layout.setSpacing(0)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(140, 140)
        
        # Set placeholder image
        pixmap = QPixmap("src/resources/icons/product_placeholder.png")
        self.image_label.setPixmap(pixmap)
        
        image_inner_layout.addWidget(self.image_label)
        
        # Image buttons
        image_buttons_layout = QVBoxLayout()
        image_buttons_layout.setSpacing(10)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setStyleSheet("""
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
        self.browse_btn.clicked.connect(self.browse_image)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("""
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
        self.clear_btn.clicked.connect(self.clear_image)
        
        image_buttons_layout.addWidget(self.browse_btn)
        image_buttons_layout.addWidget(self.clear_btn)
        image_buttons_layout.addStretch()
        
        image_layout.addWidget(self.image_frame)
        image_layout.addSpacing(10)
        image_layout.addLayout(image_buttons_layout)
        image_layout.addStretch()
        
        form_layout.addRow("Product Image:", image_layout)
        
        # Product name
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        form_layout.addRow("Product Name:", self.name_input)
        
        # Product description
        self.description_input = QTextEdit()
        self.description_input.setStyleSheet("""
            QTextEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_input)
        
        # Production time
        self.production_time_input = QDoubleSpinBox()
        self.production_time_input.setRange(0.1, 1000)
        self.production_time_input.setValue(1.0)
        self.production_time_input.setSuffix(" hours")
        self.production_time_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background-color: #334155;
                border: none;
                border-radius: 2px;
            }
        """)
        form_layout.addRow("Production Time:", self.production_time_input)
        
        # Production cost
        self.production_cost_input = QDoubleSpinBox()
        self.production_cost_input.setRange(0.01, 10000)
        self.production_cost_input.setValue(10.0)
        self.production_cost_input.setPrefix("$")
        self.production_cost_input.setDecimals(2)
        self.production_cost_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background-color: #334155;
                border: none;
                border-radius: 2px;
            }
        """)
        form_layout.addRow("Production Cost:", self.production_cost_input)
        
        # Initial quantity
        self.initial_quantity_input = QSpinBox()
        self.initial_quantity_input.setRange(0, 10000)
        self.initial_quantity_input.setValue(0)
        self.initial_quantity_input.setStyleSheet("""
            QSpinBox {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #334155;
                border: none;
                border-radius: 2px;
            }
        """)
        form_layout.addRow("Initial Quantity:", self.initial_quantity_input)
        
        # Countries
        self.countries_layout = QVBoxLayout()
        self.countries_layout.setSpacing(5)
        
        self.countries_label = QLabel("Select countries where this product is sold:")
        self.countries_label.setStyleSheet("color: #F8FAFC;")
        
        self.countries_scroll = QScrollArea()
        self.countries_scroll.setWidgetResizable(True)
        self.countries_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 4px;
            }
        """)
        
        self.countries_widget = QWidget()
        self.countries_layout.addWidget(self.countries_label)
        self.countries_layout.addWidget(self.countries_scroll)
        
        self.countries_grid = QGridLayout(self.countries_widget)
        self.countries_grid.setContentsMargins(10, 10, 10, 10)
        self.countries_grid.setSpacing(10)
        
        self.countries_scroll.setWidget(self.countries_widget)
        
        # Load countries
        self.load_countries()
        
        form_layout.addRow("Countries:", self.countries_layout)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
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
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet("""
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
        self.save_btn.clicked.connect(self.save_product)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def load_countries(self):
        """
        Load countries into the grid.
        """
        try:
            db = SessionLocal()
            countries = db.query(Country).order_by(Country.name).all()
            
            # Create checkboxes for countries
            self.country_checkboxes = {}
            
            for i, country in enumerate(countries):
                checkbox = QCheckBox(country.name)
                checkbox.setStyleSheet("""
                    QCheckBox {
                        color: #F8FAFC;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                        border: 1px solid #334155;
                        border-radius: 2px;
                        background-color: #1E293B;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #3B82F6;
                        border: 1px solid #3B82F6;
                    }
                """)
                
                self.country_checkboxes[country.id] = checkbox
                
                # Add to grid, 3 columns
                row = i // 3
                col = i % 3
                
                self.countries_grid.addWidget(checkbox, row, col)
        except Exception as e:
            logging.error(f"Error loading countries: {str(e)}")
        finally:
            db.close()
    
    def load_product_data(self):
        """
        Load product data into the form.
        """
        if not self.product:
            return
        
        # Set product image
        if self.product.image_path and os.path.exists(self.product.image_path):
            pixmap = QPixmap(self.product.image_path)
            self.image_label.setPixmap(pixmap)
            self.image_path = self.product.image_path
        
        # Set product info
        self.name_input.setText(self.product.name)
        self.description_input.setText(self.product.description or "")
        self.production_time_input.setValue(self.product.production_time)
        self.production_cost_input.setValue(self.product.production_cost)
        self.initial_quantity_input.setValue(self.product.initial_quantity)
        
        # Set countries
        for country in self.product.countries:
            if country.id in self.country_checkboxes:
                self.country_checkboxes[country.id].setChecked(True)
    
    def browse_image(self):
        """
        Browse for a product image.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Product Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            # Copy image to resources directory
            resources_dir = "src/resources/images/products"
            os.makedirs(resources_dir, exist_ok=True)
            
            # Generate a unique filename
            filename = os.path.basename(file_path)
            base_name, ext = os.path.splitext(filename)
            new_filename = f"{base_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
            new_path = os.path.join(resources_dir, new_filename)
            
            # Copy file
            try:
                import shutil
                shutil.copy2(file_path, new_path)
                
                # Update image
                pixmap = QPixmap(new_path)
                self.image_label.setPixmap(pixmap)
                self.image_path = new_path
            except Exception as e:
                logging.error(f"Error copying image: {str(e)}")
                QMessageBox.warning(self, "Error", f"Failed to copy image: {str(e)}")
    
    def clear_image(self):
        """
        Clear the product image.
        """
        pixmap = QPixmap("src/resources/icons/product_placeholder.png")
        self.image_label.setPixmap(pixmap)
        self.image_path = None
    
    def save_product(self):
        """
        Save the product data.
        """
        # Validate required fields
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Product name is required.")
            return
        
        try:
            db = SessionLocal()
            
            if self.is_edit_mode:
                # Update existing product
                product = db.query(Product).filter(Product.id == self.product.id).first()
                if not product:
                    QMessageBox.warning(self, "Error", "Product not found.")
                    return
            else:
                # Create new product
                product = Product()
                product.created_at = datetime.datetime.utcnow()
                db.add(product)
            
            # Update product data
            product.name = name
            product.description = self.description_input.toPlainText().strip() or None
            product.image_path = self.image_path
            product.production_time = self.production_time_input.value()
            product.production_cost = self.production_cost_input.value()
            product.initial_quantity = self.initial_quantity_input.value()
            product.updated_at = datetime.datetime.utcnow()
            
            # Update countries
            product.countries = []
            
            for country_id, checkbox in self.country_checkboxes.items():
                if checkbox.isChecked():
                    country = db.query(Country).filter(Country.id == country_id).first()
                    if country:
                        product.countries.append(country)
            
            db.commit()
            
            logging.info(f"Product {product.name} {'updated' if self.is_edit_mode else 'created'}")
            
            self.accept()
        except Exception as e:
            logging.error(f"Error saving product: {str(e)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
        finally:
            db.close()


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
        self.add_btn.clicked.connect(self.add_product)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addLayout(search_layout)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(header_layout)
        
        # Products grid
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
        
        self.products_grid = QGridLayout(self.products_widget)
        self.products_grid.setContentsMargins(10, 10, 10, 10)
        self.products_grid.setSpacing(20)
        
        self.products_scroll.setWidget(self.products_widget)
        
        main_layout.addWidget(self.products_scroll)
    
    def refresh_data(self):
        """
        Refresh the products data.
        """
        try:
            # Clear products grid
            for i in reversed(range(self.products_grid.count())):
                widget = self.products_grid.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # Get products
            products = self.db.query(Product).all()
            
                # Add products to grid
            for i, product in enumerate(products):
                thumbnail = ProductThumbnail(product)
                thumbnail.clicked.connect(self.view_product)
                
                # Add to grid, 4 columns
                row = i // 4
                col = i % 4
                
                self.products_grid.addWidget(thumbnail, row, col)
            
            logging.info("Products view refreshed")
        except Exception as e:
            logging.error(f"Error refreshing products data: {str(e)}")
    
    def filter_products(self):
        """
        Filter products based on search text.
        """
        search_text = self.search_input.text().lower()
        
        # Hide/show products based on search text
        for i in range(self.products_grid.count()):
            widget = self.products_grid.itemAt(i).widget()
            if isinstance(widget, ProductThumbnail):
                product_name = widget.product.name.lower()
                widget.setVisible(search_text in product_name)
    
    def add_product(self):
        """
        Open the add product dialog.
        """
        dialog = ProductDialog(parent=self)
        if dialog.exec():
            # Refresh the view to show the new product
            self.refresh_data()
    
    def view_product(self, product):
        """
        Open the product details dialog.
        """
        dialog = ProductDetailsDialog(product, self)
        dialog.exec()
    
    def edit_product(self, product):
        """
        Open the edit product dialog.
        """
        dialog = ProductDialog(parent=self, product=product)
        if dialog.exec():
            # Refresh the view to show the updated product
            self.refresh_data()
    
    def delete_product(self, product):
        """
        Delete a product.
        """
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            f"Are you sure you want to delete the product '{product.name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete product
                self.db.query(Product).filter(Product.id == product.id).delete()
                self.db.commit()
                
                logging.info(f"Product {product.name} deleted")
                
                # Refresh the view
                self.refresh_data()
            except Exception as e:
                logging.error(f"Error deleting product: {str(e)}")
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
