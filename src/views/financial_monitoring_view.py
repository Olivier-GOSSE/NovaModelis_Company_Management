"""
Financial monitoring view for the application.
"""
import os
import sys
import logging
import datetime
import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QDialog, QLineEdit, QFormLayout,
    QComboBox, QMessageBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QFileDialog, QTabWidget, QToolBar, QToolButton, QSlider, QCheckBox,
    QInputDialog, QToolTip
)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QDate, QDateTime, QPoint
from PySide6.QtGui import QIcon, QFont, QColor, QPainter, QPixmap, QPen, QBrush, QCursor
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QSplineSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal
import config


class KPICard(QFrame):
    """
    Card widget for displaying a KPI.
    """
    def __init__(self, title, value, unit="", change=0.0, parent=None):
        super().__init__(parent)
        
        self.setObjectName("kpiCard")
        self.setStyleSheet("""
            #kpiCard {
                background-color: #1E293B;
                border-radius: 8px;
                border: 1px solid #334155;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(5)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("titleLabel")
        self.title_label.setStyleSheet("color: #CBD5E1; font-size: 16px; font-weight: bold;")
        
        # Value
        value_layout = QHBoxLayout()
        value_layout.setSpacing(5)
        
        self.value_label = QLabel(f"{value}")
        self.value_label.setObjectName("valueLabel")
        self.value_label.setStyleSheet("color: #F8FAFC; font-size: 24px; font-weight: bold;")
        
        self.unit_label = QLabel(unit)
        self.unit_label.setObjectName("unitLabel")
        self.unit_label.setStyleSheet("color: #94A3B8; font-size: 14px; margin-top: 5px;")
        
        value_layout.addWidget(self.value_label)
        value_layout.addWidget(self.unit_label)
        value_layout.addStretch()
        
        # Change
        change_label = QLabel(f"{'+' if change >= 0 else ''}{change:.1f}%")
        change_label.setStyleSheet(
            f"color: {'#10B981' if change >= 0 else '#EF4444'}; "
            f"font-size: 14px; font-weight: bold;"
        )
        
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(value_layout)
        main_layout.addWidget(change_label)


class FinancialMonitoringView(QWidget):
    """
    Financial monitoring view for the application.
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
        
        header_title = QLabel("Monitoring Financier")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        # Period filter
        period_layout = QHBoxLayout()
        period_layout.setSpacing(10)
        
        period_label = QLabel("Période:")
        period_label.setStyleSheet("color: #F8FAFC;")
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Aujourd'hui", "Cette semaine", "Ce mois", "Ce trimestre", "Cette année"])
        self.period_combo.setCurrentIndex(2)  # Default to monthly
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                selection-background-color: #3B82F6;
            }
        """)
        self.period_combo.currentIndexChanged.connect(self.refresh_data)
        
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_combo)
        
        # Export button
        self.export_btn = QPushButton("Exporter")
        self.export_btn.setIcon(QIcon("src/resources/icons/export.png"))
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        self.export_btn.clicked.connect(self.export_data)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addLayout(period_layout)
        header_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(header_layout)
        
        # KPI cards
        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(15)
        
        # Create KPI cards (placeholder data, will be updated in refresh_data)
        self.revenue_card = KPICard("Chiffre d'affaires", "0", "€", 0.0)
        self.profit_card = KPICard("Bénéfice net", "0", "€", 0.0)
        self.gross_margin_card = KPICard("Marge brute", "0", "%", 0.0)
        self.net_margin_card = KPICard("Marge nette", "0", "%", 0.0)
        
        self.accounts_receivable_card = KPICard("Encours clients", "0", "€", 0.0)
        self.accounts_payable_card = KPICard("Dettes fournisseurs", "0", "€", 0.0)
        self.cash_flow_card = KPICard("Flux de trésorerie", "0", "€", 0.0)
        self.roi_card = KPICard("ROI", "0", "%", 0.0)
        
        # Add KPI cards to grid (2 rows, 4 columns)
        kpi_layout.addWidget(self.revenue_card, 0, 0)
        kpi_layout.addWidget(self.profit_card, 0, 1)
        kpi_layout.addWidget(self.gross_margin_card, 0, 2)
        kpi_layout.addWidget(self.net_margin_card, 0, 3)
        
        kpi_layout.addWidget(self.accounts_receivable_card, 1, 0)
        kpi_layout.addWidget(self.accounts_payable_card, 1, 1)
        kpi_layout.addWidget(self.cash_flow_card, 1, 2)
        kpi_layout.addWidget(self.roi_card, 1, 3)
        
        main_layout.addLayout(kpi_layout)
        
        # Charts tabs
        self.charts_tabs = QTabWidget()
        self.charts_tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: #1E293B;
                border-radius: 8px;
                border: 1px solid #334155;
            }
            QTabBar::tab {
                background-color: #0F172A;
                color: #94A3B8;
                border: none;
                padding: 8px 16px;
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
        
        # Revenue and profit trends tab
        self.trends_tab = QWidget()
        self.setup_trends_tab()
        self.charts_tabs.addTab(self.trends_tab, "Tendances")
        
        # Expenses by category tab
        self.expenses_tab = QWidget()
        self.setup_expenses_tab()
        self.charts_tabs.addTab(self.expenses_tab, "Dépenses")
        
        # Revenue by sector tab
        self.sectors_tab = QWidget()
        self.setup_sectors_tab()
        self.charts_tabs.addTab(self.sectors_tab, "Secteurs")
        
        # Detailed data tab
        self.data_tab = QWidget()
        self.setup_data_tab()
        self.charts_tabs.addTab(self.data_tab, "Données détaillées")
        
        main_layout.addWidget(self.charts_tabs)
    
    def setup_trends_tab(self):
        """
        Set up the revenue and profit trends tab.
        """
        tab_layout = QVBoxLayout(self.trends_tab)
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.setSpacing(15)
        
        # Create chart
        self.trends_chart = QChart()
        self.trends_chart.setTitle("Évolution du chiffre d'affaires et du bénéfice")
        self.trends_chart.setTitleFont(QFont("Arial", 12))
        self.trends_chart.setTitleBrush(QBrush(QColor("#F8FAFC")))
        self.trends_chart.setBackgroundBrush(QBrush(QColor("#1E293B")))
        self.trends_chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Configure legend
        legend = self.trends_chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)
        legend.setFont(QFont("Arial", 10))
        # Set light text color for better visibility on dark background
        legend.setLabelBrush(QBrush(QColor("#F8FAFC")))
        # Optional: add a semi-transparent background to the legend
        legend.setBackgroundVisible(True)
        legend.setColor(QColor(30, 41, 59, 200))  # Semi-transparent dark blue
        legend.setBrush(QBrush(QColor(30, 41, 59, 200)))
        
        # Enable tooltips
        self.trends_chart.setToolTip("Passez la souris sur un point pour voir les détails")
        
        # Create revenue series for current year
        self.revenue_series = QSplineSeries()
        self.revenue_series.setName("Chiffre d'affaires (actuel)")
        pen = QPen(QColor("#3B82F6"))
        pen.setWidth(3)
        self.revenue_series.setPen(pen)
        # Enable tooltips
        self.revenue_series.setPointsVisible(True)
        self.revenue_series.setPointLabelsVisible(False)
        
        # Create revenue series for previous year
        self.revenue_prev_series = QSplineSeries()
        self.revenue_prev_series.setName("Chiffre d'affaires (N-1)")
        pen = QPen(QColor("#93C5FD"))  # Lighter blue
        pen.setWidth(2)
        pen.setStyle(Qt.DashLine)
        self.revenue_prev_series.setPen(pen)
        # Enable tooltips
        self.revenue_prev_series.setPointsVisible(True)
        self.revenue_prev_series.setPointLabelsVisible(False)
        
        # Create profit series for current year
        self.profit_series = QSplineSeries()
        self.profit_series.setName("Bénéfice net (actuel)")
        pen = QPen(QColor("#10B981"))
        pen.setWidth(3)
        self.profit_series.setPen(pen)
        # Enable tooltips
        self.profit_series.setPointsVisible(True)
        self.profit_series.setPointLabelsVisible(False)
        
        # Create profit series for previous year
        self.profit_prev_series = QSplineSeries()
        self.profit_prev_series.setName("Bénéfice net (N-1)")
        pen = QPen(QColor("#6EE7B7"))  # Lighter green
        pen.setWidth(2)
        pen.setStyle(Qt.DashLine)
        self.profit_prev_series.setPen(pen)
        # Enable tooltips
        self.profit_prev_series.setPointsVisible(True)
        self.profit_prev_series.setPointLabelsVisible(False)
        
        # Connect signals for tooltips
        self.revenue_series.hovered.connect(self.show_point_tooltip)
        self.revenue_prev_series.hovered.connect(self.show_point_tooltip)
        self.profit_series.hovered.connect(self.show_point_tooltip)
        self.profit_prev_series.hovered.connect(self.show_point_tooltip)
        
        # Add series to chart
        self.trends_chart.addSeries(self.revenue_series)
        self.trends_chart.addSeries(self.revenue_prev_series)
        self.trends_chart.addSeries(self.profit_series)
        self.trends_chart.addSeries(self.profit_prev_series)
        
        # Create axes
        self.trends_axis_x = QBarCategoryAxis()
        self.trends_axis_y = QValueAxis()
        self.trends_axis_y.setLabelFormat("%d €")
        self.trends_axis_y.setTitleText("Montant (€)")
        self.trends_axis_y.setTitleBrush(QBrush(QColor("#CBD5E1")))
        self.trends_axis_y.setLabelsColor(QColor("#CBD5E1"))
        self.trends_axis_x.setLabelsColor(QColor("#CBD5E1"))
        
        # Add axes to chart
        self.trends_chart.addAxis(self.trends_axis_x, Qt.AlignBottom)
        self.trends_chart.addAxis(self.trends_axis_y, Qt.AlignLeft)
        
        self.revenue_series.attachAxis(self.trends_axis_x)
        self.revenue_series.attachAxis(self.trends_axis_y)
        self.revenue_prev_series.attachAxis(self.trends_axis_x)
        self.revenue_prev_series.attachAxis(self.trends_axis_y)
        self.profit_series.attachAxis(self.trends_axis_x)
        self.profit_series.attachAxis(self.trends_axis_y)
        self.profit_prev_series.attachAxis(self.trends_axis_x)
        self.profit_prev_series.attachAxis(self.trends_axis_y)
        
        # Create chart view
        chart_view = QChartView(self.trends_chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        tab_layout.addWidget(chart_view)
    
    def setup_expenses_tab(self):
        """
        Set up the expenses by category tab.
        """
        tab_layout = QVBoxLayout(self.expenses_tab)
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.setSpacing(15)
        
        # Create chart
        self.expenses_chart = QChart()
        self.expenses_chart.setTitle("Dépenses par catégorie")
        self.expenses_chart.setTitleFont(QFont("Arial", 12))
        self.expenses_chart.setTitleBrush(QBrush(QColor("#F8FAFC")))
        self.expenses_chart.setBackgroundBrush(QBrush(QColor("#1E293B")))
        self.expenses_chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Configure legend
        legend = self.expenses_chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)
        legend.setFont(QFont("Arial", 10))
        # Set light text color for better visibility on dark background
        legend.setLabelBrush(QBrush(QColor("#F8FAFC")))
        # Optional: add a semi-transparent background to the legend
        legend.setBackgroundVisible(True)
        legend.setColor(QColor(30, 41, 59, 200))  # Semi-transparent dark blue
        legend.setBrush(QBrush(QColor(30, 41, 59, 200)))
        
        # Create bar series
        self.expenses_series = QBarSeries()
        
        # Create bar sets
        self.fixed_expenses_set = QBarSet("Dépenses fixes")
        self.fixed_expenses_set.setColor(QColor("#3B82F6"))
        
        self.variable_expenses_set = QBarSet("Dépenses variables")
        self.variable_expenses_set.setColor(QColor("#10B981"))
        
        # Add bar sets to series
        self.expenses_series.append(self.fixed_expenses_set)
        self.expenses_series.append(self.variable_expenses_set)
        
        # Add series to chart
        self.expenses_chart.addSeries(self.expenses_series)
        
        # Create axes
        self.expenses_axis_x = QBarCategoryAxis()
        self.expenses_axis_y = QValueAxis()
        self.expenses_axis_y.setLabelFormat("%d €")
        self.expenses_axis_y.setTitleText("Montant (€)")
        self.expenses_axis_y.setTitleBrush(QBrush(QColor("#CBD5E1")))
        self.expenses_axis_y.setLabelsColor(QColor("#CBD5E1"))
        self.expenses_axis_x.setLabelsColor(QColor("#CBD5E1"))
        
        # Add axes to chart
        self.expenses_chart.addAxis(self.expenses_axis_x, Qt.AlignBottom)
        self.expenses_chart.addAxis(self.expenses_axis_y, Qt.AlignLeft)
        
        self.expenses_series.attachAxis(self.expenses_axis_x)
        self.expenses_series.attachAxis(self.expenses_axis_y)
        
        # Create chart view
        chart_view = QChartView(self.expenses_chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        tab_layout.addWidget(chart_view)
    
    def setup_sectors_tab(self):
        """
        Set up the revenue by sector tab.
        """
        tab_layout = QVBoxLayout(self.sectors_tab)
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.setSpacing(15)
        
        # Create chart
        self.sectors_chart = QChart()
        self.sectors_chart.setTitle("Répartition des revenus par secteur d'activité")
        self.sectors_chart.setTitleFont(QFont("Arial", 12))
        self.sectors_chart.setTitleBrush(QBrush(QColor("#F8FAFC")))
        self.sectors_chart.setBackgroundBrush(QBrush(QColor("#1E293B")))
        self.sectors_chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Configure legend
        legend = self.sectors_chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)
        legend.setFont(QFont("Arial", 10))
        # Set light text color for better visibility on dark background
        legend.setLabelBrush(QBrush(QColor("#F8FAFC")))
        # Optional: add a semi-transparent background to the legend
        legend.setBackgroundVisible(True)
        legend.setColor(QColor(30, 41, 59, 200))  # Semi-transparent dark blue
        legend.setBrush(QBrush(QColor(30, 41, 59, 200)))
        
        # Create pie series
        self.sectors_series = QPieSeries()
        # Note: QPieSeries doesn't have setLabelsColor method
        # We'll set the label color for each slice individually
        
        # Add series to chart
        self.sectors_chart.addSeries(self.sectors_series)
        
        # Create chart view
        chart_view = QChartView(self.sectors_chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        tab_layout.addWidget(chart_view)
    
    def setup_data_tab(self):
        """
        Set up the detailed data tab.
        """
        tab_layout = QVBoxLayout(self.data_tab)
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.setSpacing(15)
        
        # Filters
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(15)
        
        # Category filter
        category_label = QLabel("Catégorie:")
        category_label.setStyleSheet("color: #F8FAFC;")
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Toutes", "Revenus", "Dépenses", "Profits"])
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                selection-background-color: #3B82F6;
            }
        """)
        self.category_combo.currentIndexChanged.connect(self.filter_data)
        
        # Date range filter
        date_label = QLabel("Dates:")
        date_label.setStyleSheet("color: #F8FAFC;")
        
        self.start_date = QLineEdit()
        self.start_date.setPlaceholderText("Date début")
        self.start_date.setStyleSheet("""
            QLineEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 100px;
            }
        """)
        
        date_separator = QLabel("au")
        date_separator.setStyleSheet("color: #F8FAFC;")
        
        self.end_date = QLineEdit()
        self.end_date.setPlaceholderText("Date fin")
        self.end_date.setStyleSheet("""
            QLineEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 100px;
            }
        """)
        
        self.apply_filter_btn = QPushButton("Appliquer")
        self.apply_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.apply_filter_btn.clicked.connect(self.filter_data)
        
        filters_layout.addWidget(category_label)
        filters_layout.addWidget(self.category_combo)
        filters_layout.addSpacing(20)
        filters_layout.addWidget(date_label)
        filters_layout.addWidget(self.start_date)
        filters_layout.addWidget(date_separator)
        filters_layout.addWidget(self.end_date)
        filters_layout.addWidget(self.apply_filter_btn)
        filters_layout.addStretch()
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_layout.setSpacing(10)
        
        self.export_pdf_btn = QPushButton("PDF")
        self.export_pdf_btn.setIcon(QIcon("src/resources/icons/pdf.png"))
        self.export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        self.export_pdf_btn.clicked.connect(lambda: self.export_data("pdf"))
        
        self.export_excel_btn = QPushButton("Excel")
        self.export_excel_btn.setIcon(QIcon("src/resources/icons/excel.png"))
        self.export_excel_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.export_excel_btn.clicked.connect(lambda: self.export_data("excel"))
        
        self.export_csv_btn = QPushButton("CSV")
        self.export_csv_btn.setIcon(QIcon("src/resources/icons/csv.png"))
        self.export_csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.export_csv_btn.clicked.connect(lambda: self.export_data("csv"))
        
        export_layout.addWidget(self.export_pdf_btn)
        export_layout.addWidget(self.export_excel_btn)
        export_layout.addWidget(self.export_csv_btn)
        
        # Combine filters and export buttons
        top_layout = QHBoxLayout()
        top_layout.addLayout(filters_layout)
        top_layout.addLayout(export_layout)
        
        tab_layout.addLayout(top_layout)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels([
            "Date", "Catégorie", "Description", "Montant", "Tendance"
        ])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setStyleSheet("""
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
        
        tab_layout.addWidget(self.data_table)
    
    def show_point_tooltip(self, point, state):
        """
        Show tooltip when hovering over a point in the chart.
        
        Args:
            point: The point being hovered
            state: True if the point is being hovered, False otherwise
        """
        if state:
            # Get the series that triggered the hover
            sender = self.sender()
            
            # Get the category (date) for this point
            category = self.trends_axis_x.categories()[int(point.x())]
            
            # Format the value
            value = int(point.y())
            formatted_value = f"{value:,} €".replace(",", " ")
            
            # Determine if it's current or previous year
            year_label = ""
            if sender == self.revenue_series or sender == self.profit_series:
                year_label = "Année actuelle"
            else:
                year_label = "Année précédente"
            
            # Determine if it's revenue or profit
            type_label = ""
            if sender == self.revenue_series or sender == self.revenue_prev_series:
                type_label = "Chiffre d'affaires"
            else:
                type_label = "Bénéfice net"
            
            # Set tooltip text
            tooltip = f"{category} - {year_label}\n{type_label}: {formatted_value}"
            
            # Show tooltip
            QToolTip.showText(QCursor.pos(), tooltip)
    
    def refresh_data(self):
        """
        Refresh the financial data.
        """
        # In a real application, this would fetch data from the database
        # For this demo, we'll use random data
        
        # Update KPI cards
        revenue = random.randint(50000, 200000)
        profit = random.randint(10000, 50000)
        gross_margin = random.randint(30, 60)
        net_margin = random.randint(10, 30)
        
        accounts_receivable = random.randint(20000, 80000)
        accounts_payable = random.randint(10000, 50000)
        cash_flow = random.randint(5000, 30000)
        roi = random.randint(5, 25)
        
        self.revenue_card.value_label.setText(f"{revenue:,}".replace(",", " "))
        self.profit_card.value_label.setText(f"{profit:,}".replace(",", " "))
        self.gross_margin_card.value_label.setText(f"{gross_margin}")
        self.net_margin_card.value_label.setText(f"{net_margin}")
        
        self.accounts_receivable_card.value_label.setText(f"{accounts_receivable:,}".replace(",", " "))
        self.accounts_payable_card.value_label.setText(f"{accounts_payable:,}".replace(",", " "))
        self.cash_flow_card.value_label.setText(f"{cash_flow:,}".replace(",", " "))
        self.roi_card.value_label.setText(f"{roi}")
        
        # Update trends chart
        self.revenue_series.clear()
        self.revenue_prev_series.clear()
        self.profit_series.clear()
        self.profit_prev_series.clear()
        
        # Generate data based on selected period
        period_index = self.period_combo.currentIndex()
        
        if period_index == 0:  # Today (hourly)
            categories = ["8h", "10h", "12h", "14h", "16h", "18h"]
        elif period_index == 1:  # This week (daily)
            categories = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        elif period_index == 2:  # This month (weekly)
            categories = ["Sem 1", "Sem 2", "Sem 3", "Sem 4"]
        elif period_index == 3:  # This quarter (monthly)
            categories = ["Jan", "Fév", "Mar"]
        else:  # This year (quarterly)
            categories = ["T1", "T2", "T3", "T4"]
        
        self.trends_axis_x.clear()
        self.trends_axis_x.append(categories)
        
        max_revenue = 0
        
        # Generate data for current year
        current_year_data = []
        for i in range(len(categories)):
            revenue_value = random.randint(10000, 100000)
            profit_value = random.randint(2000, 30000)
            
            self.revenue_series.append(i, revenue_value)
            self.profit_series.append(i, profit_value)
            
            current_year_data.append((revenue_value, profit_value))
            max_revenue = max(max_revenue, revenue_value)
        
        # Generate data for previous year (slightly lower values on average)
        for i in range(len(categories)):
            # Use current year data as a reference, but with some variation
            # Previous year values are typically 80-95% of current year
            current_revenue, current_profit = current_year_data[i]
            
            # Apply a reduction factor with some randomness
            revenue_factor = random.uniform(0.80, 0.95)
            profit_factor = random.uniform(0.75, 0.90)
            
            prev_revenue_value = int(current_revenue * revenue_factor)
            prev_profit_value = int(current_profit * profit_factor)
            
            self.revenue_prev_series.append(i, prev_revenue_value)
            self.profit_prev_series.append(i, prev_profit_value)
            
            max_revenue = max(max_revenue, prev_revenue_value)
        
        self.trends_axis_y.setRange(0, max_revenue * 1.1)
        
        # Update expenses chart
        self.fixed_expenses_set.remove(0, self.fixed_expenses_set.count())
        self.variable_expenses_set.remove(0, self.variable_expenses_set.count())
        
        self.expenses_axis_x.clear()
        self.expenses_axis_x.append(categories)
        
        max_expense = 0
        
        for i in range(len(categories)):
            fixed_expense = random.randint(5000, 20000)
            variable_expense = random.randint(3000, 15000)
            
            self.fixed_expenses_set.append(fixed_expense)
            self.variable_expenses_set.append(variable_expense)
            
            max_expense = max(max_expense, fixed_expense + variable_expense)
        
        self.expenses_axis_y.setRange(0, max_expense * 1.1)
        
        # Update sectors chart
        self.sectors_series.clear()
        
        sectors = {
            "Impression 3D": random.randint(20, 40),
            "Modélisation": random.randint(15, 35),
            "Conception": random.randint(10, 30),
            "Prototypage": random.randint(5, 25),
            "Autres": random.randint(5, 15)
        }
        
        for sector, value in sectors.items():
            slice = self.sectors_series.append(sector, value)
            slice.setLabelVisible(True)
            slice.setLabelColor(QColor("#CBD5E1"))  # Set label color for each slice individually
            
            # Set slice colors
            if sector == "Impression 3D":
                slice.setColor(QColor("#3B82F6"))
            elif sector == "Modélisation":
                slice.setColor(QColor("#10B981"))
            elif sector == "Conception":
                slice.setColor(QColor("#F59E0B"))
            elif sector == "Prototypage":
                slice.setColor(QColor("#8B5CF6"))
            else:
                slice.setColor(QColor("#EC4899"))
        
        # Update data table
        self.populate_data_table()
    
    def populate_data_table(self):
        """
        Populate the data table with financial data.
        """
        # Clear table
        self.data_table.setRowCount(0)
        
        # Generate random data
        categories = ["Revenus", "Dépenses", "Profits"]
        descriptions = {
            "Revenus": ["Ventes de produits", "Services de conception", "Abonnements", "Formations"],
            "Dépenses": ["Matières premières", "Salaires", "Loyer", "Équipement", "Marketing"],
            "Profits": ["Marge brute", "Marge nette", "Bénéfice opérationnel"]
        }
        
        # Get current date
        current_date = datetime.datetime.now()
        
        # Generate 20 random entries
        for i in range(20):
            # Random date in the last 30 days
            date = current_date - datetime.timedelta(days=random.randint(0, 30))
            date_str = date.strftime("%d/%m/%Y")
            
            # Random category
            category = random.choice(categories)
            
            # Random description
            description = random.choice(descriptions[category])
            
            # Random amount
            if category == "Revenus":
                amount = random.randint(1000, 10000)
            elif category == "Dépenses":
                amount = -random.randint(500, 5000)
            else:  # Profits
                amount = random.randint(200, 3000)
            
            # Random trend
            trend = random.uniform(-10, 10)
            
            # Add row to table
            row = self.data_table.rowCount()
            self.data_table.insertRow(row)
            
            # Date
            date_item = QTableWidgetItem(date_str)
            self.data_table.setItem(row, 0, date_item)
            
            # Category
            category_item = QTableWidgetItem(category)
            self.data_table.setItem(row, 1, category_item)
            
            # Description
            description_item = QTableWidgetItem(description)
            self.data_table.setItem(row, 2, description_item)
            
            # Amount
            amount_item = QTableWidgetItem(f"{amount:,} €".replace(",", " "))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Set color based on amount
            if amount > 0:
                amount_item.setForeground(QColor("#10B981"))  # Green for positive
            elif amount < 0:
                amount_item.setForeground(QColor("#EF4444"))  # Red for negative
            
            self.data_table.setItem(row, 3, amount_item)
            
            # Trend
            trend_item = QTableWidgetItem(f"{trend:+.1f}%")
            trend_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Set color based on trend
            if trend > 0:
                trend_item.setForeground(QColor("#10B981"))  # Green for positive
            elif trend < 0:
                trend_item.setForeground(QColor("#EF4444"))  # Red for negative
            
            self.data_table.setItem(row, 4, trend_item)
    
    def filter_data(self):
        """
        Filter the data table based on selected filters.
        """
        category_filter = self.category_combo.currentText()
        
        # Get date filters
        start_date_text = self.start_date.text()
        end_date_text = self.end_date.text()
        
        # Parse dates if provided
        start_date = None
        end_date = None
        
        if start_date_text:
            try:
                start_date = datetime.datetime.strptime(start_date_text, "%d/%m/%Y")
            except ValueError:
                QMessageBox.warning(self, "Format de date invalide", "Le format de date doit être JJ/MM/AAAA")
                return
        
        if end_date_text:
            try:
                end_date = datetime.datetime.strptime(end_date_text, "%d/%m/%Y")
            except ValueError:
                QMessageBox.warning(self, "Format de date invalide", "Le format de date doit être JJ/MM/AAAA")
                return
        
        # Apply filters
        for row in range(self.data_table.rowCount()):
            row_hidden = False
            
            # Category filter
            if category_filter != "Toutes":
                category_item = self.data_table.item(row, 1)
                if category_item and category_item.text() != category_filter:
                    row_hidden = True
            
            # Date filter
            if not row_hidden and (start_date or end_date):
                date_item = self.data_table.item(row, 0)
                if date_item:
                    try:
                        row_date = datetime.datetime.strptime(date_item.text(), "%d/%m/%Y")
                        
                        if start_date and row_date < start_date:
                            row_hidden = True
                        
                        if end_date and row_date > end_date:
                            row_hidden = True
                    except ValueError:
                        # Skip invalid dates
                        pass
            
            self.data_table.setRowHidden(row, row_hidden)
    
    def export_data(self, format_type=None):
        """
        Export financial data to a file.
        
        Args:
            format_type: The format to export to (pdf, excel, csv)
        """
        if not format_type:
            # Show export options dialog
            options = ["PDF", "Excel", "CSV"]
            format_type, ok = QInputDialog.getItem(
                self, "Format d'exportation", "Choisissez un format:", options, 0, False
            )
            
            if not ok:
                return
            
            format_type = format_type.lower()
        
        # Get file path
        file_filter = ""
        if format_type == "pdf":
            file_filter = "PDF Files (*.pdf)"
        elif format_type == "excel":
            file_filter = "Excel Files (*.xlsx)"
        elif format_type == "csv":
            file_filter = "CSV Files (*.csv)"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les données", "", file_filter
        )
        
        if not file_path:
            return
        
        try:
            if format_type == "csv":
                self.export_to_csv(file_path)
            elif format_type == "excel":
                self.export_to_excel(file_path)
            elif format_type == "pdf":
                self.export_to_pdf(file_path)
            
            QMessageBox.information(self, "Exportation réussie", f"Données exportées vers {file_path}")
        except Exception as e:
            logging.error(f"Error exporting data: {str(e)}")
            QMessageBox.warning(self, "Erreur d'exportation", f"Une erreur est survenue: {str(e)}")
    
    def export_to_csv(self, file_path):
        """
        Export data to CSV file.
        
        Args:
            file_path: Path to save the CSV file
        """
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            headers = []
            for col in range(self.data_table.columnCount()):
                headers.append(self.data_table.horizontalHeaderItem(col).text())
            
            writer.writerow(headers)
            
            # Write data
            for row in range(self.data_table.rowCount()):
                if not self.data_table.isRowHidden(row):
                    row_data = []
                    for col in range(self.data_table.columnCount()):
                        item = self.data_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    
                    writer.writerow(row_data)
    
    def export_to_excel(self, file_path):
        """
        Export data to Excel file.
        
        Args:
            file_path: Path to save the Excel file
        """
        # In a real application, this would use a library like openpyxl or xlsxwriter
        # For this demo, we'll just export as CSV
        self.export_to_csv(file_path)
    
    def export_to_pdf(self, file_path):
        """
        Export data to PDF file.
        
        Args:
            file_path: Path to save the PDF file
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            # Ensure file has .pdf extension
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            
            # Create document
            doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            title = Paragraph("Rapport Financier - NovaModelis", title_style)
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # Add period information
            period_text = f"Période: {self.period_combo.currentText()}"
            period = Paragraph(period_text, styles['Normal'])
            elements.append(period)
            elements.append(Spacer(1, 20))
            
            # Get data from table
            data = [["Date", "Catégorie", "Description", "Montant", "Tendance"]]  # Header row
            
            for row in range(self.data_table.rowCount()):
                if not self.data_table.isRowHidden(row):
                    row_data = []
                    for col in range(self.data_table.columnCount()):
                        item = self.data_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
            
            # Create table
            table = Table(data)
            
            # Style the table
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
            
            # Apply alternating row colors
            for i in range(1, len(data)):
                if i % 2 == 0:
                    style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
            
            table.setStyle(style)
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            return True
        except ImportError:
            QMessageBox.warning(
                self, 
                "Dépendance manquante", 
                "La bibliothèque reportlab est nécessaire pour l'exportation PDF. "
                "Veuillez l'installer avec 'pip install reportlab'."
            )
            return False
        except Exception as e:
            logging.error(f"Error exporting to PDF: {str(e)}")
            QMessageBox.warning(
                self, 
                "Erreur d'exportation", 
                f"Une erreur est survenue lors de l'exportation en PDF: {str(e)}"
            )
            return False
