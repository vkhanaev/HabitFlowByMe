from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.exception_handlers import register_exception_handlers
from app.api.router import router as api_router
from app.core.config import get_settings
from app.core.lifespan import lifespan
from app.web.router import web_router

app = FastAPI(title=get_settings().app_name, lifespan=lifespan)

# Статика
app.mount("/static", StaticFiles(directory="static"), name="static")

register_exception_handlers(app)

app.include_router(web_router)  # HTML-интерфейс
app.include_router(api_router)  # JSON API для Swagger/мобильных приложений
