from sqlalchemy import create_engine, text
from core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

def init_schema():
    with engine.begin() as conn:
        conn.execute(text(open("sql/schema.sql","r",encoding="utf-8").read()))
