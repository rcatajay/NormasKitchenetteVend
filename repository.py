from database import get_connection




class OrderRepository:
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
            """, (
                order_id,
                item.food_item.name,
                item.quantity,
                item.food_item.price,
                item.subtotal()
            ))


        conn.commit()
        conn.close()


    def get_all_orders(self):
        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute("""
            SELECT id, order_number, customer_name, phone, order_time, total
            FROM orders
            ORDER BY id DESC
        """)


        orders = cursor.fetchall()
        conn.close()
        return orders


    def get_order_items(self, order_id):
        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute("""
            SELECT item_name, quantity, price, subtotal
            FROM order_items
            WHERE order_id = ?
        """, (order_id,))


        items = cursor.fetchall()
        conn.close()
        return items


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


        cursor.execute("""
            SELECT id, name, category, price, stock
            FROM menu_items
            ORDER BY category, name
        """)


        items = cursor.fetchall()
        conn.close()
        return items


    def get_available_menu_items(self):
        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute("""
            SELECT id, name, category, price, stock
            FROM menu_items
            WHERE stock > 0
            ORDER BY category, name
        """)


        items = cursor.fetchall()
        conn.close()
        return items


    def add_menu_item(self, name, category, price, stock):
        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute("""
            INSERT INTO menu_items (name, category, price, stock)
            VALUES (?, ?, ?, ?)
        """, (name, category, price, stock))


        conn.commit()
        conn.close()


    def update_menu_item(self, item_id, name, category, price, stock):
        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute("""
            UPDATE menu_items
            SET name = ?, category = ?, price = ?, stock = ?
            WHERE id = ?
        """, (name, category, price, stock, item_id))


        conn.commit()
        conn.close()


    def delete_menu_item(self, item_id):
        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute("""
            DELETE FROM menu_items
            WHERE id = ?
        """, (item_id,))


        conn.commit()
        conn.close()


    def reduce_stock(self, item_name, quantity):
        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute("""
            UPDATE menu_items
            SET stock = stock - ?
            WHERE name = ? AND stock >= ?
        """, (quantity, item_name, quantity))


        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
   
