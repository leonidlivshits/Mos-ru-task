from fastapi import FastAPI

from app.api.routes.demo import router as demo_router
from app.api.routes.health import router as health_router
from app.api.routes.lost_requests import router as lost_requests_router
from app.api.routes.stations import router as stations_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(health_router)
    app.include_router(stations_router)
    app.include_router(lost_requests_router)
    app.include_router(demo_router)
    return app


app = create_app()
