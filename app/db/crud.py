from sqlalchemy.orm import Session
from app.db.models import Rating, Movie, User


def save_rating(db: Session, user_id: int, movie_id: int, rating: float):
    """Save a new rating to the database"""
    new_rating = Rating(
        user_id=user_id,
        movie_id=movie_id,
        rating=rating
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating


def get_user_ratings(db: Session, user_id: int):
    """Get all ratings by a specific user"""
    return db.query(Rating).filter(Rating.user_id == user_id).all()


def get_movie(db: Session, movie_id: int):
    """Get a movie by its MovieLens ID"""
    return db.query(Movie).filter(Movie.movie_id == movie_id).first()


def save_movie(db: Session, movie_id: int, title: str, genres: str):
    """Save a movie to the database (used during seeding)"""
    existing = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if existing:
        return existing 
    
    movie = Movie(movie_id=movie_id, title=title, genres=genres)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def get_all_ratings(db: Session):
    """Get all ratings (used to reload model with latest data)"""
    return db.query(Rating).all()