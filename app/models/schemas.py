from pydantic import BaseModel
from typing import List, Optional


class MovieResponse(BaseModel):
    movie_id: int
    title:    str
    genres:   Optional[str] = None



class RecommendationItem(BaseModel):
    movie_id:   int
    title:      str
    score:      float
    score_type: str


class RecommendationResponse(BaseModel):
    user_id:         int
    recommendations: List[RecommendationItem]
    total:           int


class SimilarMoviesResponse(BaseModel):
    movie_id:      int
    title:         str
    similar_movies: List[MovieResponse]   
    total:         int


class HealthResponse(BaseModel):
    status:       str
    model_loaded: bool
    message:      str


class RatingRequest(BaseModel):
    user_id:  int
    movie_id: int
    rating:   float
    
    