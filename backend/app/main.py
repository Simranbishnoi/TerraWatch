from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import (
    health,
    farms,
    analysis,
    reports,
    auth
)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)


@app.get("/")
def root():
    return {
        "message": "TerraWatch API is running"
    }


app.include_router(
    health.router,
    prefix="/api/health",
    tags=["Health"]
)

app.include_router(
    farms.router,
    prefix="/api/farms",
    tags=["Farms"]
)

app.include_router(
    analysis.router,
    prefix="/api/analysis",
    tags=["Analysis"]
)

app.include_router(
    reports.router,
    prefix="/api/reports",
    tags=["Reports"]
)

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)