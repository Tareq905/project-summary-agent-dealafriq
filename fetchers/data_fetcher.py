import logging
import requests
from config.settings import settings

logger = logging.getLogger(__name__)


def fetch_data(url):
    """Generic GET fetcher. Returns list or empty list on failure."""
    headers = {"x-backend-service": settings.BACKEND_SERVICE_SECRET}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            json_res = response.json()
            if isinstance(json_res, list):
                return json_res
            return json_res.get("data", []) or []
        logger.error(f"❌ fetch_data error: {response.status_code} — {url}")
        return []
    except Exception as e:
        logger.error(f"❌ fetch_data exception: {e} — {url}")
        return []