import os
import sys
import logging
import uvicorn

root = os.path.dirname(os.path.abspath(__file__))
if root not in sys.path:
    sys.path.insert(0, root)

from fastapi import FastAPI
from dotenv import load_dotenv
from routers.summary_router import router
from scheduler.session_scheduler import scheduler
from scheduler.session_scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
load_dotenv()

app = FastAPI(title="AI Project Management Agent")
app.include_router(router)


@app.on_event("startup")
async def start():
    if not scheduler.running:
        scheduler.start()
        logging.info("✅ Scheduler started.")


@app.on_event("shutdown")
async def stop():
    if scheduler.running:
        scheduler.shutdown()
        logging.info(" Scheduler stopped.")

@app.on_event("startup")
async def start():
    start_scheduler()

@app.on_event("shutdown")
async def stop():
    stop_scheduler()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)