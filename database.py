
import sqlite3
from contextlib import contextmanager
from datetime import date
from decimal import Decimal

DB_NAME = "inventory.db"


@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    with get_connection() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                quantity INTEGER NOT NULL DEFAULT 0
                    CHECK (quantity >= 0),
                cost_price TEXT NOT NULL,
                selling_price TEXT NOT NULL,
                low_stock_level INTEGER NOT NULL DEFAULT 5
                    CHECK (low_stock_level >= 0)
            );

            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                movement_type TEXT NOT NULL
                    CHECK (movement_type IN ('PURCHASE', 'SALE')),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price TEXT NOT NULL,
                movement_date TEXT NOT NULL,
                FOREIGN KEY (product_id)
                    REFERENCES products(id)
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount TEXT NOT NULL,
                expense_date TEXT NOT NULL
            );
        """)


def money(value):
    """Validate and convert an amount to two decimal places."""
    amount = Decimal(str(value))

    if not amount.is_finite() or amount < 0:
        raise ValueError("Amount must be finite and non-negative.")

    return amount.quantize(Decimal("0.01"))


def add_product(
    name, quantity, cost_price, selling_price, low_stock=5
):
    name = name.strip()
    quantity = int(quantity)
    low_stock = int(low_stock)

    cost = money(cost_price)
    selling = money(selling_price)

    if not name:
        raise ValueError("Product name cannot be empty.")

    if quantity < 0 or low_stock < 0:
        raise ValueError("Quantity and low-stock level cannot be negative.")

    with get_connection() as db:
        cursor = db.execute("""
            INSERT INTO products
                (name, quantity, cost_price, selling_price, low_stock_level)
            VALUES (?, ?, ?, ?, ?)
        """, (name, quantity, str(cost), str(selling), low_stock))

        product_id = cursor.lastrowid

        if quantity > 0:
            db.execute("""
                INSERT INTO stock_movements
                    (product_id, movement_type, quantity,
                     unit_price, movement_date)
                VALUES (?, 'PURCHASE', ?, ?, ?)
            """, (
                product_id,
                quantity,
                str(cost),
                date.today().isoformat()
            ))

        return product_id


def list_products():
    with get_connection() as db:
        return db.execute("""
            SELECT * FROM products ORDER BY name
        """).fetchall()


def find_product(product_id):
    with get_connection() as db:
        return db.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()


def change_stock(product_id, movement_type, quantity):
    movement_type = movement_type.upper()
    quantity = int(quantity)

    if movement_type not in ("PURCHASE", "SALE"):
        raise ValueError("Movement must be PURCHASE or SALE.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    with get_connection() as db:
        product = db.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        if product is None:
            raise ValueError("Product not found.")

        if movement_type == "PURCHASE":
            new_quantity = product["quantity"] + quantity
            unit_price = money(product["cost_price"])
        else:
            if quantity > product["quantity"]:
                raise ValueError("Insufficient stock.")

            new_quantity = product["quantity"] - quantity
            unit_price = money(product["selling_price"])

        db.execute("""
            UPDATE products
            SET quantity = ?
            WHERE id = ?
        """, (new_quantity, product_id))

        db.execute("""
            INSERT INTO stock_movements
                (product_id, movement_type, quantity,
                 unit_price, movement_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            product_id,
            movement_type,
            quantity,
            str(unit_price),
            date.today().isoformat()
        ))


def add_expense(category, description, amount):
    category = category.strip()
    description = description.strip()
    value = money(amount)

    if not category or not description:
        raise ValueError("Category and description are required.")

    if value <= 0:
        raise ValueError("Expense must be greater than zero.")

    with get_connection() as db:
        cursor = db.execute("""
            INSERT INTO expenses
                (category, description, amount, expense_date)
            VALUES (?, ?, ?, ?)
        """, (
            category,
            description,
            str(value),
            date.today().isoformat()
        ))

        return cursor.lastrowid


def list_expenses():
    with get_connection() as db:
        return db.execute("""
            SELECT * FROM expenses
            ORDER BY expense_date DESC, id DESC
        """).fetchall()


def low_stock_products():
    with get_connection() as db:
        return db.execute("""
            SELECT * FROM products
            WHERE quantity <= low_stock_level
            ORDER BY quantity, name
        """).fetchall()


def get_report():
    with get_connection() as db:
        products = db.execute("""
            SELECT quantity, cost_price FROM products
        """).fetchall()

        expenses = db.execute("""
            SELECT amount FROM expenses
        """).fetchall()

        movements = db.execute("""
            SELECT movement_type, quantity, unit_price
            FROM stock_movements
        """).fetchall()

    inventory_value = sum(
        (
            int(p["quantity"]) * money(p["cost_price"])
            for p in products
        ),
        Decimal("0.00")
    )

    total_expenses = sum(
        (money(e["amount"]) for e in expenses),
        Decimal("0.00")
    )

    sales = sum(
        (
            int(m["quantity"]) * money(m["unit_price"])
            for m in movements
            if m["movement_type"] == "SALE"
        ),
        Decimal("0.00")
    )

    purchases = sum(
        (
            int(m["quantity"]) * money(m["unit_price"])
            for m in movements
            if m["movement_type"] == "PURCHASE"
        ),
        Decimal("0.00")
    )

    return {
        "products": len(products),
        "inventory_value": inventory_value,
        "total_expenses": total_expenses,
        "sales": sales,
        "purchases": purchases,
    }
