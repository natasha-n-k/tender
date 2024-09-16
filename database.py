from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from models import Base

DATABASE_URL = os.getenv('POSTGRES_CONN', 'postgresql://postgres:1234@localhost:5432/postgres')

engine = create_engine(DATABASE_URL)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def init_db():
    from models import User, Organization, Tender, Bid, OrganizationResponsible  # Import all models here
    Base.metadata.create_all(bind=engine)  # Create tables

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
