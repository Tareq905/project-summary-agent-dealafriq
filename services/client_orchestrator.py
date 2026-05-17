import logging
import requests
from fetchers.client_fetcher import fetch_all_clients
from agents.client_summary_agent import run_client_analysis
from config.settings import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "x-backend-service": settings.BACKEND_SERVICE_SECRET,
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
}


def push_client_result(client_id: str, result: dict) -> bool:
    url = f"{settings.CLIENT_PUSH_API}/{client_id}"
    try:
        response = requests.post(url, json=result, headers=HEADERS, timeout=30)
        if response.status_code in (200, 201):
            logger.info(f"✅ Client [{client_id}] pushed successfully.")
            return True
        logger.error(f"❌ Client [{client_id}] push failed: {response.status_code} — {response.text}")
        return False
    except Exception as e:
        logger.error(f"❌ Client [{client_id}] push exception: {e}")
        return False


def analyze_all_clients(client_id: str = None):
    logger.info("🚀 Starting Client Intelligence Analysis...")

    clients = fetch_all_clients()

    # Filter to single client if id is provided
    if client_id:
        clients = [c for c in clients if c.get("id") == client_id]
        if not clients:
            logger.warning(f"⚠️ No client found with id: {client_id}")
            return []

    total   = len(clients)
    results = []

    logger.info(f"📥 Fetched {total} clients.")

    if not clients:
        logger.warning("⚠️ No clients found to analyze.")
        return []

    for index, client in enumerate(clients, start=1):
        c_id        = client.get("id", "Unknown")
        client_name = client.get("name", "Unknown")
        logger.info(f"🔍 [{index}/{total}] Analyzing client: {client_name}")

        try:
            analysis = run_client_analysis(client)

            if not analysis:
                logger.error(f"❌ AI returned None for client: {client_name}")
                continue

            push_client_result(c_id, analysis)

            results.append({
                "clientId":   c_id,
                "clientName": client_name,
                **analysis
            })
            logger.info(f"✅ [{index}/{total}] Client '{client_name}' analyzed and pushed.")

        except Exception as e:
            logger.error(f"💥 Error analyzing client '{client_name}': {e}")
            continue

    logger.info(f"🏁 Client Analysis Complete. {len(results)}/{total} processed.")
    return results