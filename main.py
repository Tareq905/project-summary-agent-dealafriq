from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routers.summary_router import router 
from scheduler.session_scheduler import scheduler 

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
async def start():
    scheduler.start()