from fastapi import FastAPI
import uvicorn
from .routes import router

app = FastAPI(
    title="DeepMetrics API",
    description="API for receiving snapshots from clients",
    version="1.0"
)

app.include_router(router)

if __name__ == "__main__":
    # Use reload=True during development so that changes are automatically reloaded.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
