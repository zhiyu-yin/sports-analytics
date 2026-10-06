"""Anthropometric validation only. No outcome data or statistical fitting."""
import csv,json,hashlib,datetime,collections,subprocess,re
from pathlib import Path
from .normalize import number,inches,name_key,player_id
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'docs/stage0c_evidence'
RAW=ROOT/'data/raw/stage0c'
QUARANTINE={('1629655',2019),('1629672',2019),('1629023',2019),('1629675',2019)}
IDENTITY_COLUMNS=['player_id','player_name_nba','season']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def csvwrite(p,rows,fields=None):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def read_combine():
    m=json.loads((ROOT/'docs/stage0_evidence/archive_sources.json').read_text())[0]
    assert sha(ROOT/m['raw_path'])==m['sha256']
    import pyarrow as pa
    import pyarrow.csv as pc
    columns=['PLAYER_ID','PLAYER_NAME','SEASON','POSITION','HEIGHT_WO_SHOES','HEIGHT_WO_SHOES_FT_IN','HEIGHT_W_SHOES','HEIGHT_W_SHOES_FT_IN','WINGSPAN','WINGSPAN_FT_IN','STANDING_REACH','STANDING_REACH_FT_IN','WEIGHT']
    table=pc.read_csv(ROOT/m['raw_path'],convert_options=pc.ConvertOptions(include_columns=columns,column_types={c:pa.string() for c in columns}))
    return table.to_pylist(),m

def valid_id(value):
    try:return player_id(value)
    except (TypeError,ValueError):return None

def usable(r):
    h=number(r.get('HEIGHT_WO_SHOES'));w=number(r.get('WINGSPAN'))
    return valid_id(r.get('PLAYER_ID')) and h is not None and w is not None and 60<=h<=96 and 60<=w<=108 and (str(r['PLAYER_ID']),int(r['SEASON'])) not in QUARANTINE

def reference(rows,cutoff=2013):
    groups=collections.defaultdict(list)
    for r in rows:
        if int(r['SEASON'])<=cutoff and usable(r):groups[valid_id(r['PLAYER_ID'])].append(r)
    result=[]
    for pid,rs in sorted(groups.items(),key=lambda kv:int(kv[0])):
        year=max(int(r['SEASON']) for r in rs);latest=[r for r in rs if int(r['SEASON'])==year]
        if len(latest)!=1:raise ValueError('Duplicate latest record')
        result.append(latest[0])
    return result

def height_stratum(h):return 'short_lt75' if h<75 else 'medium_75_to_lt80' if h<80 else 'tall_ge80'
def era(y):return '2000-2004' if y<=2004 else '2005-2008' if y<=2008 else '2009-2013'
def sample(rows):
    groups=collections.defaultdict(list)
    for r in reference(rows):groups[(era(int(r['SEASON'])),height_stratum(float(r['HEIGHT_WO_SHOES'])))].append(r)
    selected=[];reserve=[]
    for (e,h),pool in sorted(groups.items()):
        pool.sort(key=lambda r:(float(r['WINGSPAN'])-float(r['HEIGHT_WO_SHOES']),int(r['SEASON']),r['PLAYER_NAME'],int(r['PLAYER_ID'])))
        picks={round(q*(len(pool)-1)) for q in [.1,.35,.5,.65,.9]}
        assert len(picks)==5
        for i,r in enumerate(pool):
            rank=i/(len(pool)-1);relative='lower_tail' if rank<.2 else 'upper_tail' if rank>.8 else 'middle'
            d=dict(player_id=r['PLAYER_ID'],player_name=r['PLAYER_NAME'],combine_year=int(r['SEASON']),sampling_era_stratum=e,sampling_height_stratum=h,sampling_relative_wingspan_stratum=relative,archive_barefoot_height=float(r['HEIGHT_WO_SHOES']),archive_wingspan=float(r['WINGSPAN']),within_cell_advantage_rank=rank)
            (selected if i in picks else reserve).append(d)
    return selected,reserve

def replacement(original,reserve,used):
    keys=['sampling_era_stratum','sampling_height_stratum','sampling_relative_wingspan_stratum']
    pool=[r for r in reserve if (r['player_id'],r['combine_year']) not in used and all(r[k]==original[k] for k in keys)]
    return sorted(pool,key=lambda r:hashlib.sha256((r['player_id']+':'+str(r['combine_year'])).encode()).hexdigest())[0] if pool else None

def field_status(archive,official,precision=.25,available=True):
    if not available:return 'official_source_unavailable'
    if official is None:return 'official_value_missing'
    if abs(archive-official)<1e-9:return 'exact'
    if precision<=.25 and abs(archive-official)<=.125:return 'rounding_consistent'
    return 'conflict'

def pair_check(r,observation):
    if not observation:return ('official_source_unavailable',)*3
    if str(observation['player_id'])!=str(r['player_id']) or int(observation['combine_year'])!=int(r['combine_year']):raise ValueError('Player/year mismatch')
    h=field_status(float(r['archive_barefoot_height']),observation.get('barefoot_height'),observation.get('precision',.25))
    w=field_status(float(r['archive_wingspan']),observation.get('wingspan'),observation.get('precision',.25))
    pair='conflict' if 'conflict' in (h,w) else 'official_value_missing' if 'official_value_missing' in (h,w) else 'rounding_consistent' if 'rounding_consistent' in (h,w) else 'exact'
    return h,w,pair

def candidate_identities(reader=None):
    if reader is None:
        import pyarrow.parquet as pq
        reader=pq.read_table
    return reader(ROOT/'data/processed/ft_2013_14_stage1_dataset.parquet',columns=IDENTITY_COLUMNS).to_pylist()

def fetch(url,label,source_type,years,timeout=20):
    RAW.mkdir(parents=True,exist_ok=True);stamp=now()
    r=subprocess.run(['curl','-L','-sS','--max-time',str(timeout),'-A','Mozilla/5.0','-H','Referer: https://www.nba.com/','-w','%{stderr}\nHTTP_STATUS:%{http_code}',url],capture_output=True)
    diag=r.stderr.decode(errors='replace');status=int(diag.rsplit('HTTP_STATUS:',1)[1]) if 'HTTP_STATUS:' in diag else None
    digest=hashlib.sha256(r.stdout).hexdigest() if r.stdout else None;p=RAW/(digest+'.payload') if digest else None
    if p and not p.exists():p.write_bytes(r.stdout)
    m=dict(source_name=label,publisher='NBA' if source_type.startswith('official') else 'see source URL',source_type=source_type,url=url,years=years,retrieval_timestamp_utc=stamp,http_status=status,transport_exit=r.returncode,error=diag.split('HTTP_STATUS:')[0].strip(),raw_sha256=digest,raw_path=str(p.relative_to(ROOT)) if p else None,bytes=len(r.stdout),retrieval_method='curl GET')
    dump(RAW/(hashlib.sha256((url+stamp).encode()).hexdigest()[:20]+'.manifest.json'),m)
    return m

def source_inches(value):
    # Official DOM sometimes omits a zero before fractional inches, e.g. 8' .25''.
    return inches(re.sub(r"'\s*\.", "' 0.", value) if isinstance(value,str) else value)

def systematic_discrepancies(checks):
    """Predeclared descriptive offset screen, not an inferential hypothesis test."""
    import statistics
    flags=[]
    for field in ['height_difference_inches','wingspan_difference_inches']:
        for group in ['sampling_era_stratum','sampling_height_stratum']:
            for label in {r[group] for r in checks}:
                ds=[r[field] for r in checks if r[group]==label and r[field] is not None and r[field]!=0]
                for sign in [-1,1]:
                    same=[d for d in ds if d*sign>0]
                    if len(same)>=3 and statistics.median(abs(d) for d in same)>.125:
                        flags.append(dict(field=field,group=group,stratum=label,sign=sign,count=len(same)))
    return flags
