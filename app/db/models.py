from sqlalchemy import Column,Integer,String,Float,DateTime,func
from app.db.database import Base

class User(Base):
    __tablename__="users"
    
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String(100),unique=True,nullable=False)
    email=Column(String(200),unique=True,nullable=False)
    created_at=Column(DateTime,server_default=func.now())
    
class Movie(Base):
    __tablename__="movies"
    id=Column(Integer,primary_key=True,index=True)
    movie_id=Column(Integer,unique=True,nullable=False)
    title=Column(String(300),nullable=False)
    genres=Column(String(500))
    
class Rating(Base):
    __tablename__="ratings"
    
    id =Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,nullable=False)
    movie_id=Column(Integer,nullable=False)
    rating=Column(Float,nullable=False)
    created_at=Column(DateTime,server_default=func.now())
    
    
    