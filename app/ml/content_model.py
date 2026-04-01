import os
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../saved_models/content_model.pkl")

class ContentModel:
    """
    Content-based filtering using TF-IDF on movie genres.
    Finds movies similar to ones a user already liked.
    """

    def __init__(self):
        self.vectorizer   = TfidfVectorizer()
        self.tfidf_matrix = None
        self.movies_df    = None
        self.is_trained   = False

    def train(self, movies_df: pd.DataFrame):
        """
        Build TF-IDF matrix from movie genres.
        movies_df must have columns: movie_id, title, genres
        """
        print("Building Content model...")
        self.movies_df    = movies_df.reset_index(drop=True)
        genres            = self.movies_df["genres"].fillna("")
        self.tfidf_matrix = self.vectorizer.fit_transform(genres)
        self.is_trained   = True
        print(f" Content model built!")
        print(f"   Movies: {self.tfidf_matrix.shape[0]}")
        print(f"   Genre features: {self.tfidf_matrix.shape[1]}")

    def get_similar_movies(self, movie_id: int, top_n: int = 10) -> list:
       
        """
        Find top N movies similar to a given movie.
        Returns list of (movie_id, similarity_score)
        """
        if not self.is_trained:
            raise Exception("Model not trained yet! Call train() first.")

        
        matches = self.movies_df[self.movies_df["movie_id"] == movie_id]
        if matches.empty:
            raise ValueError(f"Movie ID {movie_id} not found!")

        movie_idx        = matches.index[0]
        movie_vector     = self.tfidf_matrix[movie_idx]
        similarity_scores = cosine_similarity(movie_vector, self.tfidf_matrix)
        similarity_scores = similarity_scores.flatten()
        sorted_indices   = np.argsort(similarity_scores)[::-1]

       
        results = []
        for idx in sorted_indices:
            mid = int(self.movies_df.iloc[idx]["movie_id"])
            if mid == movie_id:
                continue
           
            score = round(float(similarity_scores[idx]), 4)
            if score == 0.0:
                continue
            results.append((mid, score))
            if len(results) >= top_n:
                break

        
        return results

    
    def recommend_for_user(self, liked_movie_ids: list,
                            rated_movie_ids: set,
                            top_n: int = 10) -> list:
        """
        Recommend movies based on user's liked movies.
        liked_movie_ids = movies user rated 4 or 5
        rated_movie_ids = ALL movies user has rated (to exclude)
        """

        if not self.is_trained:
            raise Exception("Model not trained yet! Call train() first.")

        score_accumulator = {}

        for liked_id in liked_movie_ids:
            try:
                similar = self.get_similar_movies(liked_id, top_n=20)
                for movie_id, score in similar:
                    if movie_id not in rated_movie_ids:
                        score_accumulator[movie_id] = (
                            score_accumulator.get(movie_id, 0) + score
                        
                        )
            except ValueError:
                continue

        sorted_movies = sorted(
            score_accumulator.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_movies[:top_n]

    def save(self):
        """Save model to disk"""
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
        joblib.dump({
            "vectorizer":   self.vectorizer,
            "tfidf_matrix": self.tfidf_matrix,
            "movies_df":    self.movies_df
        }, MODEL_PATH)
        print(f" Content model saved!")

    def load(self):
        """Load model from disk"""
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("No saved content model. Train first!")
        data = joblib.load(MODEL_PATH)
        
        self.vectorizer   = data["vectorizer"]
        self.tfidf_matrix = data["tfidf_matrix"]
        self.movies_df    = data["movies_df"]
        self.is_trained   = True
        print(" Content model loaded!")



if __name__ == "__main__":
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
    from app.data.loader import load_movies, get_genre_string

    movies = load_movies()
    movies = get_genre_string(movies)

    model = ContentModel()
    model.train(movies)

    print("\n Movies similar to Toy Story (1995):")
    similar = model.get_similar_movies(movie_id=1, top_n=5)
    for mid, score in similar:
        title = movies[movies["movie_id"] == mid]["title"].values[0]
        print(f"  {title:<40} → similarity: {score}")

    print("\n Recommendations for user who liked movies 1, 50, 100:")
    liked = [1, 50, 100]
    rated = {1, 50, 100, 200, 300}
    recs  = model.recommend_for_user(liked, rated, top_n=5)
    for mid, score in recs:
        title = movies[movies["movie_id"] == mid]["title"].values[0]
        print(f"  {title:<40} → score: {round(score, 4)}")

    model.save()