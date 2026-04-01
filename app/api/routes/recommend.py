from fastapi import APIRouter,HTTPException,Query
from app.models.schemas import(
    
    RecommendationResponse,
    RecommendationItem,
    SimilarMoviesResponse,
    MovieResponse,
    RatingRequest
)
from app.db.redis_cache import (
    get_cached_recommendations,
    set_cached_recommendations,
    invalidate_user_cache
)


router=APIRouter()
@router.get("/recommend/{user_id}",response_model=RecommendationResponse)
def get_recommendations(
    user_id : int,
    top_n: int = Query(default=10,ge=1,le=50) #ge=min,le=mx
    
):
    """ Get top n movie recommendations for a user.
    -known user=hybrid(Svd+content)
    new user=content based only"""
    
    from app.main import engine
    cached=get_cached_recommendations(user_id)
    if cached:
        return RecommendationResponse(
            user_id=user_id,
            recommendations=[RecommendationItem(**r) for r in cached],
            total=len(cached)
        )
    
    try:
        recs=engine.recommend(user_id=user_id,top_n=top_n)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    set_cached_recommendations(user_id,recs)
    
    return RecommendationResponse(
        user_id=user_id,
        recommendations=[RecommendationItem(**r) for r in recs],
        total=len(recs)
    )
    
@router.get("/similar/{movie_id}",response_model=SimilarMoviesResponse)
def get_similar_movies(movie_id:int,top_n:int=Query(default=10,ge=1,le=50)):
    """ Get movies similar to given movie"""
    from app.main import engine
    row=engine.movies_df[engine.movies_df["movie_id"]==movie_id]
    if row.empty:
        raise HTTPException(status_code=404,detail=f"Movie{movie_id} not found")
    
    try:
        similar=engine.content_model.get_similar_movies(movie_id,top_n=top_n)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
    similar_list=[]
    for mid,score in similar:
        mrow=engine.movie_df[engine.movies_df["movie_id"]==mid]
        if not mrow.empty:
            similar_list.append(MovieResponse(
                movie_id=int(mid),
                title=mrow["title"].values[0],
                genres=mrow["genres"].values[0]
            ))
    return SimilarMoviesResponse(
        movie_id=movie_id,
        title=row["title"].values[0],
        Similar_movies=similar_list,
        total=len(similar_list)
    )
    
@router.post("/rate")
def rate_movie(request: RatingRequest):
    """Log a new user
    it adds to in memory dataframe"""
    from app.main import engine as ml_engine
    import pandas as pd
    if not(1.0<=request.rating<=5.0):
        raise HTTPException(status_code=400,detail="rating must be between 1 to 5")
    
    new_row={
        "user_id": request.user_id,
        "movie_id":request.movie_id,
        "rating":request.rating
    }    
    
    ml_engine.ratings_df=pd.concat(
        [ml_engine.ratings_df,pd.DataFrame([new_row])],
        ignore_index=True
    )
    
    invalidate_user_cache(request.user_id)
    return {
         "message": f"Rating saved! User {request.user_id} → Movie {request.movie_id} → {request.rating}"
    }
        
    