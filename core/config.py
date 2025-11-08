import os
from pydantic import BaseModel

class Settings(BaseModel):
    APIFOOTBALL_KEY: str = os.getenv("APIFOOTBALL_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    EPL_LEAGUE_ID: int = int(os.getenv("EPL_LEAGUE_ID", 39))
    UCL_LEAGUE_ID: int = int(os.getenv("UCL_LEAGUE_ID", 2))
    CURRENT_SEASON: int = int(os.getenv("CURRENT_SEASON", 2025))

settings = Settings()
assert settings.APIFOOTBALL_KEY, "Missing APIFOOTBALL_KEY"
assert settings.DATABASE_URL, "Missing DATABASE_URL"
