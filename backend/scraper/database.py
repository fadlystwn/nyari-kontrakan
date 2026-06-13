import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_user = os.getenv("POSTGRES_USER", "scraper_user")
    db_pass = os.getenv("POSTGRES_PASSWORD", "change_this_to_a_strong_password")
    db_name = os.getenv("POSTGRES_DB", "scraper_db")
    DATABASE_URL = f"postgresql://{db_user}:{db_pass}@localhost:5432/{db_name}"

async def get_db_connection():
    """
    Establish and return a connection to the PostgreSQL database using asyncpg.
    """
    return await asyncpg.connect(DATABASE_URL)
