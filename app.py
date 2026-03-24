import streamlit as st
from datetime import datetime
import re

from models import FoodItem, OrderItem, ShoppingCart, Store
from database import create_tables, seed_menu_if_empty
from repository import OrderRepository, MenuRepository

st.set_page_config(
    page_title="Norma's Kitchenette",
    page_icon="🍽️",
    layout="centered"
)

create_tables()
seed_menu_if_empty()

order_repo = OrderRepository()
menu_repo = MenuRepository()


# ---------------------------
# Helper Functions
# ---------------------------
def format_phone(phone):
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone


def render_receipt(items, total):
    rows = ""
    for item in items:
        rows += (
            f'<div class="receipt-row">'
            f'<span class="receipt-left">{item.receipt_text()}</span>'
            f'<span class="receipt-right">${item.subtotal():.2f}</span>'
            f'</div>'
        )

    html = (
        "<style>"
        ".receipt{font-family:monospace;font-size:16px;line-height:1.4;}"
        ".receipt-row{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:4px 0;}"
        ".receipt-left{flex:1;text-align:left;word-break:break-word;}"
        ".receipt-right{min-width:90px;text-align:right;white-space:nowrap;}"
        ".receipt-divider{border-top:1px dashed #888;margin:8px 0;}"
        "</style>"
        '<div class="receipt">'
        '<div class="receipt-divider"></div>'
        f"{rows}"
        '<div class="receipt-divider"></div>'
        '<div class="receipt-row">'
        '<span class="receipt-left"><strong>TOTAL</strong></span>'
        f'<span class="receipt-right"><strong>${total:.2f}</strong></span>'
        '</div>'
        '<div class="receipt-divider"></div>'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


def load_store_from_database():
    store = Store("Norma's Kitchenette")
    menu_rows = menu_repo.get_all_menu_items()

    for _, name, category, price, stock in menu_rows:
        store.add_food(FoodItem(name, category, price, stock))

    return store


# ---------------------------
# Session State
# ---------------------------
if "cart" not in st.session_state:
    st.session_state.cart = ShoppingCart()

if "order_number" not in st.session_state:
    st.session_state.order_number = 1001

if "order_time" not in st.session_state:
    st.session_state.order_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

if "form_version" not in st.session_state:
    st.session_state.form_version = 0

if "success_message" not in st.session_state:
    st.session_state.success_message = ""

if "last_order" not in st.session_state:
    st.session_state.last_order = None


# ---------------------------
# Load Menu
# ---------------------------
store = load_store_from_database()
all_foods = store.get_menu()
available_foods = [food for food in all_foods if food.stock > 0]


# ---------------------------
# Header
# ---------------------------
st.title("🍽️ Norma's Kitchenette")
st.caption("Food ordering app with stock management")
st.write("Choose from the ready-to-serve menu below.")


# ---------------------------
# Customer Inputs
# ---------------------------
name_key = f"customer_name_{st.session_state.form_version}"
phone_key = f"customer_phone_{st.session_state.form_version}"

customer_name = st.text_input(
    "Customer Name",
    key=name_key,
    placeholder="Enter your name"
)

phone_input = st.text_input(
    "Phone Number",
    key=phone_key,
    placeholder="1234567890"
)

st.session_state.cart.customer_name = customer_name
st.session_state.cart.phone_number = phone_input


# ---------------------------
# Show Menu
# ---------------------------
with st.expander("View Menu", expanded=False):
    if all_foods:
        for food in all_foods:
            if food.stock > 2:
                st.markdown(
                    f"**{food.name}** ({food.category}) - "
                    f"**${food.price:.2f}** | Available: {food.stock}"
                )
            elif food.stock > 0:
                st.markdown(
                    f"⚠️ **{food.name}** ({food.category}) - "
                    f"**${food.price:.2f}** | Only {food.stock} left!"
                )
            else:
                st.markdown(
                    f"❌ **{food.name}** ({food.category}) - SOLD OUT"
                )
    else:
        st.write("No menu items available.")


# ---------------------------
# Order Form
# ---------------------------
if available_foods:
    food_names = [food.name for food in available_foods]
    selected_food_name = st.selectbox("Select Food", food_names)

    selected_food = next(
        (food for food in available_foods if food.name == selected_food_name),
        None
    )

    max_stock = int(selected_food.stock) if selected_food else 1

    quantity = st.number_input(
        "Quantity",
        min_value=1,
        max_value=max_stock,
        value=1,
        step=1
    )

    st.caption(f"Available stock: {max_stock}")

    if st.button("Add to Cart", use_container_width=True):
        if selected_food:
            st.session_state.cart.add_item(OrderItem(selected_food, quantity))
            st.success(f"Added {selected_food.name} x{quantity} to cart.")
else:
    st.error("All items are SOLD OUT ❌")


# ---------------------------
# Receipt
# ---------------------------
st.divider()
st.subheader("Order Receipt")

if st.session_state.last_order:
    order = st.session_state.last_order
    st.write(f"**Order Number:** #{order['order_number']}")
    st.write(f"**Time:** {order['order_time']}")
    st.write(f"**Customer:** {order['customer']}")
    st.write(f"**Phone:** {order['phone']}")
    st.write("**Items Ordered:**")
    render_receipt(order["items"], order["total"])
else:
    st.write(f"**Order Number:** #{st.session_state.order_number}")
    st.write(f"**Time:** {st.session_state.order_time}")

    if customer_name.strip():
        st.write(f"**Customer:** {customer_name}")
    else:
        st.write("**Customer:** Not entered")

    if phone_input.strip():
        st.write(f"**Phone:** {format_phone(phone_input)}")
    else:
        st.write("**Phone:** Not entered")

    if st.session_state.cart.items:
        st.write("**Items Ordered:**")
        render_receipt(st.session_state.cart.items, st.session_state.cart.total())
    else:
        st.write("No items in cart yet.")


# ---------------------------
# Submit Order
# ---------------------------
if st.button("Submit Order", use_container_width=True):
    phone_digits = re.sub(r"\D", "", phone_input)

    if customer_name.strip() and len(phone_digits) == 10 and st.session_state.cart.items:
        stock_ok = True

        for item in st.session_state.cart.items:
            success = menu_repo.reduce_stock(item.food_item.name, item.quantity)
            if not success:
                stock_ok = False
                break

        if stock_ok:
            submitted_name = customer_name.strip()
            total_amount = st.session_state.cart.total()

            order_repo.save_order(
                order_number=st.session_state.order_number,
                customer_name=submitted_name,
                phone=format_phone(phone_input),
                order_time=st.session_state.order_time,
                cart_items=st.session_state.cart.items,
                total=total_amount
            )

            st.session_state.last_order = {
                "order_number": st.session_state.order_number,
                "order_time": st.session_state.order_time,
                "customer": submitted_name,
                "phone": format_phone(phone_input),
                "items": st.session_state.cart.items.copy(),
                "total": total_amount
            }

            st.session_state.success_message = (
                f"Order #{st.session_state.order_number} for {submitted_name} has been submitted successfully."
            )

            st.session_state.order_number += 1
            st.session_state.order_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            st.session_state.cart = ShoppingCart()
            st.session_state.form_version += 1
            st.rerun()
        else:
            st.error("One or more items no longer have enough stock available.")
    else:
        st.warning("Please enter name, valid 10-digit phone number, and add at least one item.")


# ---------------------------
# Clear Order
# ---------------------------
if st.button("Clear Order", use_container_width=True):
    st.session_state.cart = ShoppingCart()
    st.session_state.last_order = None
    st.session_state.form_version += 1
    st.session_state.order_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    st.rerun()


# ---------------------------
# Saved Orders
# ---------------------------
st.divider()
st.subheader("Saved Orders")

orders = order_repo.get_all_orders()

if orders:
    for order in orders:
        order_id, order_number, name, phone, order_time, total = order
        with st.expander(f"Order #{order_number} - {name} - ${total:.2f}"):
            st.write(f"**Phone:** {phone}")
            st.write(f"**Time:** {order_time}")
            st.write(f"**Total:** ${total:.2f}")

            items = order_repo.get_order_items(order_id)
            for item_name, qty, price, subtotal in items:
                st.write(f"- {item_name} x{qty} = ${subtotal:.2f}")
else:
    st.write("No saved orders yet.")


# ---------------------------
# Success Message
# ---------------------------
if st.session_state.success_message:
    st.success(st.session_state.success_message)
    st.session_state.success_message = ""