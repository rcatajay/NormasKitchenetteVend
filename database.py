import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / "normas_kitchenette.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            order_time TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def seed_menu_if_empty():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM menu_items")
    count = cursor.fetchone()[0]

    if count == 0:
        default_items = [
            ("Chicken Adobo Combo", "Lunch Combo", 12.99, 5),
            ("Pork BBQ Combo", "Lunch Combo", 13.99, 4),
            ("Sinigang Combo", "Lunch Combo", 14.50, 3),
            ("Beef Tapa Combo", "Lunch Combo", 13.50, 4),
            ("Crispy Pork Belly Combo", "Lunch Combo", 15.99, 2),
            ("Pancit Canton", "Noodles", 9.99, 6),
            ("Lumpia (6 pcs)", "Side Dish", 5.99, 8),
            ("Extra Rice", "Add-on", 2.00, 15),
            ("Halo-Halo", "Dessert", 6.50, 5),
            ("Leche Flan", "Dessert", 4.99, 5),
            ("Soft Drinks", "Drink", 2.00, 20),
            ("Bottled Water", "Drink", 1.50, 20)
        ]

        cursor.executemany("""
            INSERT INTO menu_items (name, category, price, stock)
            VALUES (?, ?, ?, ?)
        """, default_items)

    conn.commit()
    conn.close()