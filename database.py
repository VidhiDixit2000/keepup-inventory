import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Load variables from .env
#load_dotenv()

url = os.getenv("DATABASE_URL")
engine=create_engine(url)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

print("Database loaded successfully")