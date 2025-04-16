from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DATABASE_NAME = os.getenv("DB_NAME")

# Optional: Add a debug print to verify values (remove in production)
print(f"DB config - USERNAME: {USERNAME}, HOST: {HOST}, PORT: {PORT}")

if None in [USERNAME, PASSWORD, HOST, PORT, DATABASE_NAME]:
    raise ValueError("Missing one or more environment variables for database connection.")


DATABASE_URL = f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()