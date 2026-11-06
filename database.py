from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
from  dotenv import load_dotenv
import os

DATABASE_URL = os.getenv(DB_URL)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

