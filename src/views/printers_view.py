"""
Printers view for the application.
"""
import os
import sys
import logging
import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QDialog, QLineEdit, QFormLayout,
    QComboBox, QMessageBox, QSpinBox, QDoubleSpinBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QFont, QColor, QPainter
from sqlalchemy import func

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

from database.base import SessionLocal
from models import Printer, PrinterStatus, PrintJob, PrintJobStatus
import config


class ProgressBarWidget(QWidget):
    """
    Custom widget for displaying a progress bar with a value label.
    """
    def __init__(self, progress_value, parent=None):
        super().__init__(parent)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(int(progress_value))
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #334155;
                border: none;
                border-radius: 4px;
                height: 12px;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 4px;
            }
        """)
        
        # Value label
        self.value_label = QLabel(f"{progress_value:.1f}%")
        self.value_label.setStyleSheet("color: #F8FAFC;")
        
        # Add widgets to layout
        layout.addWidget(self.progress_bar, 1)
        layout.addWidget(self.value_label)


class PrinterDetailsDialog(QDialog):
    """
    Dialog for viewing and editing printer details.
    """
    def __init__(self, printer=None, parent=None):
        super().__init__(parent)
        
        self.printer = printer
        self.is_edit_mode = printer is not None
        
        self.setWindowTitle(f"{'Edit' if self.is_edit_mode else 'Add'} Printer")
        self.setMinimumSize(500, 600)
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_printer_data()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Name
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)
        
        # Model
        self.model_input = QLineEdit()
        form_layout.addRow("Model:", self.model_input)
        
        # Manufacturer
        self.manufacturer_input = QLineEdit()
        form_layout.addRow("Manufacturer:", self.manufacturer_input)
        
        # Build volume
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(10)
        
        self.volume_x_input = QSpinBox()
        self.volume_x_input.setRange(1, 1000)
        self.volume_x_input.setSuffix(" mm")
        
        self.volume_y_input = QSpinBox()
        self.volume_y_input.setRange(1, 1000)
        self.volume_y_input.setSuffix(" mm")
        
        self.volume_z_input = QSpinBox()
        self.volume_z_input.setRange(1, 1000)
        self.volume_z_input.setSuffix(" mm")
        
        volume_layout.addWidget(QLabel("X:"))
        volume_layout.addWidget(self.volume_x_input)
        volume_layout.addWidget(QLabel("Y:"))
        volume_layout.addWidget(self.volume_y_input)
        volume_layout.addWidget(QLabel("Z:"))
        volume_layout.addWidget(self.volume_z_input)
        
        form_layout.addRow("Build Volume:", volume_layout)
        
        # Status
        self.status_combo = QComboBox()
        for status in PrinterStatus:
            self.status_combo.addItem(status.value.capitalize(), status)
        form_layout.addRow("Status:", self.status_combo)
        
        # IP address
        self.ip_input = QLineEdit()
        form_layout.addRow("IP Address:", self.ip_input)
        
        # API key
        self.api_key_input = QLineEdit()
        form_layout.addRow("API Key:", self.api_key_input)
        
        # Power consumption
        self.consumption_input = QSpinBox()
        self.consumption_input.setRange(0, 2000)
        self.consumption_input.setSuffix(" W")
        self.consumption_input.setToolTip("Consommation électrique de l'imprimante en watts")
        form_layout.addRow("Consommation:", self.consumption_input)
        
        # Notes
        self.notes_input = QLineEdit()
        form_layout.addRow("Notes:", self.notes_input)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self.save_printer)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def load_printer_data(self):
        """
        Load printer data into the form.
        """
        if not self.printer:
            return
        
        self.name_input.setText(self.printer.name)
        self.model_input.setText(self.printer.model)
        self.manufacturer_input.setText(self.printer.manufacturer)
        self.volume_x_input.setValue(self.printer.build_volume_x)
        self.volume_y_input.setValue(self.printer.build_volume_y)
        self.volume_z_input.setValue(self.printer.build_volume_z)
        
        status_index = self.status_combo.findData(self.printer.status)
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)
        
        if self.printer.ip_address:
            self.ip_input.setText(self.printer.ip_address)
        
        if self.printer.api_key:
            self.api_key_input.setText(self.printer.api_key)
        
        # Set power consumption if available
        if hasattr(self.printer, 'power_consumption') and self.printer.power_consumption is not None:
            self.consumption_input.setValue(self.printer.power_consumption)
        
        if self.printer.notes:
            self.notes_input.setText(self.printer.notes)
    
    def save_printer(self):
        """
        Save the printer data.
        """
        # Validate required fields
        name = self.name_input.text().strip()
        model = self.model_input.text().strip()
        manufacturer = self.manufacturer_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return
        
        if not model:
            QMessageBox.warning(self, "Validation Error", "Model is required.")
            return
        
        if not manufacturer:
            QMessageBox.warning(self, "Validation Error", "Manufacturer is required.")
            return
        
        try:
            db = SessionLocal()
            
            if self.is_edit_mode:
                # Update existing printer
                printer = db.query(Printer).filter(Printer.id == self.printer.id).first()
                if not printer:
                    QMessageBox.warning(self, "Error", "Printer not found.")
                    return
            else:
                # Create new printer
                printer = Printer()
                printer.created_at = datetime.datetime.utcnow()
                db.add(printer)
            
            # Update printer data
            printer.name = name
            printer.model = model
            printer.manufacturer = manufacturer
            printer.build_volume_x = self.volume_x_input.value()
            printer.build_volume_y = self.volume_y_input.value()
            printer.build_volume_z = self.volume_z_input.value()
            printer.status = self.status_combo.currentData()
            printer.ip_address = self.ip_input.text().strip() or None
            printer.api_key = self.api_key_input.text().strip() or None
            printer.power_consumption = self.consumption_input.value()
            printer.notes = self.notes_input.text().strip() or None
            printer.updated_at = datetime.datetime.utcnow()
            
            db.commit()
            
            logging.info(f"Printer {printer.name} {'updated' if self.is_edit_mode else 'created'}")
            
            self.accept()
        except Exception as e:
            logging.error(f"Error saving printer: {str(e)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
        finally:
            db.close()


class PrintersView(QWidget):
    """
    Printers view for the application.
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
        
        header_title = QLabel("Printers")
        header_title.setStyleSheet("color: #F8FAFC; font-size: 20px; font-weight: bold;")
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search printers...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_printers)
        
        search_layout.addWidget(self.search_input)
        
        # Add printer button
        self.add_btn = QPushButton("Add Printer")
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
        self.add_btn.clicked.connect(self.add_printer)
        
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addLayout(search_layout)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(header_layout)
        
        # Printers table
        self.printers_table = QTableWidget()
        self.printers_table.setColumnCount(6)
        self.printers_table.setHorizontalHeaderLabels([
            "Name", "Build Volume", "Status", "IP Address", "Operating Hours", "Actions"
        ])
        # Set row height to make icons fully visible
        self.printers_table.verticalHeader().setDefaultSectionSize(40)
        self.printers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.printers_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.printers_table.verticalHeader().setVisible(False)
        self.printers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.printers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.printers_table.setAlternatingRowColors(True)
        self.printers_table.setStyleSheet("""
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
        
        main_layout.addWidget(self.printers_table)
        
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
        jobs_title = QLabel("Active Print Jobs")
        jobs_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: bold;")
        
        jobs_header.addWidget(jobs_title)
        jobs_header.addStretch()
        
        jobs_layout.addLayout(jobs_header)
        
        # Jobs table
        self.jobs_table = QTableWidget()
        self.jobs_table.setColumnCount(6)
        self.jobs_table.setHorizontalHeaderLabels([
            "Job Name", "Printer", "Started", "Progress", "Est. Completion", "Actions"
        ])
        # Set row height to make icons fully visible
        self.jobs_table.verticalHeader().setDefaultSectionSize(40)
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
        
        main_layout.addWidget(jobs_frame)
    
    def get_printer_operating_hours(self, printer_id):
        """
        Calculate the total operating hours for a printer.
        
        Args:
            printer_id: The ID of the printer.
            
        Returns:
            float: The total operating hours.
        """
        try:
            # Get the sum of actual_print_time for completed print jobs
            total_minutes = self.db.query(func.sum(PrintJob.actual_print_time)).filter(
                PrintJob.printer_id == printer_id,
                PrintJob.status == PrintJobStatus.COMPLETED
            ).scalar() or 0
            
            # Convert minutes to hours
            return round(total_minutes / 60, 1)
        except Exception as e:
            logging.error(f"Error calculating printer operating hours: {str(e)}")
            return 0
    
    def refresh_data(self):
        """
        Refresh the printers data.
        """
        try:
            # Get all printers
            printers = self.db.query(Printer).all()
            
            # Populate printers table
            self.printers_table.setRowCount(len(printers))
            for i, printer in enumerate(printers):
                # Name
                name_item = QTableWidgetItem(printer.name)
                self.printers_table.setItem(i, 0, name_item)
                
                # Build volume
                volume_item = QTableWidgetItem(printer.build_volume)
                self.printers_table.setItem(i, 1, volume_item)
                
                # Status
                status_item = QTableWidgetItem(printer.status.value.capitalize())
                self.printers_table.setItem(i, 2, status_item)
                
                # IP address
                ip_item = QTableWidgetItem(printer.ip_address or "")
                self.printers_table.setItem(i, 3, ip_item)
                
                # Operating hours
                operating_hours = self.get_printer_operating_hours(printer.id)
                hours_item = QTableWidgetItem(f"{operating_hours} h")
                self.printers_table.setItem(i, 4, hours_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 0, 5, 0)
                actions_layout.setSpacing(5)
                
                # Edit button
                edit_btn = QPushButton()
                edit_btn.setIcon(QIcon("src/resources/icons/edit.png"))
                edit_btn.setIconSize(QSize(16, 16))
                edit_btn.setFixedSize(30, 30)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                edit_btn.setToolTip("Edit Printer")
                edit_btn.clicked.connect(lambda _=False, p=printer: self.edit_printer(p))
                
                # Delete button
                delete_btn = QPushButton()
                delete_btn.setIcon(QIcon("src/resources/icons/delete.png"))
                delete_btn.setIconSize(QSize(16, 16))
                delete_btn.setFixedSize(30, 30)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                delete_btn.setToolTip("Delete Printer")
                delete_btn.clicked.connect(lambda _=False, p=printer: self.delete_printer(p))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                self.printers_table.setCellWidget(i, 5, actions_widget)
            
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
                printer_name = printer.name if printer else "Unknown"
                printer_item = QTableWidgetItem(printer_name)
                self.jobs_table.setItem(i, 1, printer_item)
                
                # Started
                started_item = QTableWidgetItem(job.started_at.strftime("%d %b %Y %H:%M"))
                self.jobs_table.setItem(i, 2, started_item)
                
                # Progress
                progress_widget = ProgressBarWidget(job.progress)
                self.jobs_table.setCellWidget(i, 3, progress_widget)
                
                # Estimated completion
                est_completion = job.estimated_completion_time
                est_completion_text = est_completion.strftime("%d %b %Y %H:%M") if est_completion else "Unknown"
                est_completion_item = QTableWidgetItem(est_completion_text)
                self.jobs_table.setItem(i, 4, est_completion_item)
                
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
                view_btn.setToolTip("View Job")
                # Connecter le bouton à une fonction qui sera implémentée plus tard
                view_btn.clicked.connect(lambda _=False, j=job: self.view_job(j))
                
                # Pause/Resume button
                pause_btn = QPushButton()
                pause_btn.setIcon(QIcon("src/resources/icons/pause.png"))
                pause_btn.setIconSize(QSize(16, 16))
                pause_btn.setFixedSize(30, 30)
                pause_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                pause_btn.setToolTip("Pause Job")
                # Connecter le bouton à une fonction qui sera implémentée plus tard
                pause_btn.clicked.connect(lambda _=False, j=job: self.pause_job(j))
                
                # Cancel button
                cancel_btn = QPushButton()
                cancel_btn.setIcon(QIcon("src/resources/icons/delete.png"))
                cancel_btn.setIconSize(QSize(16, 16))
                cancel_btn.setFixedSize(30, 30)
                cancel_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #334155;
                        border-radius: 15px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                    }
                """)
                cancel_btn.setToolTip("Cancel Job")
                # Connecter le bouton à une fonction qui sera implémentée plus tard
                cancel_btn.clicked.connect(lambda _=False, j=job: self.cancel_job(j))
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(pause_btn)
                actions_layout.addWidget(cancel_btn)
                actions_layout.addStretch()
                
                self.jobs_table.setCellWidget(i, 5, actions_widget)
            
            logging.info("Printers view refreshed")
        except Exception as e:
            logging.error(f"Error refreshing printers data: {str(e)}")
    
    def filter_printers(self):
        """
        Filter printers based on search text.
        """
        search_text = self.search_input.text().lower()
        
        for i in range(self.printers_table.rowCount()):
            row_hidden = True
            
            # Check if search text is in any of the first 5 columns
            for j in range(5):
                item = self.printers_table.item(i, j)
                if item and search_text in item.text().lower():
                    row_hidden = False
                    break
            
            self.printers_table.setRowHidden(i, row_hidden)
    
    def add_printer(self):
        """
        Open the add printer dialog.
        """
        dialog = PrinterDetailsDialog(parent=self)
        if dialog.exec():
            # Refresh the view to show the new printer
            self.refresh_data()
    
    def edit_printer(self, printer):
        """
        Open the edit printer dialog.
        """
        dialog = PrinterDetailsDialog(printer, self)
        if dialog.exec():
            # Refresh the view to show the updated printer
            self.refresh_data()
    
    def delete_printer(self, printer):
        """
        Delete a printer.
        """
        # Check if printer has active print jobs
        active_jobs = self.db.query(PrintJob).filter(
            PrintJob.printer_id == printer.id,
            PrintJob.status.in_([PrintJobStatus.PRINTING, PrintJobStatus.PAUSED])
        ).count()
        
        if active_jobs > 0:
            QMessageBox.warning(
                self, "Cannot Delete", 
                f"Cannot delete printer '{printer.name}' because it has active print jobs."
            )
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            f"Are you sure you want to delete printer '{printer.name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete printer
                self.db.query(Printer).filter(Printer.id == printer.id).delete()
                self.db.commit()
                
                logging.info(f"Printer {printer.name} deleted")
                
                # Refresh the view
                self.refresh_data()
            except Exception as e:
                logging.error(f"Error deleting printer: {str(e)}")
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
    
    def view_job(self, job):
        """
        View details of a print job.
        
        Args:
            job: The print job to view.
        """
        # Cette méthode sera implémentée plus tard
        QMessageBox.information(self, "Information", f"Affichage des détails du travail: {job.job_name}")
    
    def pause_job(self, job):
        """
        Pause a print job.
        
        Args:
            job: The print job to pause.
        """
        # Cette méthode sera implémentée plus tard
        QMessageBox.information(self, "Information", f"Pause du travail: {job.job_name}")
    
    def cancel_job(self, job):
        """
        Cancel a print job.
        
        Args:
            job: The print job to cancel.
        """
        # Cette méthode sera implémentée plus tard
        QMessageBox.information(self, "Information", f"Annulation du travail: {job.job_name}")
