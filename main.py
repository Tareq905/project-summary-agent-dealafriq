import os
import sys

# --- PORTABLE DLL LOADER (No Hardcoding) ---
def load_dlls():
    if sys.platform == 'win32':
        # 1. Get the base path of the virtual environment
        base_path = sys.prefix
        
        # 2. Paths to required DLL folders inside venv
        dll_folders = [
            os.path.join(base_path, 'Lib', 'site-packages', 'torch', 'lib'),
            os.path.join(base_path, 'Lib', 'site-packages', 'msvc_runtime', 'data'),
        ]
        
        for folder in dll_folders:
            if os.path.exists(folder):
                os.add_dll_directory(folder)

load_dlls()
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# -------------------------------------------

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