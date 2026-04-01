from fastapi import APIRouter,HTTPException
from typing import List
from app.models.schemas import MovieResponse

router=APIRouter()

@router.get("/movies",response_model=List[MovieResponse])
def get_all_movies():
    """Return all movies in the dataset"""
    from app.main import engine
    movies=engine.movies_df[["movie_id","title","genres"]]
    return movies.to_dict(orient="records")

@router.get("/movies/{movie_id}",response_model=MovieResponse)
def get_movie(movie_id: int):
    """ GEt a single movie by ID"""
    from app.main import engine
    row=engine.movies_df[engine.movies_df["movie_id"]==movie_id]
    if row.empty:
        raise HTTPException(status_code=404,detail=f"Movie{movie_id}not found")
    return row.iloc[0].to_dict()