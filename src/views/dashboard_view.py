"""
Dashboard view for the application.
"""
import os
import sys
import logging
import random
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QButtonGroup, QProgressBar
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QFont, QColor, QPainter
from sqlalchemy import func

# For the graph
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from models import (
    Order, OrderStatus, PaymentStatus, PrintJob, PrintJobStatus, 
    Customer, CustomerEmail, EmailStatus, Printer
)
import config


class MplCanvas(FigureCanvas):
    """
    Canvas for matplotlib figure.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


class StatCard(QFrame):
    """
    Stat card widget for displaying statistics.
    """
    def __init__(self, title, value, icon_path, color="#3B82F6"):
        super().__init__()
        
        self.setObjectName("statCard")
        self.setStyleSheet(f"""
            #statCard {{
                background-color: #1E293B;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(32, 32)))
        
        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #94A3B8; font-size: 14px;")
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet("color: #F8FAFC; font-size: 36px; font-weight: bold;")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        
        # Add widgets to layout
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()


class DashboardView(QWidget):
    """
    Dashboard view for the application.
    """
    # Signals to open views with specific status filters
    open_orders_with_status = Signal(object)
    open_printers_with_status = Signal(object)
    open_customers_with_message_status = Signal(object)
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for the entire dashboard
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
        
        # Create a widget to hold all dashboard content
        dashboard_content = QWidget()
        dashboard_content.setObjectName("dashboardContent")
        dashboard_content.setStyleSheet("""
            #dashboardContent {
                background-color: #0F172A;
            }
        """)
        
        # Content layout
        content_layout = QVBoxLayout(dashboard_content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_title = QLabel("Tableau de bord")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
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
        refresh_btn.clicked.connect(self.refresh_data)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        
        content_layout.addLayout(header_layout)
        
        # Graph section
        graph_frame = QFrame()
        graph_frame.setObjectName("graphFrame")
        graph_frame.setStyleSheet("""
            #graphFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        graph_frame.setMinimumHeight(300)
        
        graph_layout = QVBoxLayout(graph_frame)
        graph_layout.setContentsMargins(15, 15, 15, 15)
        graph_layout.setSpacing(10)
        
        # Graph header
        graph_header = QHBoxLayout()
        graph_title = QLabel("Aperçu financier")
        graph_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        # Graph type buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.graph_button_group = QButtonGroup(self)
        
        credit_btn = QPushButton("Crédit")
        credit_btn.setCheckable(True)
        credit_btn.setChecked(True)  # Default selected
        credit_btn.setCursor(Qt.PointingHandCursor)
        credit_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton:checked {
                background-color: #3B82F6;
            }
        """)
        
        debit_btn = QPushButton("Débit")
        debit_btn.setCheckable(True)
        debit_btn.setCursor(Qt.PointingHandCursor)
        debit_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton:checked {
                background-color: #3B82F6;
            }
        """)
        
        purchases_btn = QPushButton("Achats")
        purchases_btn.setCheckable(True)
        purchases_btn.setCursor(Qt.PointingHandCursor)
        purchases_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #F8FAFC;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton:checked {
                background-color: #3B82F6;
            }
        """)
        
        self.graph_button_group.addButton(credit_btn, 1)
        self.graph_button_group.addButton(debit_btn, 2)
        self.graph_button_group.addButton(purchases_btn, 3)
        
        button_layout.addWidget(credit_btn)
        button_layout.addWidget(debit_btn)
        button_layout.addWidget(purchases_btn)
        
        graph_header.addWidget(graph_title)
        graph_header.addStretch()
        graph_header.addLayout(button_layout)
        
        graph_layout.addLayout(graph_header)
        
        # Graph canvas
        self.graph_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        graph_layout.addWidget(self.graph_canvas)
        
        # Connect button signals
        self.graph_button_group.buttonClicked.connect(self.update_graph)
        
        content_layout.addWidget(graph_frame)
        
        # E-commerce sales histogram
        ecommerce_frame = QFrame()
        ecommerce_frame.setObjectName("ecommerceFrame")
        ecommerce_frame.setStyleSheet("""
            #ecommerceFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        ecommerce_frame.setMinimumHeight(350)
        
        ecommerce_layout = QVBoxLayout(ecommerce_frame)
        ecommerce_layout.setContentsMargins(15, 15, 15, 15)
        ecommerce_layout.setSpacing(10)
        
        # Ecommerce header
        ecommerce_header = QHBoxLayout()
        ecommerce_title = QLabel("Ventes par site e-commerce (année en cours)")
        ecommerce_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        ecommerce_header.addWidget(ecommerce_title)
        ecommerce_header.addStretch()
        
        ecommerce_layout.addLayout(ecommerce_header)
        
        # Ecommerce canvas
        self.ecommerce_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        ecommerce_layout.addWidget(self.ecommerce_canvas)
        
        content_layout.addWidget(ecommerce_frame)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Create stat cards (will be populated in refresh_data)
        self.orders_card = StatCard("Commandes du mois", "0", "src/resources/icons/order.png")
        self.revenue_card = StatCard("Revenu du mois", "0 €", "src/resources/icons/revenue.png", "#10B981")
        self.customers_card = StatCard("Clients totaux", "0", "src/resources/icons/customer.png", "#F59E0B")
        self.printers_card = StatCard("Imprimantes actives", "0", "src/resources/icons/printer.png", "#EF4444")
        
        stats_layout.addWidget(self.orders_card)
        stats_layout.addWidget(self.revenue_card)
        stats_layout.addWidget(self.customers_card)
        stats_layout.addWidget(self.printers_card)
        
        content_layout.addLayout(stats_layout)
        
        # Tables grid
        tables_grid = QGridLayout()
        tables_grid.setSpacing(15)
        
        # Recent orders
        orders_frame = QFrame()
        orders_frame.setObjectName("ordersFrame")
        orders_frame.setStyleSheet("""
            #ordersFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        orders_layout = QVBoxLayout(orders_frame)
        orders_layout.setContentsMargins(15, 15, 15, 15)
        orders_layout.setSpacing(10)
        
        orders_header = QHBoxLayout()
        orders_title = QLabel("Commandes récentes")
        orders_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        view_all_orders = QPushButton("Voir tout")
        view_all_orders.setCursor(Qt.PointingHandCursor)
        view_all_orders.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3B82F6;
                border: none;
            }
            QPushButton:hover {
                color: #2563EB;
            }
        """)
        view_all_orders.clicked.connect(self.view_all_new_orders)
        
        orders_header.addWidget(orders_title)
        orders_header.addStretch()
        orders_header.addWidget(view_all_orders)
        
        orders_layout.addLayout(orders_header)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["N° commande", "Client", "Date", "Montant", "Statut"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setStyleSheet("""
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
        
        orders_layout.addWidget(self.orders_table)
        
        # Active print jobs
        jobs_frame = QFrame()
        jobs_frame.setObjectName("jobsFrame")
        jobs_frame.setStyleSheet("""
            #jobsFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        jobs_layout = QVBoxLayout(jobs_frame)
        jobs_layout.setContentsMargins(15, 15, 15, 15)
        jobs_layout.setSpacing(10)
        
        jobs_header = QHBoxLayout()
        jobs_title = QLabel("Travaux d'impression actifs")
        jobs_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        view_all_jobs = QPushButton("Voir tout")
        view_all_jobs.setCursor(Qt.PointingHandCursor)
        view_all_jobs.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3B82F6;
                border: none;
            }
            QPushButton:hover {
                color: #2563EB;
            }
        """)
        view_all_jobs.clicked.connect(self.view_all_active_print_jobs)
        
        jobs_header.addWidget(jobs_title)
        jobs_header.addStretch()
        jobs_header.addWidget(view_all_jobs)
        
        jobs_layout.addLayout(jobs_header)
        
        # Jobs table
        self.jobs_table = QTableWidget()
        self.jobs_table.setColumnCount(5)
        self.jobs_table.setHorizontalHeaderLabels(["Nom du travail", "Imprimante", "Démarré", "Progression", "Fin estimée"])
        self.jobs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.jobs_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.jobs_table.verticalHeader().setVisible(False)
        self.jobs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.jobs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.jobs_table.setAlternatingRowColors(True)
        self.jobs_table.setStyleSheet("""
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
        
        jobs_layout.addWidget(self.jobs_table)
        
        # Unread messages
        messages_frame = QFrame()
        messages_frame.setObjectName("messagesFrame")
        messages_frame.setStyleSheet("""
            #messagesFrame {
                background-color: #1E293B;
                border-radius: 8px;
            }
        """)
        
        messages_layout = QVBoxLayout(messages_frame)
        messages_layout.setContentsMargins(15, 15, 15, 15)
        messages_layout.setSpacing(10)
        
        messages_header = QHBoxLayout()
        messages_title = QLabel("Messages non lus")
        messages_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        view_all_messages = QPushButton("Voir tout")
        view_all_messages.setCursor(Qt.PointingHandCursor)
        view_all_messages.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3B82F6;
                border: none;
            }
            QPushButton:hover {
                color: #2563EB;
            }
        """)
        view_all_messages.clicked.connect(self.view_all_unread_messages)
        
        messages_header.addWidget(messages_title)
        messages_header.addStretch()
        messages_header.addWidget(view_all_messages)
        
        messages_layout.addLayout(messages_header)
        
        # Messages table
        self.messages_table = QTableWidget()
        self.messages_table.setColumnCount(4)
        self.messages_table.setHorizontalHeaderLabels(["De", "Sujet", "Date", "Actions"])
        self.messages_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.messages_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.messages_table.verticalHeader().setVisible(False)
        self.messages_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.messages_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.messages_table.setAlternatingRowColors(True)
        self.messages_table.setStyleSheet("""
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
        
        messages_layout.addWidget(self.messages_table)
        
        # Add widgets to tables grid
        tables_grid.addWidget(orders_frame, 0, 0)
        tables_grid.addWidget(jobs_frame, 0, 1)
        tables_grid.addWidget(messages_frame, 1, 0, 1, 2)
        
        content_layout.addLayout(tables_grid)
        
        # Set the scroll area content
        scroll_area.setWidget(dashboard_content)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
    
    def __init__(self, db):
        super().__init__()
        
        self.db = db
        
        # Store current annotations for tooltips
        self.current_tooltip = None
        self.current_ecommerce_tooltip = None
        
        self.setup_ui()
        self.refresh_data()
    
    def on_hover(self, event):
        """
        Handle hover events on the graph to show tooltips.
        
        Args:
            event: The mouse event
        """
        # Remove previous tooltip if it exists
        if hasattr(self, 'current_tooltip') and self.current_tooltip:
            self.current_tooltip.remove()
            self.current_tooltip = None
            self.graph_canvas.draw_idle()
        
        if event.inaxes:
            # Get the x and y coordinates of the mouse
            x, y = event.xdata, event.ydata
            
            # Get the current axes
            ax = event.inaxes
            
            # Get the months list
            months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
            
            # Find the closest point
            if x is not None and y is not None:
                # Round to the nearest integer for x to get the month index
                x_int = int(round(x))
                
                # Make sure x_int is within valid range
                if 0 <= x_int < len(months):
                    # Get the month name
                    month = months[x_int]
                    
                    # Format the value
                    value = f"{y:.2f} €"
                    
                    # Create tooltip text
                    tooltip = f"{month}: {value}"
                    
                    # Show tooltip
                    self.current_tooltip = ax.annotate(tooltip,
                                                     xy=(x, y),
                                                     xytext=(10, 10),
                                                     textcoords='offset points',
                                                     bbox=dict(boxstyle='round,pad=0.5', fc='#1E293B', ec='#334155', alpha=0.8),
                                                     color='#F8FAFC',
                                                     fontsize=9)
                    
                    # Redraw the canvas
                    self.graph_canvas.draw_idle()
    
    def update_graph(self, button):
        """
        Update the graph based on the selected button.
        
        Args:
            button: The button that was clicked.
        """
        # Clear the graph
        self.graph_canvas.axes.clear()
        
        # Set dark background style for the graph
        self.graph_canvas.fig.set_facecolor('#1E293B')
        self.graph_canvas.axes.set_facecolor('#1E293B')
        self.graph_canvas.axes.tick_params(colors='#94A3B8')
        self.graph_canvas.axes.spines['bottom'].set_color('#334155')
        self.graph_canvas.axes.spines['top'].set_color('#334155')
        self.graph_canvas.axes.spines['left'].set_color('#334155')
        self.graph_canvas.axes.spines['right'].set_color('#334155')
        self.graph_canvas.axes.xaxis.label.set_color('#94A3B8')
        self.graph_canvas.axes.yaxis.label.set_color('#94A3B8')
        self.graph_canvas.axes.title.set_color('#F8FAFC')
        
        # Get the current year and month
        now = datetime.now()
        current_year = now.year
        previous_year = current_year - 1
        
        # Months for x-axis
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        
        # Generate sample data for now (in a real app, this would come from the database)
        # This would be replaced with actual data from the database in a real application
        button_id = self.graph_button_group.id(button)
        
        # Generate random data for demonstration
        if button_id == 1:  # Credit
            current_year_data = [random.uniform(5000, 15000) for _ in range(12)]
            previous_year_data = [random.uniform(4000, 12000) for _ in range(12)]
            title = "Crédit mensuel"
            y_label = "Crédit (€)"
        elif button_id == 2:  # Debit
            current_year_data = [random.uniform(3000, 10000) for _ in range(12)]
            previous_year_data = [random.uniform(2500, 9000) for _ in range(12)]
            title = "Débit mensuel"
            y_label = "Débit (€)"
        else:  # Purchases
            current_year_data = [random.uniform(2000, 8000) for _ in range(12)]
            previous_year_data = [random.uniform(1500, 7000) for _ in range(12)]
            title = "Achats mensuels"
            y_label = "Achats (€)"
        
        # Plot the data
        x = np.arange(len(months))
        width = 0.35
        
        # Only show data up to the current month for the current year
        current_month = now.month
        current_year_plot_data = current_year_data[:current_month]
        
        # Plot previous year data with smooth curve
        # Use a polynomial of degree 5 for smoothing
        z = np.polyfit(x, previous_year_data, 5)
        p = np.poly1d(z)
        
        # Create smooth curve with more points
        xnew = np.linspace(0, len(months)-1, 100)  # 100 points for smooth curve
        smooth_prev = p(xnew)
        
        # Plot the smooth curve
        self.graph_canvas.axes.plot(xnew, smooth_prev, linestyle='-', color='#94A3B8', 
                                   linewidth=2, label=f'{previous_year}')
        
        # Add data points on the curve
        for i, month in enumerate(months):
            # Calculate the y-value on the curve for this x-point
            point_y = p(i)
            self.graph_canvas.axes.plot(i, point_y, marker='o', markersize=6, color='#94A3B8')
            
            # Add event handling for tooltips
            self.graph_canvas.mpl_connect('motion_notify_event', self.on_hover)
        
        # Plot current year data with smooth curve
        if current_month >= 3:  # Need at least 3 points for a reasonable polynomial
            # Use a polynomial of appropriate degree based on number of points
            degree = min(3, current_month-1)
            z_current = np.polyfit(x[:current_month], current_year_plot_data, degree)
            p_current = np.poly1d(z_current)
            
            # Create smooth curve with more points
            xnew_current = np.linspace(0, current_month-1, 50)  # 50 points for smooth curve
            smooth_current = p_current(xnew_current)
            
            # Plot the smooth curve
            self.graph_canvas.axes.plot(xnew_current, smooth_current, linestyle='-', 
                                      color='#3B82F6', linewidth=2, label=f'{current_year}')
            
            # Add data points on the curve
            for i in range(current_month):
                # Calculate the y-value on the curve for this x-point
                point_y = p_current(i)
                self.graph_canvas.axes.plot(i, point_y, marker='o', markersize=6, color='#3B82F6')
        
        # Set labels and title
        self.graph_canvas.axes.set_xlabel('Mois')
        self.graph_canvas.axes.set_ylabel(y_label)
        self.graph_canvas.axes.set_title(title)
        self.graph_canvas.axes.set_xticks(x)
        self.graph_canvas.axes.set_xticklabels(months)
        
        # Add legend
        self.graph_canvas.axes.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#F8FAFC')
        
        # Add grid
        self.graph_canvas.axes.grid(True, linestyle='--', alpha=0.3, color='#334155')
        
        # Update the canvas
        self.graph_canvas.draw()
    
    def on_ecommerce_hover(self, event):
        """
        Handle hover events on the e-commerce graph to show tooltips.
        
        Args:
            event: The mouse event
        """
        # Remove previous tooltip if it exists
        if hasattr(self, 'current_ecommerce_tooltip') and self.current_ecommerce_tooltip:
            self.current_ecommerce_tooltip.remove()
            self.current_ecommerce_tooltip = None
            self.ecommerce_canvas.draw_idle()
        
        if event.inaxes:
            # Get the x and y coordinates of the mouse
            x, y = event.xdata, event.ydata
            
            # Get the current axes
            ax = event.inaxes
            
            # Get the months list
            months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
            
            # Find the closest point
            if x is not None and y is not None:
                # Round to the nearest integer for x to get the month index
                x_int = int(round(x))
                
                # Make sure x_int is within valid range
                if 0 <= x_int < len(months):
                    # Get the month name
                    month = months[x_int]
                    
                    # Format the value
                    value = f"{y:.2f} €"
                    
                    # Create tooltip text
                    tooltip = f"{month}: {value}"
                    
                    # Show tooltip
                    self.current_ecommerce_tooltip = ax.annotate(tooltip,
                                                               xy=(x, y),
                                                               xytext=(10, 10),
                                                               textcoords='offset points',
                                                               bbox=dict(boxstyle='round,pad=0.5', fc='#1E293B', ec='#334155', alpha=0.8),
                                                               color='#F8FAFC',
                                                               fontsize=9)
                    
                    # Redraw the canvas
                    self.ecommerce_canvas.draw_idle()
    
    def update_ecommerce_histogram(self):
        """
        Update the e-commerce sales chart with smooth curves.
        """
        # Clear the graph
        self.ecommerce_canvas.axes.clear()
        
        # Set dark background style for the graph
        self.ecommerce_canvas.fig.set_facecolor('#1E293B')
        self.ecommerce_canvas.axes.set_facecolor('#1E293B')
        self.ecommerce_canvas.axes.tick_params(colors='#94A3B8')
        self.ecommerce_canvas.axes.spines['bottom'].set_color('#334155')
        self.ecommerce_canvas.axes.spines['top'].set_color('#334155')
        self.ecommerce_canvas.axes.spines['left'].set_color('#334155')
        self.ecommerce_canvas.axes.spines['right'].set_color('#334155')
        self.ecommerce_canvas.axes.xaxis.label.set_color('#94A3B8')
        self.ecommerce_canvas.axes.yaxis.label.set_color('#94A3B8')
        self.ecommerce_canvas.axes.title.set_color('#F8FAFC')
        
        # E-commerce platforms
        platforms = ['Shopify', 'Amazon', 'eBay', 'Cdiscount']
        platform_colors = {
            'Shopify': '#3B82F6',  # Blue
            'Amazon': '#F59E0B',   # Orange
            'eBay': '#10B981',     # Green
            'Cdiscount': '#EF4444' # Red
        }
        
        # Months for x-axis (current year only)
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # Use all months of the current year
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        
        # Generate sample data for each platform (for all months of the year)
        data = {
            'Shopify': [random.uniform(2000, 8000) for _ in range(12)],
            'Amazon': [random.uniform(3000, 10000) for _ in range(12)],
            'eBay': [random.uniform(1500, 6000) for _ in range(12)],
            'Cdiscount': [random.uniform(1000, 5000) for _ in range(12)]
        }
        
        # Set up the plot
        x = np.arange(len(months))
        
        # Plot smooth curves for each platform
        for platform, values in data.items():
            # Use a polynomial of appropriate degree based on number of points
            # For fewer months, use a lower degree to avoid overfitting
            if len(months) >= 4:
                degree = min(3, len(months) - 1)
            else:
                degree = 1  # Linear fit for 2-3 months
                
            z = np.polyfit(x, values, degree)
            p = np.poly1d(z)
            
            # Create smooth curve with more points
            xnew = np.linspace(0, len(months)-1, 100)  # 100 points for smooth curve
            smooth_values = p(xnew)
            
            # Plot the smooth curve
            self.ecommerce_canvas.axes.plot(xnew, smooth_values, linestyle='-', 
                                          color=platform_colors[platform], 
                                          linewidth=2, label=platform)
            
            # Add data points on the curve
            for i in range(len(months)):
                # Calculate the y-value on the curve for this x-point
                point_y = p(i)
                self.ecommerce_canvas.axes.plot(i, point_y, marker='o', 
                                              markersize=6, color=platform_colors[platform])
        
        # Add event handling for tooltips
        self.ecommerce_canvas.mpl_connect('motion_notify_event', self.on_ecommerce_hover)
        
        # Set labels and title
        self.ecommerce_canvas.axes.set_xlabel('Mois')
        self.ecommerce_canvas.axes.set_ylabel('Ventes (€)')
        self.ecommerce_canvas.axes.set_title('Ventes mensuelles par plateforme e-commerce')
        self.ecommerce_canvas.axes.set_xticks(x)
        self.ecommerce_canvas.axes.set_xticklabels(months, rotation=45, ha='right')
        
        # Add legend
        self.ecommerce_canvas.axes.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#F8FAFC')
        
        # Add grid
        self.ecommerce_canvas.axes.grid(True, linestyle='--', alpha=0.3, color='#334155')
        
        # Adjust layout to make room for the rotated x-axis labels
        self.ecommerce_canvas.fig.tight_layout()
        
        # Update the canvas
        self.ecommerce_canvas.draw()
    
    def view_all_new_orders(self):
        """
        Open the orders view with the NEW status filter.
        """
        # Emit signal to open orders view with NEW status
        self.open_orders_with_status.emit(OrderStatus.NEW)
    
    def view_all_active_print_jobs(self):
        """
        Open the printers view with the PRINTING status filter.
        """
        # Emit signal to open printers view with PRINTING status
        self.open_printers_with_status.emit(PrintJobStatus.PRINTING)
    
    def view_all_unread_messages(self):
        """
        Open the customers view with the NEW message status filter.
        """
        # Emit signal to open customers view with NEW message status
        self.open_customers_with_message_status.emit(EmailStatus.UNREAD)
    
    def refresh_data(self):
        """
        Refresh the dashboard data.
        """
        # Update the graphs
        selected_button = self.graph_button_group.checkedButton()
        if selected_button:
            self.update_graph(selected_button)
        
        # Update the e-commerce histogram
        self.update_ecommerce_histogram()
        try:
            # Get statistics
            # Get current month and year
            now = datetime.now()
            current_month = now.month
            current_year = now.year
            
            # Count orders for current month only
            total_orders = self.db.query(Order).filter(
                func.extract('month', Order.order_date) == current_month,
                func.extract('year', Order.order_date) == current_year
            ).count()
            # Calculate revenue for current month only
            total_revenue = self.db.query(Order).filter(
                Order.payment_status == PaymentStatus.PAID,
                func.extract('month', Order.order_date) == current_month,
                func.extract('year', Order.order_date) == current_year
            ).with_entities(
                func.sum(Order.total_amount)
            ).scalar() or 0
            total_customers = self.db.query(Customer).count()
            active_printers = self.db.query(PrintJob).filter(PrintJob.status == PrintJobStatus.PRINTING).count()
            
            # Update stat cards
            self.orders_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(total_orders))
            self.revenue_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(f"{total_revenue:.2f} €")
            self.customers_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(total_customers))
            self.printers_card.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(str(active_printers))
            
            # Get recent orders
            recent_orders = self.db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
            
            # Populate orders table
            self.orders_table.setRowCount(len(recent_orders))
            for i, order in enumerate(recent_orders):
                # Order number
                order_num_item = QTableWidgetItem(order.order_number)
                self.orders_table.setItem(i, 0, order_num_item)
                
                # Customer
                customer = self.db.query(Customer).filter(Customer.id == order.customer_id).first()
                customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Inconnu"
                customer_item = QTableWidgetItem(customer_name)
                self.orders_table.setItem(i, 1, customer_item)
                
                # Date
                date_item = QTableWidgetItem(order.order_date.strftime("%d %b %Y"))
                self.orders_table.setItem(i, 2, date_item)
                
                # Amount
                amount_item = QTableWidgetItem(f"{order.total_amount:.2f} €")
                self.orders_table.setItem(i, 3, amount_item)
                
                # Status
                status_item = QTableWidgetItem(order.status.value.capitalize())
                self.orders_table.setItem(i, 4, status_item)
            
            # Get active print jobs
            active_jobs = self.db.query(PrintJob).filter(PrintJob.status == PrintJobStatus.PRINTING).all()
            
            # Populate jobs table
            self.jobs_table.setRowCount(len(active_jobs))
            for i, job in enumerate(active_jobs):
                # Job name
                job_name_item = QTableWidgetItem(job.job_name)
                self.jobs_table.setItem(i, 0, job_name_item)
                
                # Printer
                printer = self.db.query(Printer).filter(Printer.id == job.printer_id).first()
                printer_name = printer.name if printer else "Inconnu"
                printer_item = QTableWidgetItem(printer_name)
                self.jobs_table.setItem(i, 1, printer_item)
                
                # Started
                started_item = QTableWidgetItem(job.started_at.strftime("%d %b %Y %H:%M"))
                self.jobs_table.setItem(i, 2, started_item)
                
                # Progress
                progress_widget = QProgressBar()
                progress_widget.setRange(0, 100)
                progress_widget.setValue(int(job.progress))
                progress_widget.setTextVisible(True)
                progress_widget.setFormat("%.1f%%" % job.progress)
                progress_widget.setStyleSheet("""
                    QProgressBar {
                        background-color: #334155;
                        border: none;
                        border-radius: 4px;
                        text-align: center;
                        color: #F8FAFC;
                    }
                    QProgressBar::chunk {
                        background-color: #3B82F6;
                        border-radius: 4px;
                    }
                """)
                self.jobs_table.setCellWidget(i, 3, progress_widget)
                
                # Estimated completion
                est_completion = job.estimated_completion_time
                est_completion_text = est_completion.strftime("%d %b %Y %H:%M") if est_completion else "Inconnue"
                est_completion_item = QTableWidgetItem(est_completion_text)
                self.jobs_table.setItem(i, 4, est_completion_item)
            
            # Get unread messages
            unread_messages = self.db.query(CustomerEmail).filter(
                CustomerEmail.is_incoming == True,
                CustomerEmail.status == EmailStatus.UNREAD
            ).order_by(CustomerEmail.received_at.desc()).all()
            
            # Populate messages table
            self.messages_table.setRowCount(len(unread_messages))
            for i, message in enumerate(unread_messages):
                # From
                customer = self.db.query(Customer).filter(Customer.id == message.customer_id).first()
                from_text = f"{customer.first_name} {customer.last_name}" if customer else "Inconnu"
                from_item = QTableWidgetItem(from_text)
                self.messages_table.setItem(i, 0, from_item)
                
                # Subject
                subject_item = QTableWidgetItem(message.subject)
                self.messages_table.setItem(i, 1, subject_item)
                
                # Date
                date_item = QTableWidgetItem(message.received_at.strftime("%d %b %Y %H:%M"))
                self.messages_table.setItem(i, 2, date_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 0, 5, 0)
                actions_layout.setSpacing(5)
                
                # View button
                view_btn = QPushButton()
                view_btn.setIcon(QIcon("src/resources/icons/view.png"))
                view_btn.setIconSize(QSize(16, 16))
                view_btn.setFixedSize(30, 30)
                view_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                view_btn.setToolTip("Voir le message")
                
                # Reply button
                reply_btn = QPushButton()
                reply_btn.setIcon(QIcon("src/resources/icons/reply.png"))
                reply_btn.setIconSize(QSize(16, 16))
                reply_btn.setFixedSize(30, 30)
                reply_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                reply_btn.setToolTip("Répondre")
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(reply_btn)
                actions_layout.addStretch()
                
                self.messages_table.setCellWidget(i, 3, actions_widget)
            
            logging.info("Dashboard data refreshed")
        except Exception as e:
            logging.error(f"Error refreshing dashboard data: {str(e)}")
