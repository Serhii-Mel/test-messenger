import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(64), index=True)
    username = Column(String(32))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Ініціалізація бази даних та створення таблиць"""
    if os.path.exists("./chat.db"):
        os.remove("./chat.db")  # Очистка старої БД (опціонально)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()