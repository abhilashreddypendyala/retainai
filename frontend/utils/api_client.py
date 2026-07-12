import os
import logging
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        # Read API base URL from environment variable, default to localhost
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "8000")
        
        # In a real environment, API_URL might be fully qualified
        self.base_url = os.getenv("API_URL", f"http://{api_host}:{api_port}")
        
        # Enforce HTTP scheme if missing
        if not self.base_url.startswith("http"):
            self.base_url = f"http://{self.base_url}"
            
        self.session = requests.Session()
        self.timeout = 10  # Configurable timeout for graceful failure handling

    def _get(self, endpoint: str) -> dict:
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"API request failed for {url}: {e}")
            raise
            
    def _post(self, endpoint: str, data: dict = None) -> dict:
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"API request failed for POST {url}: {e}")
            raise

    def get_dashboard_summary(self):
        """Fetches the KPI summary cards from the backend."""
        return self._get("/dashboard/summary")

    def get_dashboard_charts(self):
        """Fetches the chart data arrays from the backend."""
        return self._get("/dashboard/charts")

    def get_dashboard_interventions(self):
        """Fetches the high-risk customer interventions list from the backend."""
        return self._get("/dashboard/interventions")

    def get_model_summary(self):
        """Fetches the churn model metadata from the backend."""
        return self._get("/dashboard/model-summary")

    def get_customers(self, page: int = 1, page_size: int = 50, sim_risk: float = None, sim_clv: float = None):
        """Fetches a paginated list of customers."""
        url = f"/customers?page={page}&page_size={page_size}"
        if sim_risk is not None: url += f"&sim_risk={sim_risk}"
        if sim_clv is not None: url += f"&sim_clv={sim_clv}"
        return self._get(url)

    def search_customers(self, query: str, sim_risk: float = None, sim_clv: float = None):
        """Searches for customers by ID."""
        url = f"/customers/search?q={query}"
        if sim_risk is not None: url += f"&sim_risk={sim_risk}"
        if sim_clv is not None: url += f"&sim_clv={sim_clv}"
        return self._get(url)

    def filter_customers(self, segment: str = None, country: str = None, churn_prediction: int = None, sim_risk: float = None, sim_clv: float = None):
        """Filters customers based on exact criteria."""
        params = []
        if segment: params.append(f"segment={segment}")
        if country: params.append(f"country={country}")
        if churn_prediction is not None: params.append(f"churn_prediction={churn_prediction}")
        if sim_risk is not None: params.append(f"sim_risk={sim_risk}")
        if sim_clv is not None: params.append(f"sim_clv={sim_clv}")
        query_string = "&".join(params)
        endpoint = f"/customers/filter?{query_string}" if query_string else "/customers/filter"
        return self._get(endpoint)

    def get_customer_360(self, customer_id: str):
        """Fetches the complete Customer 360 profile."""
        return self._get(f"/customers/{customer_id}")
        
    def predict_customer(self, features: dict):
        """Generates a churn prediction for the given features."""
        return self._post("/prediction", data=features)

api_client = APIClient()
