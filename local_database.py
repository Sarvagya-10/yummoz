import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import streamlit as st

# Database file paths in root directory
ORDERS_FILE = "orders.json"
MENU_FILE = "menu.json"
INVENTORY_FILE = "inventory.json"

def load_json_file(file_path: str, default_data: Dict = None) -> Dict:
    """Load JSON file with fallback to default data"""
    
    if default_data is None:
        default_data = {}
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create file with default data
            save_json_file(file_path, default_data)
            return default_data
    except Exception as e:
        st.error(f"Error loading {file_path}: {str(e)}")
        return default_data

def save_json_file(file_path: str, data: Dict) -> bool:
    """Save data to JSON file"""
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving {file_path}: {str(e)}")
        return False

# Order operations
def save_order(order_data: Dict[str, Any]) -> bool:
    """Save order to local JSON database"""
    try:
        orders = load_json_file(ORDERS_FILE, {})
        order_id = str(uuid.uuid4())
        orders[order_id] = order_data
        return save_json_file(ORDERS_FILE, orders)
    except Exception as e:
        st.error(f"Error saving order: {str(e)}")
        return False

def get_orders() -> Dict[str, Any]:
    """Get all orders from local JSON database"""
    return load_json_file(ORDERS_FILE, {})

def update_order_status(order_id: str, status: str) -> bool:
    """Update order status in local JSON database"""
    try:
        orders = load_json_file(ORDERS_FILE, {})
        if order_id in orders:
            orders[order_id]['status'] = status
            if status == 'completed':
                orders[order_id]['completed_at'] = datetime.now().isoformat()
            return save_json_file(ORDERS_FILE, orders)
        return False
    except Exception as e:
        st.error(f"Error updating order status: {str(e)}")
        return False

def delete_order(order_id: str) -> bool:
    """Delete order from local JSON database"""
    try:
        orders = load_json_file(ORDERS_FILE, {})
        if order_id in orders:
            del orders[order_id]
            return save_json_file(ORDERS_FILE, orders)
        return False
    except Exception as e:
        st.error(f"Error deleting order: {str(e)}")
        return False

# Menu operations
def save_menu_item(item_name: str, price: float, image_url: str = None) -> bool:
    """Save menu item to local JSON database"""
    try:
        menu = load_json_file(MENU_FILE, {})
        if image_url is None:
            # Generate a placeholder image URL if none provided
            image_url = f"https://via.placeholder.com/200x150/FF6B6B/FFFFFF?text={item_name.replace(' ', '%20')}"
        
        menu[item_name] = {"price": price, "image": image_url}
        return save_json_file(MENU_FILE, menu)
    except Exception as e:
        st.error(f"Error saving menu item: {str(e)}")
        return False

def get_menu() -> Dict[str, Dict]:
    """Get menu items from local JSON database"""
    default_menu = {
        "Chicken Momo": {"price": 120.0, "image": "https://via.placeholder.com/200x150/FF6B6B/FFFFFF?text=Chicken%20Momo"},
        "Veg Momo": {"price": 80.0, "image": "https://via.placeholder.com/200x150/4ECDC4/FFFFFF?text=Veg%20Momo"},
        "Buff Momo": {"price": 100.0, "image": "https://via.placeholder.com/200x150/45B7D1/FFFFFF?text=Buff%20Momo"},
        "Paneer Momo": {"price": 90.0, "image": "https://via.placeholder.com/200x150/F7DC6F/FFFFFF?text=Paneer%20Momo"}
    }
    return load_json_file(MENU_FILE, default_menu)

def delete_menu_item(item_name: str) -> bool:
    """Delete menu item from local JSON database"""
    try:
        menu = load_json_file(MENU_FILE, {})
        if item_name in menu:
            del menu[item_name]
            return save_json_file(MENU_FILE, menu)
        return False
    except Exception as e:
        st.error(f"Error deleting menu item: {str(e)}")
        return False

# Inventory operations
def save_inventory(inventory_data: Dict[str, Any]) -> bool:
    """Save inventory data to local JSON database"""
    try:
        return save_json_file(INVENTORY_FILE, inventory_data)
    except Exception as e:
        st.error(f"Error saving inventory: {str(e)}")
        return False

def get_inventory() -> Dict[str, Any]:
    """Get inventory data from local JSON database"""
    default_inventory = {
        "Chicken": {"available": True, "quantity": 100},
        "Vegetables": {"available": True, "quantity": 50},
        "Flour": {"available": True, "quantity": 20},
        "Spices": {"available": True, "quantity": 10},
        "Oil": {"available": True, "quantity": 5}
    }
    return load_json_file(INVENTORY_FILE, default_inventory)

# Statistics operations
def get_order_statistics() -> Dict[str, Any]:
    """Get order statistics from local JSON database"""
    try:
        orders = get_orders()
        if not orders:
            return {}
        
        stats = {
            'total_orders': len(orders),
            'completed_orders': 0,
            'pending_orders': 0,
            'momo_types': {},
            'total_revenue': 0
        }
        
        menu = get_menu()
        
        for order in orders.values():
            if order.get('status') == 'completed':
                stats['completed_orders'] += 1
            else:
                stats['pending_orders'] += 1
            
            momo_type = order.get('momo_type', 'Unknown')
            quantity = order.get('quantity', 0)
            
            if momo_type in stats['momo_types']:
                stats['momo_types'][momo_type] += quantity
            else:
                stats['momo_types'][momo_type] = quantity
            
            # Calculate revenue if menu price is available
            if menu and momo_type in menu:
                stats['total_revenue'] += quantity * menu[momo_type]
        
        return stats
    except Exception as e:
        st.error(f"Error getting statistics: {str(e)}")
        return {}
