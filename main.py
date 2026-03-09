import os
import sys

root = os.path.dirname(os.path.abspath(__file__))
if root not in sys.path:
    sys.path.insert(0, root)

from fastapi import FastAPI
from dotenv import load_dotenv
from routers.summary_router import router 
from scheduler.session_scheduler import scheduler 

load_dotenv()

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
async def start():
    if not scheduler.running:
        scheduler.start()

