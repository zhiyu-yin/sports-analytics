"""Targeted historical evidence only; cache bodies stay ignored and checksummed."""
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
import hashlib,json,time
from injury_warning.pilot_io import ROOT,now
from .io import D
SOURCES={
'p2b_strawther_return':('2024-02-09','https://gazette.com/2024/02/09/julian-strawther-is-back-from-injury-but-michael-malone-says-nuggets-plan-to-stick-with-jamal-murray-led-second-unit/'),
'p2b_cissoko_serial':('2024-01-23','https://www.foxsports.com/nba/sidy-cissoko-2-player?p=4'),
'p2b_strawther_jan29':('2024-01-29','https://www.nba.com/nuggets/news/nuggets-and-bucks-play-in-battle-of-two-title-contenders'),
'p2b_strawther_assignment':('2024-02-04','https://www.nba.com/nuggets/news/nuggets-play-trail-blazers-for-second-time-in-three-days'),
'p2b_knox_waiver':('2024-02-09','https://www.nba.com/jazz/news/utah-jazz-waive-kevin-knox-ii'),
'p2b_korkmaz_waiver':('2024-02-09','https://www.nba.com/pacers/news/indiana-pacers-waive-furkan-korkmaz'),
'p2b_nance_10day':('2024-01-18','https://gleague.nba.com/news/cavaliers-sign-pete-nance-to-10-day-contract'),
'p2b_nance_2way':('2024-02-19','https://www.nba.com/cavaliers/news/releases-pete-nance-two-way-240219'),
'p2b_diakite_sign':('2024-01-01','https://www.nba.com/spurs/news/spurs-sign-mamadi-diakite-to-two-way-contract'),
'p2b_stewart_suspension':('2024-02-22','https://www.nba.com/news/pistons-isaiah-stewart-suspension'),
'p2b_morris_contract':('2024-03-18','https://www.nba.com/news/cleveland-cavaliers-marcus-morris-10-day-contract'),
'p2b_hayes_waiver':('2024-02-08','https://www.nba.com/pistons/news/detroit-pistons-request-waivers-on-killian-hayes-joe-harris-and-danuel-house-jr')}
def fetch(item):
 sid,(day,url)=item;r=dict(source_id=sid,date=day,url=url,retrieved_at=now(),role='C_targeted_review_only; not historical predictor publication')
 try:
  with urlopen(Request(url,headers={'User-Agent':'NBAInjuryFeasibilityResearch/0.1'}),timeout=25) as f:b=f.read(12000001)
  assert len(b)<=12000000;h=hashlib.sha256(b).hexdigest();p=ROOT/'data/raw/phase2b'/f'{h}.html';p.parent.mkdir(exist_ok=True);p.write_bytes(b);r.update(status='obtained',sha256=h,raw_file=str(p.relative_to(ROOT)),bytes=len(b))
 except Exception as e:r.update(status='failed',error=str(e))
 return r
def acquire():
 p=D/'source_manifest.json';old=json.loads(p.read_text()) if p.exists() else [];seen={r['source_id'] for r in old}
 with ThreadPoolExecutor(max_workers=5) as pool:old+=list(pool.map(fetch,[r for r in SOURCES.items() if r[0] not in seen]))
 p.write_text(json.dumps(old,indent=2)+'\n');print([(r['source_id'],r['status']) for r in old])
if __name__=='__main__':acquire()
