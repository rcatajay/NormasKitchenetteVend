class FoodItem:
    def __init__(self, name, category, price, stock=0):
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock


    def get_info(self):
        return f"{self.name} ({self.category}) - ${self.price:.2f} | Available: {self.stock}"




class OrderItem:
    def __init__(self, food_item, quantity):
        self.food_item = food_item
        self.quantity = quantity


    def subtotal(self):
        return self.food_item.price * self.quantity


    def receipt_text(self):
        return f"{self.food_item.name} x{self.quantity}"




class ShoppingCart:
    def __init__(self, customer_name="", phone_number=""):
        self.customer_name = customer_name
        self.phone_number = phone_number
        self.items = []


    def add_item(self, order_item):
        self.items.append(order_item)


    def total(self):
        return sum(item.subtotal() for item in self.items)


    def item_count(self):
        return sum(item.quantity for item in self.items)


    def clear_items(self):
        self.items = []




class Store:
    def __init__(self, name):
        self.name = name
        self.menu = []


    def add_food(self, food_item):
        self.menu.append(food_item)


    def get_menu(self):
        return self.menu


    def find_food(self, food_name):
        for item in self.menu:
            if item.name == food_name:
                return item
        return None
    