import streamlit as st


from database import create_tables, seed_menu_if_empty
from repository import MenuRepository, OrderRepository


st.set_page_config(
    page_title="Norma Admin Panel",
    page_icon="⚙️",
    layout="centered"
)


create_tables()
seed_menu_if_empty()


menu_repo = MenuRepository()
order_repo = OrderRepository()


ADMIN_PASSWORD = "norma123"


if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


if not st.session_state.admin_logged_in:
    st.title("🔐 Norma's Kitchenette Admin Login")
    password = st.text_input("Enter Admin Password", type="password")


    if st.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()


st.title("⚙️ Norma's Kitchenette Admin Panel")
st.caption("Manage ready-to-serve menu and available stock")


st.subheader("Current Menu Inventory")


current_menu = menu_repo.get_all_menu_items()


if current_menu:
    for item_id, name, category, price, stock in current_menu:
        with st.expander(f"{name} | {category} | ${price:.2f} | Stock: {stock}"):
            edit_name = st.text_input("Item Name", value=name, key=f"menu_name_{item_id}")
            edit_category = st.text_input("Category", value=category, key=f"menu_category_{item_id}")
            edit_price = st.number_input(
                "Price",
                min_value=0.0,
                value=float(price),
                step=0.50,
                key=f"menu_price_{item_id}"
            )
            edit_stock = st.number_input(
                "Available Stock",
                min_value=0,
                value=int(stock),
                step=1,
                key=f"menu_stock_{item_id}"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Update Item", key=f"update_{item_id}", use_container_width=True):
                    if edit_name.strip() and edit_category.strip():
                        menu_repo.update_menu_item(
                            item_id=item_id,
                            name=edit_name.strip(),
                            category=edit_category.strip(),
                            price=edit_price,
                            stock=edit_stock
                        )
                        st.success(f"{edit_name} updated successfully.")
                        st.rerun()
                    else:
                        st.warning("Name and category cannot be empty.")

            with col2:
                if st.button("Delete Item", key=f"delete_{item_id}", use_container_width=True):
                    menu_repo.delete_menu_item(item_id)
                    st.success(f"{name} deleted successfully.")
                    st.rerun()

            st.write("### Restock Item")
            restock_amount = st.number_input(
                "Enter restock quantity",
                min_value=1,
                value=1,
                step=1,
                key=f"restock_amount_{item_id}"
            )

            if st.button("Restock", key=f"restock_{item_id}", use_container_width=True):
                menu_repo.restock_menu_item(item_id, restock_amount)
                st.success(f"{name} restocked by {restock_amount}.")
                st.rerun()
else:
    st.info("No menu items found.")


st.divider()
st.subheader("Add New Menu Item")


new_name = st.text_input("New Item Name", key="menu_new_name")
new_category = st.text_input("New Category", key="menu_new_category")
new_price = st.number_input("New Price", min_value=0.0, value=0.0, step=0.50, key="menu_new_price")
new_stock = st.number_input("New Stock", min_value=0, value=0, step=1, key="menu_new_stock")


if st.button("Add New Menu Item", use_container_width=True):
    if new_name.strip() and new_category.strip():
        menu_repo.add_menu_item(new_name.strip(), new_category.strip(), new_price, new_stock)
        st.success(f"{new_name} added.")
        st.rerun()
    else:
        st.warning("Please enter valid item details.")
