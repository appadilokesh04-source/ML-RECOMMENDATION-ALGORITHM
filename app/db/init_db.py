import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),"../.."))

from app.db.database import engine, SessionLocal
from app.db.models import Base
from app.db.crud import save_movie
from app.data.loader import load_movies, get_genre_string


def init():
    print("Creating tables..")
    Base.metadata.create_all(bind=engine)  # <-- this was missing
    
    db = SessionLocal()
    try:
        movies = get_genre_string(load_movies())
        print(f"Seeding {len(movies)} movies...")
        
        for _, row in movies.iterrows():
            save_movie(
                db=db,
                movie_id=int(row["movie_id"]),
                title=row["title"],
                genres=row["genres"]
            )
        print("Movies seeded!")
    finally:
        db.close()


if __name__ == "__main__":
    init()