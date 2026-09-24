"""Bounded Stage 0 probes; stdlib only; no models or bulk season download."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import time
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'docs' / 'stage0_evidence'
OUT.mkdir(parents=True, exist_ok=True)
manifest = []

def fetch(name, url):
    path = OUT / (name + '.json')
    start = time.monotonic()
    run = subprocess.run(['curl', '-sS', '--max-time', '18', '-A', 'Mozilla/5.0', '-H', 'Referer: https://www.nba.com/', '-o', str(path), '-w', '%{http_code}', url], capture_output=True, text=True)
    record = dict(name=name, url=url, retrieved_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(), elapsed_seconds=round(time.monotonic()-start, 2), curl_exit=run.returncode, http_status=run.stdout, error=run.stderr.strip())
    if path.exists():
        raw = path.read_bytes()
        record.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        try:
            obj = json.loads(raw)
            record['valid_json'] = True
        except (ValueError, UnicodeError):
            obj = None
            record['valid_json'] = False
            path.rename(path.with_suffix('.txt'))
    else:
        obj = None
    manifest.append(record)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(record), flush=True)
    time.sleep(1)
    return obj

def stats(name, endpoint, params):
    return fetch(name, 'https://stats.nba.com/stats/' + endpoint + '?' + urlencode(params))

base = dict(Counter=0, DateFrom='10/24/2023', DateTo='10/25/2023', Direction='ASC', LeagueID='00', PlayerOrTeam='T', Season='2023-24', SeasonType='Regular Season', Sorter='DATE')
stats('leaguegamelog_2023_opening', 'leaguegamelog', base)
stats('teamgamelog_den_2023_opening', 'teamgamelog', dict(TeamID=1610612743, Season='2023-24', SeasonType='Regular Season', LeagueID='00', DateFrom='10/24/2023', DateTo='10/25/2023'))
dash = dict(LastNGames=0, Month=0, OpponentTeamID=0, PaceAdjust='N', PerMode='Totals', Period=0, PlusMinus='N', Rank='N', Season='2023-24', SeasonType='Regular Season', LeagueID='00', DateFrom='10/24/2023', DateTo='10/25/2023')
dash.update({k:'' for k in ['Conference','Division','GameScope','GameSegment','Location','Outcome','PORound','PlayerExperience','PlayerPosition','SeasonSegment','ShotClockRange','StarterBench','TeamID','TwoWay','VsConference','VsDivision']})
for measure in ['Advanced','Four Factors']:
    stats('teamstats_'+measure.replace(' ', '_').lower(), 'leaguedashteamstats', dict(dash, MeasureType=measure))
stats('scoreboard_2023_opening', 'scoreboardv2', dict(DayOffset=0, GameDate='10/24/2023', LeagueID='00'))
fetch('live_boxscore_0022300061', 'https://cdn.nba.com/static/json/liveData/boxscore/boxscore_0022300061.json')
fetch('live_playbyplay_0022300061', 'https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_0022300061.json')
