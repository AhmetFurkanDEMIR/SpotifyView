import uvicorn
from fastapi import FastAPI
from pathlib import Path
from fastAPI.routes import routes
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="../spotifyAPI/fastAPI/static"), name="static")
app.include_router(routes)

if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app", host="0.0.0.0", port=80)


