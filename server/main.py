import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.config import Config

# 2. Create and load the config
config = Config()  # or whatever filename/path you like

from routes import router

# 4. Build the FastAPI app
app = FastAPI(
    title="DeepMetrics API",
    description="API for receiving snapshots from clients",
    version="1.0",
)

# 5. Apply CORS from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.server_settings.allowed_origins,  # or ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. Include your router
app.include_router(router)

if __name__ == "__main__":
    # 7. Run Uvicorn, telling it not to override our logging config
    logger.info("Starting server on 0.0.0.0:8000...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=config.uvicorn_log_config  
    )
