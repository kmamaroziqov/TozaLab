from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from sqlalchemy import Column, Integer, String
from dotenv import load_dotenv
load_dotenv()

# Create the engine
engine = create_engine(os.getenv("DATABASE_URL"))

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestTable(Base):
    __tablename__ = "test_table"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

# Create all tables
Base.metadata.create_all(bind=engine)