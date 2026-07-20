from fastapi import APIRouter

from app.web.auth import router as auth_router
from app.web.habits import router as habits_router

web_router = APIRouter()

web_router.include_router(auth_router)
web_router.include_router(habits_router)
