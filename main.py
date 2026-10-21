
from decimal import Decimal, InvalidOperation

import database as db


def read_int(prompt, minimum=0):
    while True:
        try:
            value = int(input(prompt).strip())
            if value < minimum:
                print(f"Enter a number >= {minimum}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number.")


def read_money(prompt):
    while True:
        try:
            value = Decimal(input(prompt).strip())
            if not value.is_finite() or value < 0:
                raise ValueError
            return value
        except (InvalidOperation, ValueError):
            print("Enter a valid non-negative amount, e.g. 199.50.")


def show_products():
    products = db.list_products()

    if not products:
        print("\nNo products found.")
        return

    print("\n" + "-" * 94)
    print(f"{'ID':<5}{'Product':<25}{'Quantity':>10}"
          f"{'Cost':>14}{'Selling':>14}{'Stock Alert':>16}")
    print("-" * 94)

    for p in products:
        alert = "LOW STOCK" if p["quantity"] <= p["low_stock_level"] else "OK"
        print(
            f"{p['id']:<5}{p['name'][:24]:<25}"
            f"{p['quantity']:>10}"
            f"{Decimal(p['cost_price']):>14.2f}"
            f"{Decimal(p['selling_price']):>14.2f}"
            f"{alert:>16}"
        )

    print("-" * 94)


def create_product():
    print("\n--- Add New Product ---")
    name = input("Product name: ")
    quantity = read_int("Opening stock quantity: ")
    cost = read_money("Cost price per item (INR): ")
    selling = read_money("Selling price per item (INR): ")
    low_stock = read_int("Low-stock alert level [5]: ")

    product_id = db.add_product(
        name, quantity, cost, selling, low_stock
    )
    print(f"Product added successfully. ID: {product_id}")


def update_stock():
    show_products()
    product_id = read_int("Product ID: ", minimum=1)

    print("1. Purchase / add stock")
    print("2. Sale / remove stock")
    choice = input("Choose operation: ").strip()

    if choice not in ("1", "2"):
        print("Invalid operation.")
        return

    quantity = read_int("Quantity: ", minimum=1)
    movement = "PURCHASE" if choice == "1" else "SALE"

    db.change_stock(product_id, movement, quantity)
    print(f"{movement.title()} recorded successfully.")


def record_expense():
    print("\n--- Record Expense ---")
    category = input("Category (Rent, Electricity, Travel, etc.): ")
    description = input("Description: ")
    amount = read_money("Amount (INR): ")

    expense_id = db.add_expense(category, description, amount)
    print(f"Expense recorded successfully. ID: {expense_id}")


def show_expenses():
    expenses = db.list_expenses()

    if not expenses:
        print("\nNo expenses recorded.")
        return

    total = Decimal("0.00")
    print("\n--- Expense History ---")

    for expense in expenses:
        amount = Decimal(expense["amount"])
        total += amount
        print(
            f"#{expense['id']} | {expense['expense_date']} | "
            f"{expense['category']} | {expense['description']} | "
            f"INR {amount:.2f}"
        )

    print(f"\nTotal expenses: INR {total:.2f}")


def show_low_stock():
    products = db.low_stock_products()

    print("\n--- Low Stock Report ---")
    if not products:
        print("All products are above their alert levels.")
        return

    for p in products:
        print(
            f"ID: {p['id']} | {p['name']} | "
            f"Available: {p['quantity']} | "
            f"Alert level: {p['low_stock_level']}"
        )


def show_report():
    report = db.get_report()

    print("\n========== BUSINESS REPORT ==========")
    print(f"Number of products : {report['products']}")
    print(f"Inventory value   : INR {report['inventory_value']:.2f}")
    print(f"Total expenses    : INR {report['total_expenses']:.2f}")
    print(f"Recorded sales    : INR {report['sales']:.2f}")
    print(f"Recorded purchases: INR {report['purchases']:.2f}")
    print("=====================================")
    print("Note: Sales are revenue, not profit.")


def main():
    db.initialize_database()

    actions = {
        "1": create_product,
        "2": show_products,
        "3": update_stock,
        "4": record_expense,
        "5": show_expenses,
        "6": show_low_stock,
        "7": show_report,
    }

    while True:
        print("""
========================================
 INVENTORY & EXPENSE MANAGEMENT SYSTEM
========================================
1. Add product
2. View inventory
3. Record purchase or sale
4. Add expense
5. View expenses
6. Low-stock report
7. Business summary
0. Exit
========================================
""")

        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("Thank you for using the system!")
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Please select 0-7.")
            continue

        try:
            action()
        except (ValueError, TypeError) as error:
            print(f"Could not complete operation: {error}")
        except Exception as error:
            print(f"An unexpected error occurred: {error}")


if __name__ == "__main__":
    main()
