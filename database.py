import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

dbname = 'users.db'
engine = create_engine('sqlite:///' + dbname)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_db():
    Base.metadata.create_all(bind=engine)

def clear_db():
    Base.metadata.clear()

def drop_db():
    Base.metadata.drop_all(bind=engine)

def get_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

