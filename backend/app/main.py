from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import observe, trace, detect, respond, audit, simulator, system
from app.services.scenario_generator import ScenarioGenerator
from app.services.evaluation_service import EvaluationService

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure baseline synthetic dataset exists
    db = SessionLocal()
    try:
        from app.models.entities import Account
        count = db.query(Account).count()
        if count == 0:
            print("Seeding initial synthetic multi-bank financial network...")
            ScenarioGenerator.generate_full_seeded_dataset(db, total_accounts=1500, total_transactions=30000, seed=42)
            print("Dataset seeded successfully.")
            # Run initial model training & benchmark
            print("Training Isolation Forest and GraphSAGE models...")
            EvaluationService.train_models_if_needed(db)
            print("Models initialized.")
    except Exception as e:
        print(f"Startup initialization notice: {e}")
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    description="Unified Financial Investigation · Eight Algorithmic Engines · Original UI · End-to-End Evidence"
)

# CORS middleware for local frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(observe.router, prefix=settings.API_V1_PREFIX)
app.include_router(trace.router, prefix=settings.API_V1_PREFIX)
app.include_router(detect.router, prefix=settings.API_V1_PREFIX)
app.include_router(respond.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit.router, prefix=settings.API_V1_PREFIX)
app.include_router(simulator.router, prefix=settings.API_V1_PREFIX)
app.include_router(system.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "project": "MULE MATRIX",
        "description": "Unified Financial Investigation & Multi-Engine Detection Platform",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

