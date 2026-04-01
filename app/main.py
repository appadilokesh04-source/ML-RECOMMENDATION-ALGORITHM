import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI

sys.path.append(os.path.join(os.path.dirname(__file__),".."))
from app.ml.hybrid import HybridEngine
from app.api.routes import health,movies,recommend

#global engine instance - shared across all routes
engine=HybridEngine()
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load Ml modles once when server starts.Never reload on each request-too slow!"""
    print("Starting Movie recommender API...")
    if os.path.exists("saved_models/svd_model.pkl") and \
        os.path.exists("saved_models/content_model.pkl"):
            engine.load()
    else:
        print("No saved models found.")
        engine.train()
    print("Models Loaded.Api ready")
    yield
    print("Shutting down")
        
app=FastAPI(
    title="Movie REcommender API",
    description="Hybrid Ml recommendation engine(Svd + Content-Based)",
    version="1.0.0",
    lifespan=lifespan
)

#register all routers
app.include_router(health.router,tags=["Health"])
app.include_router(movies.router,tags=["Movies"])
app.include_router(recommend.router,tags=["Recommendations"])

@app.get("/")
def root():
    return {
        "message":  " Movie Recommender API",
        "docs":     "/docs",
        "version":  "1.0.0"
        
    }
        
        
    