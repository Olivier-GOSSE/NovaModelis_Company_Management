# NovaModelis - 3D Printing Business Management System

NovaModelis is a comprehensive desktop application designed to help 3D printing businesses manage their operations efficiently. The application provides tools for managing printers, customers, orders, and print jobs.

## Features

- **Dashboard**: Get an overview of your business with key metrics and recent activities
- **Printer Management**: Track and manage your 3D printers, including status and specifications
- **Customer Management**: Maintain a database of customers with contact information and order history
- **Order Management**: Create and track orders from receipt to delivery
- **Print Job Tracking**: Monitor print jobs, track progress, and manage the printing queue
- **Customer Communication**: Keep track of customer emails and communications

## Technology Stack

- **Python**: Core programming language
- **PySide6 (Qt)**: GUI framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Database engine

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/novamodelisapp.git
   cd novamodelisapp
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run the application:
   ```
   python src/main.py
   ```

## Project Structure

```
novamodelisapp/
├── config.py                  # Application configuration
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── data/                      # Data directory
│   ├── db/                    # Database files
│   └── logs/                  # Log files
└── src/                       # Source code
    ├── database/              # Database modules
    │   ├── base.py            # Database connection and base setup
    │   └── init_db.py         # Database initialization
    ├── models/                # Database models
    │   ├── __init__.py        # Models package initialization
    │   ├── user.py            # User model
    │   ├── printer.py         # Printer model
    │   ├── customer.py        # Customer model
    │   ├── sales_channel.py   # Sales channel model
    │   ├── order.py           # Order models
    │   ├── print_job.py       # Print job model
    │   └── customer_email.py  # Customer email model
    ├── resources/             # Application resources
    │   └── icons/             # Application icons
    ├── utils/                 # Utility modules
    │   └── logger.py          # Logging utility
    ├── views/                 # UI views
    │   ├── login_window.py    # Login window
    │   ├── main_window.py     # Main application window
    │   ├── dashboard_view.py  # Dashboard view
    │   ├── printers_view.py   # Printers management view
    │   ├── customers_view.py  # Customers management view
    │   ├── orders_view.py     # Orders management view
    │   └── settings_view.py   # Settings view
    └── main.py                # Application entry point
```

## Default Login

- **Username**: admin
- **Password**: admin123

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request
