import os
import joblib
import pandas as pd
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import accuracy

# Where we save the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../saved_models/svd_model.pkl")

class SVDModel:
    """
    Wraps scikit-surprise SVD model.
    Handles training, prediction, and saving/loading.
    """

    def __init__(self, n_factors=100, n_epochs=20):
        """
        n_factors = number of hidden features (latent factors)
        n_epochs  = how many times to loop through data during training
        """
        self.model = SVD(n_factors=n_factors, n_epochs=n_epochs, verbose=True)
        self.trainset = None   # full training data
        self.is_trained = False

    def train(self, ratings_df: pd.DataFrame):
        """
        Train SVD on ratings dataframe.
        ratings_df must have columns: user_id, movie_id, rating
        """
        print("Training SVD model...")

        # Step 1 — tell surprise our rating scale is 1 to 5
        reader = Reader(rating_scale=(1, 5))

        # Step 2 — load dataframe into surprise's format
        data = Dataset.load_from_df(
            ratings_df[["user_id", "movie_id", "rating"]],
            reader
        )

        # Step 3 — split into train (80%) and test (20%)
        trainset, testset = train_test_split(data, test_size=0.2, random_state=42)
        self.trainset = trainset

        # Step 4 — train the model
        self.model.fit(trainset)
        self.is_trained = True

        # Step 5 — evaluate on test set (lower RMSE = better)
        predictions = self.model.test(testset)
        rmse = accuracy.rmse(predictions)
        print(f" SVD trained! RMSE: {rmse:.4f}")
        return rmse

    def predict_rating(self, user_id: int, movie_id: int) -> float:
        """
        Predict what rating a user would give a movie.
        Returns a float between 1.0 and 5.0
        """
        if not self.is_trained:
            raise Exception("Model not trained yet! Call train() first.")

        prediction = self.model.predict(uid=str(user_id), iid=str(movie_id))
        return round(prediction.est, 2)  # .est = estimated rating

    def recommend_movies(self, user_id: int, all_movie_ids: list, 
                          rated_movie_ids: set, top_n: int = 10) -> list:
        """
        Recommend top N movies for a user.
        Skips movies the user has already rated.

        Returns list of (movie_id, predicted_rating) sorted by rating descending
        """
        if not self.is_trained:
            raise Exception("Model not trained yet! Call train() first.")

        predictions = []

        for movie_id in all_movie_ids:
            # Skip already rated movies
            if movie_id in rated_movie_ids:
                continue

            pred = self.model.predict(uid=str(user_id), iid=str(movie_id))
            predictions.append((movie_id, round(pred.est, 2)))

        # Sort by predicted rating, highest first
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:top_n]

    def save(self):
        """Save trained model to disk using joblib"""
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)
        print(f" Model saved to {MODEL_PATH}")

    def load(self):
        """Load trained model from disk"""
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("No saved model found. Train first!")
        self.model = joblib.load(MODEL_PATH)
        self.is_trained = True
        print(" Model loaded from disk")


# ── Quick test ──
if __name__ == "__main__":
    # Import our loader from Day 1
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
    from app.data.loader import load_ratings, load_movies

    # Load data
    ratings = load_ratings()
    movies  = load_movies()

    all_movie_ids  = movies["movie_id"].tolist()

    # Train model
    svd = SVDModel(n_factors=100, n_epochs=20)
    svd.train(ratings)

    # Test prediction — what would user 1 rate movie 50?
    pred = svd.predict_rating(user_id=1, movie_id=50)
    print(f"\nPredicted rating for User 1 → Movie 50: {pred}")

    # Test recommendations — top 10 for user 1
    rated_by_user1 = set(ratings[ratings["user_id"] == 1]["movie_id"].tolist())
    recommendations = svd.recommend_movies(
        user_id=1,
        all_movie_ids=all_movie_ids,
        rated_movie_ids=rated_by_user1,
        top_n=10
    )

    print("\nTop 10 recommendations for User 1:")
    for movie_id, score in recommendations:
        title = movies[movies["movie_id"] == movie_id]["title"].values[0]
        print(f"  {title:<40} → predicted rating: {score}")

    # Save model
    svd.save()