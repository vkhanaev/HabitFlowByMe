import logging.config
from typing import Any

from app.config import get_settings


def get_logging_config() -> dict[str, Any]:
    settings = get_settings()

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "level": settings.log_level,
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "level": settings.log_level,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["default"],
                "level": "WARNING",
                "propagate": False,
            },
            "app": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["default"],
        },
    }


def setup_logging() -> None:
    logging.config.dictConfig(get_logging_config())
