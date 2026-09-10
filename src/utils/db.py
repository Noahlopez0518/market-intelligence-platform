"""Supabase/Postgres connection helper, shared by ingestion scripts."""
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine() -> Engine:
    host = os.environ["SUPABASE_DB_HOST"]
    port = os.environ.get("SUPABASE_DB_PORT", "5432")
    name = os.environ.get("SUPABASE_DB_NAME", "postgres")
    user = os.environ["SUPABASE_DB_USER"]
    password = os.environ["SUPABASE_DB_PASSWORD"]
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
    return create_engine(url)
