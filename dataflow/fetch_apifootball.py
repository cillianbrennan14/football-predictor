import requests
from typing import Dict, Any, List
from core.config import settings

BASE = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": settings.APIFOOTBALL_KEY}

def _get(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.get(f"{BASE}/{path}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def get_fixtures(league_id: int, season: int):
    return {
        "upcoming": _get("fixtures", {"league": league_id, "season": season, "next": 200}),
        "recent": _get("fixtures", {"league": league_id, "season": season, "last": 400}),
    }

def get_lineups_and_stats(fixture_ids: List[int]):
    out = {}
    chunk = 20
    for i in range(0, len(fixture_ids), chunk):
        ids = ",".join(str(x) for x in fixture_ids[i:i+chunk])
        out.setdefault("events", []).append(_get("fixtures/events", {"ids": ids}))
        out.setdefault("lineups", []).append(_get("fixtures/lineups", {"ids": ids}))
        out.setdefault("statistics", []).append(_get("fixtures/statistics", {"ids": ids}))
        out.setdefault("players", []).append(_get("fixtures/players", {"ids": ids}))
    return out

def get_teams(league_id: int, season: int):
    return _get("teams", {"league": league_id, "season": season})
