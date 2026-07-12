# Milestone 05A: Customer Backend Foundation

## Objective
Implement the foundational backend infrastructure for the Customer Intelligence module, providing clean, RESTful APIs to access the master customer dataset. This module establishes a strict separation between the SQLite database and future frontend requests.

## Architecture
This implementation adheres strictly to the defined project architecture:
`Frontend (Future)` -> `Customer API` -> `Customer Service` -> `SQLite`

## Components Created

### 1. Pydantic Schemas (`backend/schemas/customer.py`)
- `CustomerSummary`: Compact model for list, search, and filter results.
- `CustomerProfile`: Comprehensive 360-degree view of a customer (includes RFM, AOV, and Purchase Frequency).
- `CustomerListResponse`: Schema for paginated list responses.

### 2. Service Layer (`backend/services/customer_service.py`)
- Encapsulates all SQLite database interactions.
- Optimized country lookups using a memory-mapped Python dictionary to avoid expensive O(N) database subqueries over the 400,000+ row `transactions` table.
- Implements:
  - `get_customers(page, page_size)`
  - `get_customer_by_id(customer_id)`
  - `search_customers(query)`
  - `filter_customers(segment, country, churn_prediction)`

### 3. API Router (`backend/api/customers.py`)
- Exposes `GET /customers`
- Exposes `GET /customers/search`
- Exposes `GET /customers/filter`
- Exposes `GET /customers/{customer_id}`
- Registered the router globally inside `backend/main.py`.

## Constraints Addressed
- All operations are strictly read-only.
- No modifications were made to the Streamlit UI, existing APIs, or database structure.
- Pagination, robust error handling (404, 400), and dynamic filtering were implemented successfully.
