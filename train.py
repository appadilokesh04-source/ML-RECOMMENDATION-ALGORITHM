import sys
import os
import urllib.request
import zipfile

sys.path.append("/app")

# Download MovieLens dataset if not present
DATA_DIR = "/app/app/data/ml-100k/ml-100k"
if not os.path.exists(DATA_DIR):
    print("Downloading MovieLens dataset...")
    url = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
    urllib.request.urlretrieve(url, "/tmp/ml-100k.zip")
    
    # Extract
    with zipfile.ZipFile("/tmp/ml-100k.zip", "r") as z:
        z.extractall("/app/app/data/ml-100k/")
    print("✅ Dataset downloaded!")

from app.ml.hybrid import HybridEngine
engine = HybridEngine()
engine.train()
print("✅ Models trained and saved!")