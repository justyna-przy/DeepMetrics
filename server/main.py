from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

app = FastAPI(
    title="DeepMetrics API",
    description="API for receiving snapshots from clients",
    version="1.0",
)

# List all the origins you allow (e.g., your React dev server address).
# Use ["*"] to allow all, but more restrictive is better for production.
origins = [
    "http://localhost:3001",
    "http://localhost:3000",
    "http://127.0.0.1:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # or ["*"]
    allow_credentials=True,
    allow_methods=["*"],        # or specific methods like ["GET", "POST"]
    allow_headers=["*"],        # or specific headers
)

app.include_router(router)

if __name__ == "__main__":
    # Use reload=True during development so that changes are automatically reloaded.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
