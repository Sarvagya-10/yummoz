import streamlit as st
import pandas as pd
from datetime import datetime
import json
from local_database import (
    save_order,
    get_orders,
    update_order_status,
    delete_order,
    save_menu_item,
    get_menu,
    delete_menu_item,
    save_inventory,
    get_inventory,
    get_order_statistics
)

# App configuration
st.set_page_config(
    page_title="Yummoz - Momo Shop Management System",
    page_icon="🥟",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">🥟 Yummoz - Momo Shop Management System</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select Page", ["Customer Order", "Cook's View", "Admin Panel"])

def customer_order_page():
    st.header("📝 Customer Order Form")
    
    # Initialize cart in session state
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if 'customer_name' not in st.session_state:
        st.session_state.customer_name = ""
    if 'special_instructions' not in st.session_state:
        st.session_state.special_instructions = ""
    
    # Get menu items for dropdown
    try:
        menu_items = get_menu()
        if not menu_items:
            st.warning("No menu items available. Please contact admin to add items.")
            return
    except Exception as e:
        st.error(f"Error loading menu: {str(e)}")
        return
    
    # Customer information
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name", value=st.session_state.customer_name, placeholder="Enter customer name")
        st.session_state.customer_name = customer_name
    
    with col2:
        special_instructions = st.text_area("Special Instructions", value=st.session_state.special_instructions, placeholder="Any special requests?")
        st.session_state.special_instructions = special_instructions
    
    st.divider()
    
    # Add items to cart section
    st.subheader("🛒 Add Items to Cart")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_momo = st.selectbox("Select Momo Type", list(menu_items.keys()))
    with col2:
        quantity = st.number_input("Quantity", min_value=1, max_value=50, value=1)
    with col3:
        price = menu_items[selected_momo]
        st.write(f"Price: ${price:.2f}")
    
    if st.button("➕ Add to Cart"):
        # Add item to cart
        cart_item = {
            "momo_type": selected_momo,
            "quantity": quantity,
            "price": price,
            "total": price * quantity
        }
        st.session_state.cart.append(cart_item)
        st.success(f"Added {quantity}x {selected_momo} to cart!")
        st.rerun()
    
    st.divider()
    
    # Display cart
    if st.session_state.cart:
        st.subheader("🛒 Your Cart")
        
        total_amount = 0
        for i, item in enumerate(st.session_state.cart):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                st.write(f"**{item['momo_type']}**")
            with col2:
                st.write(f"Qty: {item['quantity']}")
            with col3:
                st.write(f"${item['price']:.2f}")
            with col4:
                st.write(f"${item['total']:.2f}")
            with col5:
                if st.button("🗑️", key=f"remove_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
            
            total_amount += item['total']
        
        st.divider()
        st.markdown(f"### **Total: ${total_amount:.2f}**")
        
        # Submit order button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🛒 Submit Order", type="primary"):
                if customer_name.strip():
                    try:
                        # Create order data with all cart items
                        order_data = {
                            "customer_name": customer_name.strip(),
                            "items": st.session_state.cart,
                            "special_instructions": special_instructions.strip() if special_instructions else "",
                            "total_amount": total_amount,
                            "timestamp": datetime.now().isoformat(),
                            "status": "pending"
                        }
                        
                        success = save_order(order_data)
                        if success:
                            st.success("🎉 Order submitted successfully!")
                            st.balloons()
                            # Clear cart and form
                            st.session_state.cart = []
                            st.session_state.customer_name = ""
                            st.session_state.special_instructions = ""
                            st.rerun()
                        else:
                            st.error("❌ Failed to submit order. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Error submitting order: {str(e)}")
                else:
                    st.error("❌ Please enter a customer name.")
        
        with col2:
            if st.button("🗑️ Clear Cart"):
                st.session_state.cart = []
                st.rerun()
    else:
        st.info("🛒 Your cart is empty. Add some items above!")

def cooks_view_page():
    st.header("👨‍🍳 Cook's Order View")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh orders", value=True)
    
    if auto_refresh:
        # Auto-refresh every 5 seconds
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now()
        
        # Check if 5 seconds have passed
        if (datetime.now() - st.session_state.last_refresh).seconds >= 5:
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    # Manual refresh button
    if st.button("🔄 Refresh Orders"):
        st.rerun()
    
    try:
        orders = get_orders()
        
        if orders:
            # Display all orders (all are pending since completed ones are deleted)
            order_list = []
            for order_id, order_data in orders.items():
                order_data['order_id'] = order_id
                order_list.append(order_data)
            
            if order_list:
                st.subheader("🔥 Active Orders")
                for order in order_list:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**Customer:** {order['customer_name']}")
                            
                            # Display items in the order
                            if 'items' in order:
                                st.write("**Items:**")
                                for item in order['items']:
                                    st.write(f"• {item['quantity']}x {item['momo_type']} (${item['total']:.2f})")
                                st.write(f"**Total Amount:** ${order.get('total_amount', 0):.2f}")
                            else:
                                # Handle old order format
                                st.write(f"**Order:** {order.get('quantity', 1)}x {order.get('momo_type', 'Unknown')}")
                            
                            if order.get('special_instructions'):
                                st.write(f"**Special Instructions:** {order['special_instructions']}")
                            st.write(f"**Time:** {order['timestamp'][:19]}")
                        
                        with col2:
                            st.write(f"**Status:** {order.get('status', 'pending').upper()}")
                        
                        with col3:
                            if st.button(f"✅ Complete & Remove", key=f"complete_{order['order_id']}"):
                                try:
                                    success = delete_order(order['order_id'])
                                    if success:
                                        st.success("Order completed and removed!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to complete order.")
                                except Exception as e:
                                    st.error(f"Error completing order: {str(e)}")
                        
                        st.divider()
            else:
                st.info("🎉 No pending orders! All caught up.")
            
            # Note: Completed orders are automatically removed from the system
        else:
            st.info("📋 No orders yet. Waiting for customers...")
    
    except Exception as e:
        st.error(f"❌ Error loading orders: {str(e)}")

def admin_panel_page():
    st.header("⚙️ Admin Panel")
    
    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["🍽️ Menu Management", "📦 Inventory Management", "📊 Order Statistics"])
    
    with tab1:
        st.subheader("🍽️ Menu Management")
        
        # Display current menu with CRUD operations
        try:
            menu_items = get_menu()
            if menu_items:
                st.write("**Current Menu Items:**")
                
                # Create a more interactive table
                for item_name, price in menu_items.items():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{item_name}**")
                    
                    with col2:
                        st.write(f"${price:.2f}")
                    
                    with col3:
                        # Edit button
                        if st.button("✏️ Edit", key=f"edit_menu_{item_name}"):
                            st.session_state[f"editing_menu_{item_name}"] = True
                            st.rerun()
                    
                    with col4:
                        # Delete button
                        if st.button("🗑️ Delete", key=f"delete_menu_{item_name}"):
                            try:
                                success = delete_menu_item(item_name)
                                if success:
                                    st.success(f"Deleted {item_name} from menu!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete item.")
                            except Exception as e:
                                st.error(f"Error deleting item: {str(e)}")
                    
                    # Edit form (show if editing)
                    if st.session_state.get(f"editing_menu_{item_name}", False):
                        with st.form(f"edit_menu_{item_name}"):
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                new_name = st.text_input("New Name", value=item_name)
                            
                            with col2:
                                new_price = st.number_input("New Price", min_value=0.0, step=0.1, format="%.2f", value=price)
                            
                            with col3:
                                if st.form_submit_button("💾 Update"):
                                    try:
                                        # Delete old item and add new one
                                        delete_menu_item(item_name)
                                        success = save_menu_item(new_name.strip(), new_price)
                                        if success:
                                            st.success(f"Updated menu item!")
                                            st.session_state[f"editing_menu_{item_name}"] = False
                                            st.rerun()
                                        else:
                                            st.error("Failed to update item.")
                                    except Exception as e:
                                        st.error(f"Error updating item: {str(e)}")
                                
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state[f"editing_menu_{item_name}"] = False
                                    st.rerun()
                    
                    st.divider()
            else:
                st.info("No menu items found. Add some items below.")
        except Exception as e:
            st.error(f"Error loading menu: {str(e)}")
        
        # Add new menu item
        st.subheader("➕ Add New Menu Item")
        with st.form("add_menu_item"):
            col1, col2 = st.columns(2)
            
            with col1:
                item_name = st.text_input("Item Name", placeholder="e.g., Chicken Momo")
            
            with col2:
                item_price = st.number_input("Price", min_value=0.0, step=0.1, format="%.2f")
            
            add_item = st.form_submit_button("➕ Add Item", type="primary")
            
            if add_item:
                if item_name.strip():
                    try:
                        success = save_menu_item(item_name.strip(), item_price)
                        if success:
                            st.success(f"Added {item_name} to menu!")
                            st.rerun()
                        else:
                            st.error("Failed to add item to menu.")
                    except Exception as e:
                        st.error(f"Error adding item: {str(e)}")
                else:
                    st.error("Please enter an item name.")
    
    with tab2:
        st.subheader("📦 Inventory Management")
        
        # Get current inventory
        try:
            inventory = get_inventory()
            if not inventory:
                inventory = {
                    "Chicken": {"available": True, "quantity": 100},
                    "Vegetables": {"available": True, "quantity": 50},
                    "Flour": {"available": True, "quantity": 20},
                    "Spices": {"available": True, "quantity": 10},
                    "Oil": {"available": True, "quantity": 5}
                }
                # Save default inventory
                save_inventory(inventory)
        except Exception as e:
            st.error(f"Error loading inventory: {str(e)}")
            inventory = {}
        
        # Display inventory with CRUD operations
        if inventory:
            st.write("**Current Inventory:**")
            
            for item_name, details in inventory.items():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{item_name}**")
                
                with col2:
                    available = details.get('available', True)
                    status = "✅ Available" if available else "❌ Out of Stock"
                    st.write(status)
                
                with col3:
                    quantity = details.get('quantity', 0)
                    st.write(f"Qty: {quantity}")
                
                with col4:
                    # Edit button
                    if st.button("✏️ Edit", key=f"edit_inv_{item_name}"):
                        st.session_state[f"editing_inv_{item_name}"] = True
                        st.rerun()
                
                with col5:
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_inv_{item_name}"):
                        try:
                            current_inventory = get_inventory()
                            if item_name in current_inventory:
                                del current_inventory[item_name]
                                success = save_inventory(current_inventory)
                                if success:
                                    st.success(f"Deleted {item_name} from inventory!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete item.")
                        except Exception as e:
                            st.error(f"Error deleting item: {str(e)}")
                
                # Edit form (show if editing)
                if st.session_state.get(f"editing_inv_{item_name}", False):
                    with st.form(f"edit_inv_{item_name}"):
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        
                        with col1:
                            new_name = st.text_input("New Name", value=item_name)
                        
                        with col2:
                            new_available = st.checkbox("Available", value=details.get('available', True))
                        
                        with col3:
                            new_quantity = st.number_input("Quantity", min_value=0, value=details.get('quantity', 0))
                        
                        with col4:
                            if st.form_submit_button("💾 Update"):
                                try:
                                    current_inventory = get_inventory()
                                    # Remove old item
                                    if item_name in current_inventory:
                                        del current_inventory[item_name]
                                    # Add updated item
                                    current_inventory[new_name.strip()] = {
                                        "available": new_available,
                                        "quantity": new_quantity
                                    }
                                    success = save_inventory(current_inventory)
                                    if success:
                                        st.success(f"Updated inventory item!")
                                        st.session_state[f"editing_inv_{item_name}"] = False
                                        st.rerun()
                                    else:
                                        st.error("Failed to update item.")
                                except Exception as e:
                                    st.error(f"Error updating item: {str(e)}")
                            
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"editing_inv_{item_name}"] = False
                                st.rerun()
                
                st.divider()
        
        # Add new inventory item
        st.subheader("➕ Add New Inventory Item")
        with st.form("add_inventory_item"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_item_name = st.text_input("Item Name", placeholder="e.g., Cheese")
            
            with col2:
                new_item_available = st.checkbox("Available", value=True)
            
            with col3:
                new_item_quantity = st.number_input("Quantity", min_value=0, value=0)
            
            add_inv_item = st.form_submit_button("➕ Add Item", type="primary")
            
            if add_inv_item:
                if new_item_name.strip():
                    try:
                        current_inventory = get_inventory()
                        current_inventory[new_item_name.strip()] = {
                            "available": new_item_available,
                            "quantity": new_item_quantity
                        }
                        success = save_inventory(current_inventory)
                        if success:
                            st.success(f"Added {new_item_name} to inventory!")
                            st.rerun()
                        else:
                            st.error("Failed to add item to inventory.")
                    except Exception as e:
                        st.error(f"Error adding item: {str(e)}")
                else:
                    st.error("Please enter an item name.")
    
    with tab3:
        st.subheader("📊 Order Statistics & Revenue")
        
        try:
            orders = get_orders()
            if orders:
                # Calculate statistics
                total_orders = len(orders)
                total_revenue = 0
                order_data = []
                
                for order_id, order in orders.items():
                    if 'total_amount' in order:
                        total_revenue += order['total_amount']
                        order_data.append({
                            'date': order['timestamp'][:10],
                            'revenue': order['total_amount'],
                            'customer': order['customer_name']
                        })
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Orders", total_orders)
                
                with col2:
                    st.metric("Total Revenue", f"${total_revenue:.2f}")
                
                with col3:
                    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
                    st.metric("Average Order Value", f"${avg_order_value:.2f}")
                
                # Revenue chart
                if order_data:
                    st.subheader("📈 Revenue Chart")
                    
                    # Group by date
                    import pandas as pd
                    df = pd.DataFrame(order_data)
                    daily_revenue = df.groupby('date')['revenue'].sum().reset_index()
                    
                    # Create bar chart
                    st.bar_chart(daily_revenue.set_index('date')['revenue'])
                    
                    # Recent orders table
                    st.subheader("📋 Recent Orders")
                    recent_orders = []
                    for order_id, order_data in orders.items():
                        order_info = {
                            'Order ID': order_id[:8],
                            'Customer': order_data['customer_name'],
                            'Total': f"${order_data.get('total_amount', 0):.2f}",
                            'Status': order_data.get('status', 'pending').upper(),
                            'Date': order_data['timestamp'][:19]
                        }
                        recent_orders.append(order_info)
                    
                    # Sort by date (newest first)
                    recent_orders.sort(key=lambda x: x['Date'], reverse=True)
                    
                    # Show only last 10 orders
                    recent_orders = recent_orders[:10]
                    
                    if recent_orders:
                        st.dataframe(recent_orders, use_container_width=True)
                else:
                    st.info("No revenue data available yet.")
            else:
                st.info("No orders yet to display statistics.")
        
        except Exception as e:
            st.error(f"Error loading order statistics: {str(e)}")

# Page routing
if page == "Customer Order":
    customer_order_page()
elif page == "Cook's View":
    cooks_view_page()
elif page == "Admin Panel":
    admin_panel_page()

# Footer
st.markdown("---")
st.markdown("© 2025 Yummoz - Momo Shop Management System")
