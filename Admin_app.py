    import streamlit as st
from database import create_tables, seed_menu_if_empty, seed_primary_admin_if_empty
from repository import MenuRepository, OrderRepository, AdminUserRepository

# 1. Page Configuration
st.set_page_config(page_title="Norma Admin Panel", page_icon="⚙️")

# 2. Initialize
create_tables()
seed_menu_if_empty()
seed_primary_admin_if_empty()

menu_repo = MenuRepository()
order_repo = OrderRepository()
admin_repo = AdminUserRepository()

# 3. Session State
if "admin_user" not in st.session_state:
    st.session_state.admin_user = None

def show_login():
    st.title("🔐 Norma's Kitchenette Admin Login")
    u = st.text_input("Username", key="login_u")
    p = st.text_input("Password", type="password", key="login_p")
    if st.button("Login", use_container_width=True):
        user = admin_repo.authenticate(u.strip(), p)
        if user:
            st.session_state.admin_user = {"id": user[0], "username": user[1], "role": user[2]}
            st.rerun()
        else:
            st.error("Invalid Username or Password")
    st.stop()

# 4. Safety Check
if st.session_state.admin_user is None:
    show_login()
else:
    current_user = st.session_state.admin_user
    role = current_user["role"].lower()

    st.title("⚙️ Norma's Kitchenette Admin Panel")
    st.caption(f"Logged in as: **{current_user['username']}** | Role: **{role}**")

    if st.button("Logout", use_container_width=True):
        st.session_state.admin_user = None
        st.rerun()

    st.divider()

    # --- SECTION 1: STAFF MANAGEMENT (Norma Only) ---
    if role in ['admin', 'primary_admin']:
        with st.expander("👤 Manage Authorized Staff"):
            st.subheader("Current Staff List")
            users = admin_repo.get_all_users()
            for uid, uname, urole in users:
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{uname}** ({urole.lower()})")
                if uname.lower() != 'norma':
                    if c2.button("Remove", key=f"user_del_{uid}"):
                        admin_repo.delete_user(uid)
                        st.rerun()
            
            st.divider()
            st.subheader("Add New Staff")
            new_u = st.text_input("New Username", key="new_u")
            new_p = st.text_input("New Password", type="password", key="new_p")
            if st.button("Create Account"):
                if new_u and new_p:
                    admin_repo.add_user(new_u, new_p, role="staff")
                    st.rerun()

    st.divider()

    # --- SECTION 2: MENU MANAGEMENT (NEW ADD/DELETE FEATURES) ---
    st.subheader("🍱 Menu Inventory")

    # A. Add New Item (Only for Norma)
    if role in ['admin', 'primary_admin']:
        with st.expander("➕ Add New Food Item"):
            add_n = st.text_input("Item Name")
            add_c = st.selectbox("Category", ["Lunch Combo", "Noodles", "Side Dish", "Dessert", "Drink", "Add-on"])
            add_p = st.number_input("Price", min_value=0.0, format="%.2f")
            add_s = st.number_input("Starting Stock", min_value=0, step=1)
            if st.button("Add to Menu"):
                if add_n:
                    menu_repo.add_menu_item(add_n, add_c, add_p, add_s)
                    st.success(f"Added {add_n}!")
                    st.rerun()

    st.write("") # Spacer

    # B. List and Manage Existing Items
    items = menu_repo.get_all_menu_items()
    if items:
        for item_id, name, cat, price, stock in items:
            # Create a right-aligned feel using a status label
            if stock == 0:
                status_label = "🔴 SOLD OUT"
            elif stock < 5:
                status_label = f"⚠️ LOW STOCK: {stock}"
            else:
                status_label = f"🟢 STOCK: {stock}"
            
            # This string uses a simple trick to push the status to the side
            header_label = f"{name} | {status_label}"
            
            with st.expander(header_label):
                if role in ['admin', 'primary_admin']:
                    # Edit Fields
                    en = st.text_input("Name", value=name, key=f"en_{item_id}")
                    ep = st.number_input("Price", value=float(price), key=f"ep_{item_id}")
                    es = st.number_input("Stock", value=int(stock), key=f"es_{item_id}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Save Changes", key=f"sv_{item_id}"):
                            menu_repo.update_menu_item(item_id, en, cat, ep, es)
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Delete Item", key=f"menu_del_{item_id}"):
                            menu_repo.delete_menu_item(item_id)
                            st.rerun()
                else:
                    # Staff View
                    st.write(f"Category: {cat} | Price: ${price:.2f}")
                    restock = st.number_input("Restock", min_value=0, key=f"re_{item_id}")
                    if st.button("Update Stock", key=f"up_{item_id}"):
                        menu_repo.update_menu_item(item_id, name, cat, price, stock + restock)
                        st.rerun()

    # --- SECTION 3: RECENT ORDERS (With Date Filter) ---
    st.divider()
    st.subheader("📝 Order History")

    # 1. Date Range Selector
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_dt = st.date_input("From Date")
    with col_d2:
        end_dt = st.date_input("To Date")

    # 2. Fetch filtered orders
    # We convert the dates to strings (YYYY-MM-DD) for the database
    orders = order_repo.get_orders_by_date_range(str(start_dt), str(end_dt))

    if not orders:
        st.info(f"No orders found between {start_dt} and {end_dt}.")
    else:
        st.write(f"Showing **{len(orders)}** orders for this period.")
        
        for o in orders:
            # Drop-down style expander
            with st.expander(f"Order #{o[1]} - {o[2]} (${o[5]:.2f})"):
                st.write(f"**Phone:** {o[3]} | **Time:** {o[4]}")
                st.divider()
                
                o_items = order_repo.get_order_items(o[0])
                receipt_text = f"ORDER #{o[1]}\nCustomer: {o[2]}\n"
                
                for i in o_items:
                    line = f"{i[1]}x {i[0]} - ${i[3]:.2f}"
                    st.write(f"- {line}")
                    receipt_text += line + "\n"
                
                st.divider()
                
                # Action Buttons
                c_print, c_del = st.columns(2)
                with c_print:
                    st.download_button("📄 Download Receipt", receipt_text, file_name=f"Order_{o[1]}.txt", key=f"p_{o[0]}")
                
                with c_del:
                    if role in ['admin', 'primary_admin']:
                        if st.button("🗑️ Delete Record", key=f"del_o_{o[0]}"):
                            order_repo.delete_order(o[0])
                            st.rerun()
