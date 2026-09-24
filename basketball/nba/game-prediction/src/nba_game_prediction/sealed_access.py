"""Fail-closed development I/O policy. Not a substitute for an OS sandbox."""
import builtins,io,os,re,socket,json
from pathlib import Path
from hashlib import sha256
from contextvars import ContextVar
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
OPEN=tuple(f'{y}-{str(y+1)[2:]}' for y in range(2015,2024))
SAFE=frozenset('season season_type game_id game_date team_id team_name team_abbreviation home_team_id home_team_name home_team_abbreviation away_team_id away_team_name away_team_abbreviation is_home matchup opponent_team_abbreviation neutral_site venue city'.split())
_ACTIVE=ContextVar('projected_reader',default=False)
_STAGE5_SESSION=ContextVar('stage5_authorized_session',default=None)
_RAW_OPEN=builtins.open
_RAW_IO=io.open
_RAW_PATH_OPEN=Path.open
EVENTS=Counter();READS=Counter();INSTALLED=False
class SealedAccessError(ValueError):pass

def deny(reason):
    EVENTS['blocked:'+reason]+=1
    raise SealedAccessError(reason)

def require_seasons(seasons,purpose='outcomes'):
    seasons=tuple(seasons)
    if not seasons or any(s not in OPEN for s in seasons):deny('sealed or forbidden season: '+purpose)
    return seasons

def path_of(source):
    if isinstance(source,(str,bytes,os.PathLike)):
        return Path(os.fsdecode(source)).resolve()
    return None

def kind(source):
    p=path_of(source)
    if p is None:return 'anonymous'
    if re.search(r'2025[-_]26',str(p)):return 'forbidden'
    try:rel=p.relative_to(ROOT/'data')
    except ValueError:return 'other'
    text=str(rel)
    if re.search(r'2024[-_]25',text):return 'sealed'
    if 'multiseason' in text:
        return 'open' if p.name.startswith('stage1c_') else 'mixed'
    if any(s in text or s.replace('-','_') in text for s in OPEN):return 'open'
    return 'unknown'

def filters_open(filters):
    if not isinstance(filters,list) or not filters:return False
    branches=[filters] if isinstance(filters[0],tuple) else filters
    for branch in branches:
        if not isinstance(branch,list) or not branch:return False
        bounded=False
        for term in branch:
            if not isinstance(term,tuple) or len(term)!=3:return False
            col,op,value=term
            if col=='season' and op in ('=','==','in'):
                values=[value] if op!='in' else value
                if not isinstance(values,(list,tuple)) or not values or not all(v in OPEN for v in values):return False
                bounded=True
        if not bounded:return False
    return True

def check_projection(source,columns,filters=None):
    k=kind(source)
    if k=='forbidden':deny('2025-26 access forbidden')
    session=_STAGE5_SESSION.get()
    if session is not None and session.admit_read(source,columns,filters):
        READS[(str(path_of(source).relative_to(ROOT)),tuple(columns or ()),repr(filters))]+=1
        return
    if k=='anonymous':deny('anonymous decoder source forbidden')
    if k=='unknown':deny('unregistered project data source forbidden')
    if k in ('sealed','mixed','open'):
        ledger=json.loads((ROOT/'docs/stage4a_evidence/protected_artifact_hashes_before.json').read_text())
        relative=str(path_of(source).relative_to(ROOT))
        if relative not in ledger:deny('unregistered project data source forbidden')
        if checksum(path_of(source))!=ledger[relative]:deny('protected data checksum mismatch')
    if k in ('sealed','mixed','unknown'):
        if filters is not None:
            branches=[filters] if isinstance(filters,list) and filters and isinstance(filters[0],tuple) else filters
            if not isinstance(branches,list) or not branches:deny('unsupported sealed filter')
            for branch in branches:
                if not isinstance(branch,list) or not branch:deny('unsupported sealed filter')
                for term in branch:
                    if not isinstance(term,tuple) or len(term)!=3 or term[0] not in SAFE:deny('outcome filter forbidden')
                    if '2025-26' in str(term[2]) or '2025_26' in str(term[2]):deny('2025-26 filter forbidden')
        if not isinstance(columns,(list,tuple)) or not columns:deny('broad sealed read forbidden')
        safe=set(columns).issubset(SAFE)
        if not safe and not (k=='mixed' and filters_open(filters)):deny('sealed outcome or derived value forbidden')
        if not safe and k=='mixed' and 'outcome' in path_of(source).name:deny('mixed outcome containers are metadata-only; use load_outcomes')
        if k=='sealed' and path_of(source).suffix not in ('.parquet','.csv'):deny('sealed raw source forbidden')
        EVENTS['allowed:metadata' if safe else 'allowed:open_filtered']+=1
    if k in ('sealed','mixed','unknown','open'):
        READS[(str(path_of(source).relative_to(ROOT)),tuple(columns or ()),repr(filters))]+=1

def guarded_open(original):
    def wrapped(file,mode='r',*args,**kwargs):
        if not _ACTIVE.get() and isinstance(file,(str,bytes,os.PathLike)):
            k=kind(file)
            if k=='forbidden':deny('2025-26 physical access forbidden')
            if k in ('sealed','mixed','unknown') and not any(x in mode for x in ('w','a','x')):deny('unprojected sealed physical read forbidden')
        return original(file,mode,*args,**kwargs)
    return wrapped

def checksum(path):
    """Opaque integrity stream: returns only a digest, never bytes or decoded values."""
    if kind(path)=='forbidden':deny('2025-26 checksum forbidden')
    h=sha256()
    with _RAW_OPEN(path,'rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    EVENTS['checksum_only']+=1
    return h.hexdigest()

def no_model_execution(*args,**kwargs):
    EVENTS['blocked:model_execution']+=1
    raise RuntimeError('Stage 4A: model fitting/replay/prediction/selection/evaluation forbidden')

def decoder(original,label):
    def wrapped(source,*args,**kwargs):
        if _ACTIVE.get():return original(source,*args,**kwargs)
        columns=kwargs.get('columns',args[0] if args and label=='parquet' else None)
        if label=='csv':columns=kwargs.get('usecols')
        check_projection(source,columns,kwargs.get('filters'))
        token=_ACTIVE.set(True)
        try:return original(source,*args,**kwargs)
        finally:_ACTIVE.reset(token)
    return wrapped

def load_outcomes(root,seasons,purpose,columns=('game_id','home_win')):
    seasons=require_seasons(seasons,purpose)
    if not purpose or not columns or not set(columns).issubset({'season','game_id','home_win','home_pts','away_pts'}):deny('invalid outcome projection')
    import pandas as pd
    frames=[]
    for season in seasons:
        path=Path(root)/'data/interim/seasons'/('game_outcomes_'+season.replace('-','_')+'.parquet')
        selected=[c for c in columns if c!='season']
        frame=pd.read_parquet(path,columns=selected or ['game_id'])
        if 'season' in columns:frame['season']=season
        frames.append(frame.loc[:,list(columns)])
    return pd.concat(frames,ignore_index=True)

def load_identity(root,seasons=('2024-25',),columns=('season','game_id','game_date','home_team_id','away_team_id')):
    if not seasons or any(s not in OPEN+('2024-25',) for s in seasons):deny('forbidden identity season')
    if not columns or not set(columns).issubset(SAFE):deny('identity projection contains outcomes')
    import pandas as pd
    return pd.read_parquet(Path(root)/'data/processed/game_features_multiseason.parquet',columns=list(columns),filters=[('season','in',list(seasons))])

def install():
    global INSTALLED
    if INSTALLED:return
    import pandas as pd
    import pyarrow.parquet as pq
    import pyarrow.dataset as ds
    pd.read_parquet=decoder(pd.read_parquet,'parquet');pd.read_csv=decoder(pd.read_csv,'csv');pd.read_json=decoder(pd.read_json,'json')
    pq.read_table=decoder(pq.read_table,'arrow');pq.read_pandas=decoder(pq.read_pandas,'arrow')
    for module,name in [(pq,'ParquetFile'),(ds,'dataset')]:
        original=getattr(module,name)
        def constructor(source,*args,_original=original,**kwargs):
            if not _ACTIVE.get() and kind(source) in ('sealed','mixed','unknown','forbidden','anonymous'):deny('direct Arrow reader forbidden')
            return _original(source,*args,**kwargs)
        setattr(module,name,constructor)
    builtins.open=guarded_open(_RAW_OPEN);io.open=guarded_open(_RAW_IO);Path.open=guarded_open(_RAW_PATH_OPEN)
    original_socket=socket.socket
    class BlockedSocket(original_socket):
        def __init__(self,*args,**kwargs):
            EVENTS['blocked:network']+=1
            raise RuntimeError('Development network blocked')
    socket.socket=BlockedSocket
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import HistGradientBoostingClassifier
    for cls in (LogisticRegression,HistGradientBoostingClassifier):
        for method in ('fit','predict','predict_proba'):
            original=getattr(cls,method)
            def guarded(self,*args,_method=method,_original=original,**kwargs):
                session=_STAGE5_SESSION.get()
                if session is None:return no_model_execution()
                return session.model_call(_original,_method,self,*args,**kwargs)
            setattr(cls,method,guarded)
    INSTALLED=True

def snapshot():
    return dict(events=dict(sorted(EVENTS.items())),reads=[dict(path=p,columns=list(c),filters=f,count=n) for (p,c,f),n in sorted(READS.items())],network_blocked=INSTALLED)
