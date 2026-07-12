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

api_client = APIClient()
