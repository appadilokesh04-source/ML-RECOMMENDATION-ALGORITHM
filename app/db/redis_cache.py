import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL=os.getenv("REDIS_URL","redis://localhost:6379")#Create Redis client

CACHE_TTL=3600#Cache expiry-1hr

def get_cached_recommendations(user_id: int):
    """Try to get recommendations from cache.Returns list of dicts if found,none if not cached"""
    key=f"recommend:user:{user_id}"
    try:
        data=client.get(key)
        if data:
            print(f"Cache HIT for user {user_id}")
            return json.loads(data)
        print(f"Cache MISS for user {user_id}")
        return None
    except Exception as e:
        #if redis down ,dont crash
        print(f"Redis error:{e}")
        return None
    
def set_cached_recommendations(user_id: int,recommendations: list):
    """Save recommendations to cache,expires automatically after CACHE_TTL seconds"""
    
    key=f"recommend:user:{user_id}"
    try:
        client.setex(
            name=key,
            time=CACHE_TTL,
            value=json.dumps(recommendations)#serializes python lists to json
            
        )
        print(f"Cached recommendations for user {user_id} (TTL: {CACHE_TTL})")
    except Exception as e:
        print(f"Redis error: {e}")
        
def invalidate_user_cache(user_id: int):
    """Delete cached recommendatikns when user adds a new rating.
    Forces fresh recommendations on next request"""
    key=f"recommend:user:{user_id}"
    try:
        client.delete(key)
        print(f" Cache invalidated for user {user_id}")
    except Exception as e:
        print(f" Redis error: {e}")
        
        
def cache_health():
    """Check if redis is reachable"""
    try:
        client.ping()
        return True
    except Exception:
        return False
     
    
        
        

