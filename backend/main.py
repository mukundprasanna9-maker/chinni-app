from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.repositories.database import init_db
from backend.api.students import router as students_router
from backend.api.tracks import router as tracks_router
from backend.api.tests import router as tests_router
from backend.api.plans import router as plans_router
from backend.api.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
    except Exception as e:
        print(f"[Startup Warning] DB init encountered: {e}")
    yield


app = FastAPI(
    title="Cadence API (chinni-app)",
    description="Backend API for Study Rhythm, Test Score Tracking, and Analytics",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(students_router)
app.include_router(tracks_router)
app.include_router(tests_router)
app.include_router(plans_router)
app.include_router(analytics_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": "chinni-app",
        "service": "Cadence API",
        "version": "1.0.0",
    }
