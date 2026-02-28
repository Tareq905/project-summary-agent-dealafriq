import sys
import os
import uvicorn

# This line forces Python to look for the 'app' folder correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)