import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__),"../.."))
from app.ml.svd_model import SVDModel
from app.ml.content_model import ContentModel
from app.data.loader import load_ratings,load_movies,get_genre_string


class HybridEngine:
    """Combines SVD (collaborative) + Content-Based filtering.
    -Known user = SVD 70 % + content 30 %
    -New user = Content 100%(cold start fallback)
    """
    
    def __init__(self,svd_weight: float = 0.7,content_weight: float=0.3):
        self.svd_weight=svd_weight
        self.content_weight=content_weight
        self.svd_model=SVDModel()
        self.content_model=ContentModel()
        self.ratings_df=None
        self.movies_df=None
        
    def train(self):
        """Load data and train both models"""
        print("Training hybrid Engine..")
        self.ratings_df=load_ratings()
        self.movies_df=get_genre_string(load_movies())
        self.svd_model.train(self.ratings_df)
        print()
        self.content_model.train(self.movies_df)
        self.svd_model.save()
        self.content_model.save()    
        print("Hybrid Engine ready")
        
    def load(self):
        """ Load both pre-trained models from disk"""
        self.ratings_df=load_ratings()
        self.movies_df=get_genre_string(load_movies())
        self.svd_model.load()
        self.content_model.load()
        print("Hybrid Engine loaded from disk")
        
    def recommend(self,user_id:int,top_n: int = 10):
        """Main recommendation method.
        Return list of dicts:
        [
          { "movie_id": 50, "title": "Star Wars", "score": 4.82 },
        ]
        """
        #Gets all the movies that user has already rated
        user_ratings = self.ratings_df[self.ratings_df["user_id"] == user_id]
        rated_ods=set(user_ratings["movie_id"].tolist())
        all_ids=self.movies_df["movie_id"].tolist()
        
        
        if len(rated_ods)==0:
            
            print(f"User {user_id} has no atings using content-based")
            #Recommend top genres from popular movies
            popular_ids=self._get_popular_movie_ids(top_n=5)
            recs=self.content_model.recommend_for_user(
                liked_movie_ids=popular_ids,
                rated_movie_ids=rated_ods,
                top_n=top_n
                
            )
            return self._format_results(recs,score_type="content")
        
        liked_ids=set(
            user_ratings[user_ratings["rating"]>=4]["movie_id"].tolist()
            
        )
        svd_scores=self.svd_model.recommend_movies(
            user_id=user_id,
            all_movie_ids=all_ids,
            rated_movie_ids=rated_ods,
            top_n=100#get top 100 candiates from svd
        )
        
        #Convert Svd scores to dict:{movie_id: normalized_score}
        svd_dict={
            mid:(score-1)/4
            for mid,score in svd_scores
        }
        
        content_recs=self.content_model.recommend_for_user(
            liked_movie_ids=list(liked_ids),
            rated_movie_ids=rated_ods,
            top_n=100
        )
        #Normailize content scores 0-1
        max_content=max((s for _,s in content_recs),default=1)
        content_dict={
            mid: score / max_content
            for mid, score in content_recs
        }
        #combines scores
        all_candiates=set(svd_dict.keys()) | set(content_dict.keys())
        hybrid_scores={}
        
        for mid in all_candiates:
            svd_s = svd_dict.get(mid,0)
            content_s=content_dict.get(mid,0)
            hybrid_scores[mid]=(
                self.svd_weight * svd_s +
                self.content_weight * content_s 
                
            )
            
        sorted_recs=sorted(
            hybrid_scores.items(),
            key=lambda x : x[1],
            reverse=True
            
        )[:top_n]
        return self._format_results(sorted_recs,score_type="hybrid")
    
    def _get_popular_movie_ids(self,top_n: int=5):
        """Return most rated movie Ids (used for cold start)"""
        popular=(
            self.ratings_df.groupby("movie_id")
            .size()
            .sort_values(ascending=False)
            .head(top_n)
            .index.tolist()
        )
        return popular
    
    def _format_results(self,recs: list ,score_type:str):
        """Convert (movie_id,score) list into rich dicts with title."""
        results=[]
        for movie_id,score in recs:
            row=self.movies_df[self.movies_df["movie_id"]==movie_id]
            if row.empty:
                continue
            results.append({
                "movie_id": int(movie_id),
                "title": row["title"].values[0],
                "score": round(float(score),4),
                "score_type": score_type
            })
        return results
    
if __name__=="__mainn__":
    
    engine=HybridEngine()
       

    # Check if models already saved → load, else train
    if os.path.exists("saved_models/svd_model.pkl") and \
       os.path.exists("saved_models/content_model.pkl"):
        engine.load()
    else:
        engine.train()

    # Test 1 — known user
    print("\n Top 10 recommendations for User 1:")
    recs = engine.recommend(user_id=1, top_n=10)
    for i, r in enumerate(recs, 1):
        print(f"  {i:>2}. {r['title']:<45} score: {r['score']}")

    # Test 2 — another user
    print("\n Top 10 recommendations for User 50:")
    recs = engine.recommend(user_id=50, top_n=10)
    for i, r in enumerate(recs, 1):
        print(f"  {i:>2}. {r['title']:<45} score: {r['score']}")

    # Test 3 — new user (no ratings)
    print("\n Recommendations for NEW user (id=9999):")
    recs = engine.recommend(user_id=9999, top_n=5)
    for i, r in enumerate(recs, 1):
        print(f" {i:>2}. {r['title']:<45} score:{r['score']}")