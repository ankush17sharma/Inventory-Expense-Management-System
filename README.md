
# Inventory & Expense Management System

A Python-based Inventory and Expense Management System that uses SQLite
to store product inventory, stock movements, and business expenses.

## Features

- Add and view products
- Track opening inventory quantities
- Record purchases and sales
- Automatically update stock after transactions
- Prevent sales when stock is insufficient
- Store expenses with category, description, date, and amount
- Generate low-stock alerts
- Calculate inventory valuation
- View total expenses, purchases, and recorded sales
- Persist data using an SQLite database
- Validate user input and use database transactions

## Tech Stack

- Python 3.10+
- SQLite
- sqlite3
- Decimal
- datetime

No third-party Python packages are required.

## Project Structure

    inventory-expense-manager/
    ├── main.py
    ├── database.py
    ├── README.md
    ├── .gitignore
    └── inventory.db  # Generated automatically

## Installation

### 1. Clone the repository

    git clone https://github.com/ankush17sharma/inventory-expense-manager.git

### 2. Open the project folder

    cd inventory-expense-manager

### 3. Check Python installation

    python --version

### 4. Run the application

    python main.py

On Windows, you can also use:

    py main.py

The application automatically initializes the SQLite database
when it starts for the first time.

## How to Use

1. Select **Add product** to create a product.
2. Select **View inventory** to see available stock.
3. Select **Record purchase or sale** to update inventory.
4. Select **Add expense** to record a business expense.
5. Select **View expenses** to review expense history.
6. Select **Low-stock report** to identify products requiring restocking.
7. Select **Business summary** to review inventory value and totals.
8. Select **Exit** to close the application.

## Database Tables

### products

Stores product names, quantities, cost prices, selling prices,
and low-stock alert levels.

### stock_movements

Records purchase and sale transactions with quantities, unit prices,
and transaction dates.

### expenses

Stores expense categories, descriptions, amounts, and dates.

## Important Notes

- Monetary values are stored as decimal strings and calculated with
  Python's Decimal type to reduce floating-point rounding errors.
- The inventory valuation uses current quantity multiplied by cost price.
- Recorded sales represent revenue, not net profit.
- The expense report currently includes manually entered expenses.
- Stock purchase costs and manually entered expenses are reported
  separately to avoid automatically treating both as the same expense.
- This is a learning project, not a production accounting system.

## Future Improvements

- GUI using Tkinter or a web dashboard using Flask
- User login and role-based access
- Search, filtering, and product editing
- Expense categories and monthly charts
- Export reports to CSV or Excel
- Supplier and customer management
- Automated backups
- Unit tests and improved audit logs

## License

This project is available under the MIT License.
Add a LICENSE file before distributing it under that license.

## Author

Your Name

GitHub: https://github.com/YOUR_USERNAME
