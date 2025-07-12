# Yummoz - Momo Shop Management System

A complete momo shop management system built with Streamlit and Firebase for order processing, kitchen management, and inventory tracking.

## Features

### Customer Order Form
- Input fields for customer name, momo type, quantity, and special instructions
- Real-time order submission to Firebase Realtime Database
- User-friendly interface with form validation

### Cook's Order View
- Real-time display of all pending orders
- Clean table format showing order details
- One-click order completion marking
- Auto-refresh functionality for real-time updates
- Separate view for completed orders

### Admin Panel
- Menu management: Add new momo types and prices
- Inventory checklist: Track available stock items
- Order statistics and analytics
- Real-time data synchronization

## Firebase Database Structure

The application uses Firebase Realtime Database with the following structure:

```json
{
  "orders": {
    "order_id_1": {
      "customer_name": "John Doe",
      "momo_type": "Chicken Momo",
      "quantity": 2,
      "special_instructions": "Extra spicy",
      "timestamp": "2025-07-05T10:30:00",
      "status": "pending"
    }
  },
  "menu": {
    "Chicken Momo": 120.00,
    "Veg Momo": 80.00,
    "Buff Momo": 100.00,
    "Paneer Momo": 90.00
  },
  "inventory": {
    "Chicken": {
      "available": true,
      "quantity": 100
    },
    "Vegetables": {
      "available": true,
      "quantity": 50
    },
    "Flour": {
      "available": true,
      "quantity": 20
    }
  }
}
