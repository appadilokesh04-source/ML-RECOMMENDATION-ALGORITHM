import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(__file__),"ml-100k/ml-100k")
print("lokking for data at:",DATA_PATH)

def load_ratings() -> pd.DataFrame:
    cols = ["user_id", "movie_id", "rating", "timestamp"]
    df = pd.read_csv(
        os.path.join(DATA_PATH, "u.data"),
        sep="\t",
        names=cols,
        encoding="latin-1"
    )
    df.drop(columns=["timestamp"], inplace=True)
    return df


def load_movies() -> pd.DataFrame:
    genre_cols = [
        "unknown", "Action", "Adventure", "Animation", "Children",
        "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
        "Film-Noir", "Horror", "Musical", "Mystery", "Romance",
        "Sci-Fi", "Thriller", "War", "Western"
    ]
    cols = ["movie_id", "title", "release_date", "video_release_date", "imdb_url"] + genre_cols
    df = pd.read_csv(
        os.path.join(DATA_PATH, "u.item"),
        sep="|",
        names=cols,
        encoding="latin-1"
    )
    df = df[["movie_id", "title"] + genre_cols]
    return df


def load_users() -> pd.DataFrame:
    cols = ["user_id", "age", "gender", "occupation", "zip_code"]
    df = pd.read_csv(
        os.path.join(DATA_PATH, "u.user"),
        sep="|",
        names=cols,
        encoding="latin-1"
    )
    return df


def get_genre_string(movies_df: pd.DataFrame) -> pd.DataFrame:
    genre_cols = [
        "unknown", "Action", "Adventure", "Animation", "Children",
        "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
        "Film-Noir", "Horror", "Musical", "Mystery", "Romance",
        "Sci-Fi", "Thriller", "War", "Western"
    ]
    movies_df["genres"] = movies_df[genre_cols].apply(
        lambda row: " ".join([genre for genre, val in row.items() if val == 1]),
        axis=1
    )
    return movies_df[["movie_id", "title", "genres"]]


if __name__ == "__main__":
    ratings = load_ratings()
    movies = load_movies()
    users = load_users()
    movies = get_genre_string(movies)

    print("=== RATINGS ===")
    print(ratings.head())
    print(f"Shape: {ratings.shape}")

    print("\n=== MOVIES ===")
    print(movies.head())
    print(f"Shape: {movies.shape}")

    print("\n=== USERS ===")
    print(users.head())
    print(f"Shape: {users.shape}")