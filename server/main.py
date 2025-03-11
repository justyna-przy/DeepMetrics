import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.config import Config 
from routes import router  
from database.db import init_db

class Application:
    def __init__(self):
        self.config = Config()

        # Initialize the global DB
        init_db(self.config.db_url)

        self.app = FastAPI(
            title="DeepMetrics API",
            description="API for receiving snapshots from clients and sending data to frontend",
            version="1.0",
        )

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.server_settings.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.app.include_router(router)

    def run(self, host="0.0.0.0", port=8000, reload=False):
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            reload=reload,
            log_config=self.config.uvicorn_log_config
        )

if __name__ == "__main__":
    app = Application()
    app.run(reload=False)