from sqlalchemy import text
from core.db import engine
from core.config import settings
from dataflow.fetch_apifootball import get_fixtures, get_lineups_and_stats, get_teams

def upsert(conn, sql, rows):
    if not rows: return
    for row in rows:
        conn.execute(text(sql), row)

def run_fetch_and_load():
    with engine.begin() as conn:
        for league_id in [settings.EPL_LEAGUE_ID, settings.UCL_LEAGUE_ID]:
            teams = get_teams(league_id, settings.CURRENT_SEASON)["response"]
            upsert(conn,
                """insert into teams(team_id,name) values(:id,:name)
                   on conflict (team_id) do update set name=excluded.name""",
                [{"id": t["team"]["id"], "name": t["team"]["name"]} for t in teams])

            fx_payload = get_fixtures(league_id, settings.CURRENT_SEASON)
            def normalize_fixture(f):
                fix = f["fixture"]; lg=f["league"]; t=f["teams"]
                return {
                    "fixture_id": fix["id"],
                    "date_utc": fix["date"],
                    "league_id": lg["id"],
                    "season": lg["season"],
                    "home_id": t["home"]["id"],
                    "away_id": t["away"]["id"],
                    "venue": (fix["venue"] or {}).get("name"),
                    "referee": fix.get("referee"),
                    "status": fix["status"]["short"]
                }
            fixtures = [normalize_fixture(f) for f in fx_payload["upcoming"]["response"]] + \
                       [normalize_fixture(f) for f in fx_payload["recent"]["response"]]
            upsert(conn, """
                insert into fixtures(fixture_id,date_utc,league_id,season,home_id,away_id,venue,referee,status)
                values(:fixture_id,:date_utc,:league_id,:season,:home_id,:away_id,:venue,:referee,:status)
                on conflict (fixture_id) do update set
                  date_utc=excluded.date_utc, status=excluded.status, referee=excluded.referee, venue=excluded.venue
            """, fixtures)

            fixture_ids = [f["fixture_id"] for f in fixtures]
            bulk = get_lineups_and_stats(fixture_ids)

            for page in bulk["statistics"]:
                for item in page["response"]:
                    fid = item["fixture"]["id"]
                    for side in item["statistics"]:
                        team = side["team"]["id"]
                        def getv(key):
                            for stat in side["statistics"]:
                                if stat["type"].lower()==key: return stat["value"] or 0
                            return 0
                        row = {
                          "fixture_id": fid, "team_id": team,
                          "goals": getv("goals"), "xg": getv("expected goals") or getv("xg"),
                          "shots": getv("shots total"), "shots_on_target": getv("shots on target"),
                          "corners": getv("corners"), "cards_yellow": getv("yellow cards"),
                          "cards_red": getv("red cards"), "fouls": getv("fouls")
                        }
                        conn.execute(text("""
                          insert into team_stats(fixture_id,team_id,goals,xg,shots,shots_on_target,corners,cards_yellow,cards_red,fouls)
                          values(:fixture_id,:team_id,:goals,:xg,:shots,:shots_on_target,:corners,:cards_yellow,:cards_red,:fouls)
                          on conflict (fixture_id,team_id) do update set
                            goals=excluded.goals,xg=excluded.xg,shots=excluded.shots,shots_on_target=excluded.shots_on_target,
                            corners=excluded.corners,cards_yellow=excluded.cards_yellow,cards_red=excluded.cards_red,fouls=excluded.fouls
                        """), row)
