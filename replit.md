# Yummoz - Momo Shop Management System

## Overview

Yummoz is a comprehensive momo shop management system built with Streamlit for the frontend and Firebase Realtime Database for backend data storage. The application serves three main user roles: customers placing orders, cooks managing order preparation, and admins handling menu and inventory management. The system provides real-time order processing, kitchen workflow management, and inventory tracking capabilities.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid development and easy deployment of data-driven web applications
- **UI Components**: Custom CSS styling with responsive design
- **Real-time Updates**: Auto-refresh functionality for live order tracking
- **Multi-page Structure**: Separate views for customer orders, cook's dashboard, and admin panel

### Backend Architecture
- **Database**: Local JSON files - simple file-based storage for orders, menu, and inventory
- **Data Storage**: Three JSON files in root directory (orders.json, menu.json, inventory.json)
- **Data Models**: JSON-based document structure for orders, menu items, and inventory
- **No External Dependencies**: Completely self-contained with no external services required

## Key Components

### 1. Customer Order Interface
- **Purpose**: Allow customers to place momo orders
- **Features**: Form validation, real-time submission, special instructions support
- **Data Flow**: Form → Validation → Firebase → Confirmation

### 2. Cook's Dashboard
- **Purpose**: Display and manage pending orders in the kitchen
- **Features**: Real-time order display, one-click completion, order history
- **Data Flow**: Firebase → Real-time display → Status updates → Firebase

### 3. Admin Panel
- **Purpose**: Manage menu items, inventory, and view analytics
- **Features**: Menu management, inventory tracking, order statistics
- **Data Flow**: Admin inputs → Firebase → Real-time updates across all interfaces

### 4. Database Operations Layer
- **File**: `local_database.py`
- **Purpose**: Centralized JSON file database interactions
- **Functions**: CRUD operations for orders, menu items, and inventory
- **Storage**: Direct file operations on JSON files in root directory

## Data Flow

### Order Processing Flow
1. Customer adds multiple items to shopping cart through Streamlit interface
2. Order data validated and assigned unique UUID
3. Order saved to local `orders.json` file with "pending" status
4. Cook's dashboard displays orders by reading from local JSON file
5. Cook marks order as completed, which deletes it from orders.json
6. Revenue data calculated from order history for analytics

### Menu Management Flow
1. Admin performs full CRUD operations on menu items through admin panel
2. Changes saved to local `menu.json` file
3. Customer order form reads menu options from local JSON file
4. Price changes reflected immediately across all interfaces

### Inventory Tracking Flow
1. Admin performs full CRUD operations on inventory items through admin panel
2. Inventory data saved to local `inventory.json` file
3. Availability status accessible across all interfaces

## External Dependencies

### Core Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and display
- **Matplotlib**: Revenue charts and analytics visualization
- **UUID**: Unique identifier generation for orders
- **JSON**: Built-in Python library for data storage

## Deployment Strategy

### Current Setup
- **Local Development**: Direct JSON file operations on local filesystem
- **Configuration**: No external configuration needed
- **Data Storage**: JSON files in root directory for immediate access

### Production Considerations
- JSON files are stored locally and persist across application restarts
- No external API keys or service accounts required
- Streamlit deployment through Streamlit Cloud, Heroku, or similar platforms
- Consider database migration for high-traffic production environments

### Scalability Approach
- Local JSON files suitable for small to medium traffic
- File-based storage eliminates external dependencies
- Easy to backup and restore with simple file operations
- Consider database migration for concurrent user scenarios

## Changelog

```
Changelog:
- July 12, 2025. Implemented shopping cart system with multiple items, complete CRUD operations for admin panel, revenue analytics with graphs, and cleaned up all Firebase-related code
- July 05, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## Technical Notes

### Database Schema
```json
{
  "orders": {
    "order_id": {
      "customer_name": "string",
      "momo_type": "string",
      "quantity": "number",
      "special_instructions": "string",
      "timestamp": "ISO string",
      "status": "pending|completed"
    }
  },
  "menu": {
    "item_name": "price_number"
  },
  "inventory": {
    "item_name": {
      "available": "boolean",
      "quantity": "number"
    }
  }
}
```

### Security Considerations
- No external API keys or credentials required
- Local JSON files accessible only to application
- No network-based security concerns for data storage

### Development Workflow
- Modular code structure with separated concerns
- Error handling implemented for file operations
- Simple file-based storage ensures data persistence across application restarts
- No external service dependencies for development or deployment