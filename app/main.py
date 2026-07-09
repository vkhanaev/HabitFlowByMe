from fastapi import FastAPI

from app.api.router import router
from app.config import get_settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title=get_settings().app_name)

app.include_router(router)
