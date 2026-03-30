from datetime import datetime # Make sure this is at the very top of repository.py
from database import get_connection

class AdminUserRepository:
    def authenticate(self, username, password):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM admin_users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        return user

    def get_all_users(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM admin_users")
        users = cursor.fetchall()
        conn.close()
        return users

    def add_user(self, username, password, role="staff"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO admin_users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    def delete_user(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admin_users WHERE id = ? AND role != 'primary_admin'", (user_id,))
        conn.commit()
        conn.close()


class OrderRepository:
    # 1. Save an order to the database
    def save_order(self, order_number, customer_name, phone, order_time, cart_items, total):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (order_number, customer_name, phone, order_time, total)
            VALUES (?, ?, ?, ?, ?)
        """, (order_number, customer_name, phone, order_time, total))
        order_id = cursor.lastrowid
        for item in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, item_name, quantity, price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, item.food_item.name, item.quantity, item.food_item.price, item.subtotal()))
        conn.commit()
        conn.close()

    # 2. THIS IS THE ONE YOU ARE MISSING
    def get_all_orders(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, order_number, customer_name, phone, order_time, total FROM orders ORDER BY id DESC")
        orders = cursor.fetchall()
        conn.close()
        return orders

    # 3. The Date Range function we added earlier
    def get_orders_by_date_range(self, start_date, end_date):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, order_number, customer_name, phone, order_time, total
            FROM orders
            WHERE date(order_time) BETWEEN ? AND ?
            ORDER BY id DESC
        """, (start_date, end_date))
        orders = cursor.fetchall()
        conn.close()
        return orders

    # 4. Get items for a specific order
    def get_order_items(self, order_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, quantity, price, subtotal FROM order_items WHERE order_id = ?", (order_id,))
        items = cursor.fetchall()
        conn.close()
        return items

    # 5. Delete an order
    def delete_order(self, order_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()

class MenuRepository:
    def get_all_menu_items(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, price, stock FROM menu_items ORDER BY category, name")
        items = cursor.fetchall()
        conn.close()
        return items

    def get_available_menu_items(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, price, stock FROM menu_items WHERE stock > 0 ORDER BY category, name")
        items = cursor.fetchall()
        conn.close()
        return items

    def get_menu_item_by_name(self, name):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, price, stock FROM menu_items WHERE name = ?", (name,))
        item = cursor.fetchone()
        conn.close()
        return item

    def add_menu_item(self, name, category, price, stock):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO menu_items (name, category, price, stock) VALUES (?, ?, ?, ?)", (name, category, price, stock))
        conn.commit()
        conn.close()

    def update_menu_item(self, item_id, name, category, price, stock):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE menu_items SET name=?, category=?, price=?, stock=? WHERE id=?", (name, category, price, stock, item_id))
        conn.commit()
        conn.close()

    def delete_menu_item(self, item_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

    def reduce_stock(self, item_name, quantity):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE menu_items SET stock = stock - ? WHERE name = ? AND stock >= ?", (quantity, item_name, quantity))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
   
