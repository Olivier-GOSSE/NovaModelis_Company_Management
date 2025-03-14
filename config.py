"""
Configuration file for the application.
"""
import os

# Application information
APP_NAME = "NovaModelis"
APP_VERSION = "1.0.0"

# Database configuration
DATABASE_URL = "sqlite:///data/db/novamodelisapp.db"
SQL_ECHO = False  # Set to True to log SQL queries

# Logging configuration
LOG_FILE = "data/logs/novamodelisapp.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Admin user configuration
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
ADMIN_EMAIL = "admin@novamodelisapp.com"

# Auto-refresh interval in seconds
AUTO_REFRESH_INTERVAL = 60

# Demo data
CREATE_DEMO_DATA = True
