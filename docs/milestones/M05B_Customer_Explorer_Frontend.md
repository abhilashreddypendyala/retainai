# Milestone 05B: Customer Explorer Frontend

## Objective
Implement the Customer Explorer frontend module, providing a streamlined Streamlit interface for users to browse, search, and filter the customer base.

## Architecture
This implementation adheres strictly to the defined project architecture:
`Customer Intelligence UI` -> `API Client` -> `Customer API` -> `SQLite`

Direct database access is strictly prohibited from the frontend.

## Components Created/Modified

### 1. API Client (`frontend/utils/api_client.py`)
- Reused the existing `APIClient` class, avoiding duplicated HTTP connection logic.
- Added 3 new methods to interact with the backend API:
  - `get_customers(page, page_size)`: Fetches a paginated customer list.
  - `search_customers(query)`: Sends search queries to the backend.
  - `filter_customers(segment, country, churn_prediction)`: Handles dynamic URL parameter creation for filters.

### 2. UI Components
- **`frontend/components/customer_table.py`**: A new, reusable Streamlit component `render_customer_table`. Extends the `dark_table` utility to format the customer JSON response cleanly, converting raw data into formatted strings (e.g. percentages, currency, text mappings) and displaying the dataframe using Streamlit's native `st.dataframe`.

### 3. Customer Intelligence Page (`frontend/pages/Customer_Intelligence.py`)
- Created the main entry point for the Customer Intelligence module.
- Features:
  - **Header & Layout**: Maintained visual consistency with the Dashboard, reusing global styles and headers.
  - **Search**: Interactive text box to trigger customer ID partial searches.
  - **Filters**: Dropdowns for Segment, Country, and Churn Status. Changing a filter reruns the query and displays the results instantly.
  - **Pagination**: Added backend-driven pagination (Next/Previous controls) defaulting to 50 rows per page.
  - **Loading State & Error Handling**: Displays `st.spinner` while network requests happen and catches any backend connection errors cleanly to present a friendly message without crashing Streamlit.

## Constraints Addressed
- The UI maintains exact visual coherence with the rest of RetainAI.
- Uses `api_client` entirely for data access.
- Avoided implementing profiles/charts as instructed.
