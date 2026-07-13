from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.router import router
from app.core.config import get_settings
from app.core.lifespan import lifespan

app = FastAPI(title=get_settings().app_name, lifespan=lifespan)

register_exception_handlers(app)

app.include_router(router)
