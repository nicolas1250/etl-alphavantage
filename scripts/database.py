import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def get_engine():
    """Crea engine SQLAlchemy para PostgreSQL"""
    url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)

engine = get_engine()

def test_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print(f'Conectado: {result.fetchone()[0]}')
