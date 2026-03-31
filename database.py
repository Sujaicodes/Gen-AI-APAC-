from sqlalchemy.orm import sessionmaker
from models import engine, Base, SessionLocal

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    return SessionLocal()