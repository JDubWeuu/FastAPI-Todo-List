from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Intialize the database
SQLALCHEMY_DATABASE_URL = "sqlite:///./mydatabase.db" 
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ToDoItem(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    # With default keyword, it allows the user to not have to input something, and we can assign it to a default value
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ToDoItemCreate(BaseModel):
    title: str = ""
    description: str = ""
    completed: Optional[bool] = False

class ToDoItemResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at = datetime

    class Config:
        orm_mode = True