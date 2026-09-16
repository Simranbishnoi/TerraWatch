from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.db import base

from app.api.routes import health, farms, analysis, reports, auth



app = FastAPI(
    title="TerraWatch API",
    description="Deforestation Monitoring and Verification Platform",
    version="1.0.0"
)

# CORS middleware configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



Base.metadata.create_all(bind=engine)



app.include_router(
    auth.router,
    tags=["Authentication"]
)

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

# Root-level aliases for direct frontend compatibility
app.include_router(
    farms.router,
    prefix="/farms",
    include_in_schema=False
)

app.include_router(
    reports.router,
    prefix="/reports",
    include_in_schema=False
)



@app.get("/")
def root():
    return {
        "message": "TerraWatch backend is running"
    }