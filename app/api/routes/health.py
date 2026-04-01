from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.db.redis_cache import cache_health
router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Check if the API and ML model are running"""
    from app.main import engine
    redis_ok=cache_health()
    return HealthResponse(
        status="ok" if redis_ok else "degraded",
        model_loaded=engine.svd_model.is_trained,
        message="REdis connected "if redis_ok else "Redis not connected"
    )