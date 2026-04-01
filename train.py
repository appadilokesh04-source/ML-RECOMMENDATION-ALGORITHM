import sys
sys.path.append("/app")

from app.ml.hybrid import HybridEngine

engine = HybridEngine()
engine.train()
print(" Models trained and saved!")