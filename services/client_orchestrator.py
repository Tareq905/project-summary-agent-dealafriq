import logging
import traceback
import json
import requests
from fetchers.client_fetcher import fetch_all_clients
from agents.client_summary_agent import run_client_analysis
from config.settings import settings

# ════════════════════════════════════════════════════════════════════
# 🚨 IF YOU SEE THIS BANNER IN SERVER LOG, THE NEW FILE IS LOADED 🚨
# ════════════════════════════════════════════════════════════════════
print("\n" + "*" * 35)
print("* NEW client_orchestrator.py LOADED — VERSION 2.0 (with PUSH_DBG)")
print("*" * 35 + "\n")

logger = logging.getLogger(__name__)

HEADERS = {
    "x-backend-service": settings.BACKEND_SERVICE_SECRET,
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
}


def push_client_result(client_id: str, result: dict) -> bool:
    """
    Push client analysis to backend.
    FULL DIAGNOSTIC version — prints every detail of the outgoing request
    and the incoming response so we can compare with Postman exactly.
    """
    url = f"{settings.CLIENT_PUSH_API}/{client_id}"
    payload = {"clientId": client_id, **result}

    # ── PRE-REQUEST DIAGNOSTIC ──────────────────────────────
    print("\n")
    print("═" * 70)
    print(f"📤 [PUSH_DBG] Preparing POST request for client: {client_id}")
    print("═" * 70)
    print(f"🔗 URL: {repr(url)}")  # repr() reveals hidden chars
    print(f"🔗 URL length: {len(url)}")
    print(f"📋 Headers being sent:")
    for k, v in HEADERS.items():
        if k == "x-backend-service":
            print(f"     {k}: {repr(v)} (len={len(v) if v else 'None/empty'})")
        else:
            print(f"     {k}: {v}")
    print(f"📦 Payload top-level keys: {list(payload.keys())}")
    print(f"📦 Payload size: {len(json.dumps(payload))} bytes")
    print(f"📦 Payload preview (first 500 chars):")
    print(f"     {json.dumps(payload)[:500]}")
    print("─" * 70)

    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=30)

        # ── POST-RESPONSE DIAGNOSTIC ────────────────────────
        print(f"📥 [PUSH_DBG] Response received from backend")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response URL (after redirects): {response.url}")
        print(f"   Response Headers:")
        for k, v in response.headers.items():
            print(f"     {k}: {v}")
        print(f"   Response Body (first 1500 chars):")
        print(f"     {response.text[:1500]}")
        print("═" * 70)
        print("\n")

        if response.status_code in (200, 201):
            logger.info(f"✅ Client [{client_id}] pushed successfully.")
            return True

        logger.error(f"❌ Client [{client_id}] push failed: {response.status_code} — {response.text}")
        return False

    except Exception as e:
        print(f"💥 [PUSH_DBG] Exception during POST: {type(e).__name__}: {e}")
        print(f"   Traceback:\n{traceback.format_exc()}")
        print("═" * 70 + "\n")
        logger.error(f"❌ Client [{client_id}] push exception: {e}")
        return False


def analyze_all_clients(client_id: str = None):
    logger.info("🚀 Starting Client Intelligence Analysis...")

    # ── DIAGNOSTIC: Print env values being used ─────────────
    print("\n")
    print("▓" * 70)
    print(f"🔧 [ENV_DBG] Configuration loaded at runtime:")
    print(f"   CLIENT_PUSH_API: {repr(settings.CLIENT_PUSH_API)}")
    print(f"   CLIENT_PUSH_API length: {len(settings.CLIENT_PUSH_API)}")
    secret = settings.BACKEND_SERVICE_SECRET
    print(f"   BACKEND_SERVICE_SECRET: {repr(secret[:40])}{'...' if len(secret) > 40 else ''}")
    print(f"   BACKEND_SERVICE_SECRET length: {len(secret)}")
    print("▓" * 70)
    print("\n")

    clients = fetch_all_clients()

    if not clients:
        logger.warning("⚠️ No clients found to analyze.")
        return []

    if client_id:
        clients = [
            c for c in clients
            if c.get("id") == client_id or c.get("clientId") == client_id
        ]
        if not clients:
            logger.warning(f"⚠️ No client found with id: {client_id}")
            return []

    total   = len(clients)
    results = []

    logger.info(f"📥 Processing {total} client(s).")

    for index, client in enumerate(clients, start=1):
        c_id        = client.get("id") or client.get("clientId", "Unknown")
        client_name = client.get("name", "Unknown")
        logger.info(f"🔍 [{index}/{total}] Analyzing client: {client_name} [{c_id}]")

        try:
            analysis = run_client_analysis(client)

            if not analysis:
                logger.error(f"❌ AI returned None for client: {client_name} [{c_id}]")
                continue

            # Capture actual push result
            push_ok = push_client_result(c_id, analysis)

            results.append({
                "clientId":   c_id,
                "clientName": client_name,
                **analysis
            })

            if push_ok:
                logger.info(f"✅ [{index}/{total}] Client '{client_name}' analyzed AND pushed successfully.")
            else:
                logger.warning(
                    f"⚠️ [{index}/{total}] Client '{client_name}' analyzed but PUSH FAILED. "
                    f"See [PUSH_DBG] block above for backend response details."
                )

        except Exception as e:
            logger.error("✗" * 60)
            logger.error(f"💥 Error analyzing client '{client_name}' [{c_id}]")
            logger.error(f"   Exception type: {type(e).__name__}")
            logger.error(f"   Exception message: {e}")
            logger.error(f"   FULL TRACEBACK:")
            for line in traceback.format_exc().splitlines():
                logger.error(f"     {line}")
            logger.error("✗" * 60)
            continue

    logger.info(f"🏁 Client Analysis Complete. {len(results)}/{total} processed.")
    return results