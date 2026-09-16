from fastapi import FastAPI

from app.db.database import Base, engine
from app.db import base

from app.api.routes import health, farms, analysis, reports


app = FastAPI(
    title="TerraWatch API",
    description="Deforestation Monitoring and Verification Platform",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)


app.include_router(
    health.router,
    prefix="/api",
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


@app.get("/")
def root():
    return {
        "message": "TerraWatch backend is running"
    }