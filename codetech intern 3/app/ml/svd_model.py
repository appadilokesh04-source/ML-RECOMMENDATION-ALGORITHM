import os
import joblib
import pandas as pd
from surprise import svd,dataset,reader
from suprise.model_selection import train_test_split
from surprise import accuracy

MODEL_PATH=os.path.join(os.path.dirname(__file__), "../../saved_models/svd_model.pkl")

class SVDModel:
    
    def __init__(self,n_factors=100,n_epochs=20):
        self.model=SVD(n_factors=n_factors,n_epochs=n_epochs,verbose=True)
        self.trainset=None
        self.is_trained=False
        
    
    def train(self,ratings_df:pd.DataFrame):
        
        print("Training SVD model..")
        reader=reader(rating_scale=(1,5))
        
        data=dataset.load_from_df(
            ratings_df[["user_id","movie_id","rating"]],
            reader
            
        )
                    
        self.trainset,testset=train_test_split(data,test_size=0.2,random_state=42)
        self.trainset=self.trainset
        
        self.model.fit(trainset)
        self.is_trained=True
        
        predictions=self.model.test(testset)
        print(f"SVD trained! RMSE: {rmse:.4f}")
        return rmse
    
    def predict_rating(self,user_id: int,movie_id: int):
        
        