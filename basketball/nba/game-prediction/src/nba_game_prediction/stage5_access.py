"""Stage 5-only authorization, ledger and exact frozen numerical runtime."""
from pathlib import Path
from datetime import datetime,timezone
from contextlib import contextmanager
import hashlib,importlib,json,sys,types,os
from . import sealed_access as access
from .multiseason import write_json
SEASON='2024-25'
IDENTITY=['season','game_id','game_date','home_team_id','away_team_id']
NAMES={'constant_home_prior':'constant_probability','raw_elo':'raw_elo_probability','basketball_features_logistic':'basketball_features_logistic_probability','elo_logistic':'elo_logistic_probability','features_plus_elo_logistic':'features_plus_elo_logistic_probability','basketball_features_hgb':'basketball_features_hgb_probability','features_plus_elo_hgb':'features_plus_elo_hgb_probability'}
PRIMARY=('features_plus_elo_logistic','raw_elo')
def now():return datetime.now(timezone.utc).isoformat(timespec='microseconds')
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def exclusive_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(value,indent=2,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())

def verify_artifacts(root):
    expected=json.loads((root/'docs/stage5_evidence/protected_before.json').read_text())
    for p,h in expected.items():
        if access.checksum(root/p)!=h:raise ValueError('Frozen artifact mismatch: '+p)
    return expected

def verify_recipes(root):
    freeze=json.loads((root/'docs/stage4a_evidence/candidate_freeze.json').read_text())
    if freeze['candidates']!=list(NAMES) or freeze['leading_candidate']!=PRIMARY[0]:raise ValueError('Candidate set changed')
    s2=json.loads((root/'docs/stage2_evidence/selected_elo_parameters.json').read_text());s3=json.loads((root/'docs/stage3_evidence/selected_logistic_parameters.json').read_text());s4=json.loads((root/'docs/stage4_evidence/selected_hgb_parameters.json').read_text())
    if s2['parameters']!={'K':20.,'H':50.,'alpha':.5} or freeze['frozen_elo']!=s2['parameters']:raise ValueError('Elo changed')
    if s3['C_by_model']!={m:.01 for m in list(NAMES)[2:5]}:raise ValueError('C changed')
    expected={'basketball_features_hgb':dict(learning_rate=.03,max_leaf_nodes=7,l2_regularization=5.),'features_plus_elo_hgb':dict(learning_rate=.03,max_leaf_nodes=7,l2_regularization=1.)}
    if s4['parameters_by_model']!=expected:raise ValueError('HGB changed')
    from .features import GAME_FEATURES
    for m in list(NAMES)[2:]:
        recipe=freeze['recipes'][m];features=['elo_logit'] if m=='elo_logistic' else GAME_FEATURES+(['elo_logit'] if m.startswith('features_plus_elo') else [])
        if recipe['features']!=features:raise ValueError('Feature allowlist changed')
        if m.endswith('_hgb'):
            if recipe['parameters']!=expected[m] or recipe['fixed']!=s4['fixed']:raise ValueError('HGB freeze mismatch')
        elif recipe['C']!=s3['C_by_model'][m]:raise ValueError('Logistic freeze mismatch')
    return freeze,s2,s3,s4

class Session:
    """A single process capability, bound to verified recipes and immutable protocol."""
    def __init__(self,root,mode):
        self.root=Path(root);self.e=self.root/'docs/stage5_evidence';self.mode=mode
        if mode not in ('open','replay'):raise ValueError('Unknown Stage 5 operation')
        verify_artifacts(self.root);self.freeze,*_=verify_recipes(self.root)
        self.ledger_path=self.e/'preholdout_opening_ledger.json'
        self.phase='reconstruct';self.fit_calls=[];self.training_model=None;self.decode_calls=0
        if mode=='open' and self.ledger_path.exists():raise RuntimeError('Opening ledger already exists; cannot open again')
        if mode=='replay':
            ledger=json.loads(self.ledger_path.read_text())
            if ledger['status']!='completed':raise RuntimeError('Incomplete/failed opening: STOP; no automatic recovery')
            self.phase='replay'
    def check_seasons(self,seasons):
        seasons=list(seasons)
        allowed=access.OPEN+(SEASON,) if self.phase in ('opened','replay') else access.OPEN
        if not seasons or any(s not in allowed for s in seasons):raise access.SealedAccessError('Stage 5 season not authorized')
    def model_call(self,original,method,estimator,*args,**kwargs):
        if type(estimator).__name__ not in ('LogisticRegression','HistGradientBoostingClassifier'):raise RuntimeError('Unapproved estimator')
        if method=='fit':
            if self.phase!='reconstruct' or self.ledger_path.exists() or self.training_model not in list(NAMES)[2:] or len(args[0])!=9519:raise RuntimeError('Fit forbidden outside original training reconstruction')
            self.fit_calls.append(dict(model=self.training_model,rows=len(args[0]),phase=self.phase))
        elif self.phase not in ('reconstruct','opened','replay'):raise RuntimeError('Prediction phase forbidden')
        return original(estimator,*args,**kwargs)
    def admit_read(self,source,columns,filters):
        path=access.path_of(source)
        if path is None:return False
        relative=str(path.relative_to(self.root)) if path.is_relative_to(self.root) else ''
        targets={'data/interim/reconciled/game_outcomes_2024_25.parquet':('game_id','home_win'),'data/processed/seasons/game_features_2024_25.parquet':None}
        if relative not in targets:return False
        if self.phase not in ('armed','opened','replay'):return False
        from .features import GAME_FEATURES
        expected=list(targets[relative]) if targets[relative] else IDENTITY+GAME_FEATURES
        if columns!=expected or filters is not None:raise access.SealedAccessError('Stage 5 exact projection required')
        protected=json.loads((self.e/'protected_before.json').read_text())
        if access.checksum(path)!=protected[relative]:raise ValueError('Stage 1D input hash mismatch')
        if targets[relative]:
            if self.decode_calls:raise RuntimeError('Only one outcome decode per evaluation process')
            if self.phase=='armed':
                ledger=json.loads(self.ledger_path.read_text())
                if ledger['status']!='authorized_not_decoded':raise RuntimeError('Opening already consumed')
                timestamp=now();event=dict(event='first_stage5_outcome_decode_started',timestamp_utc=timestamp,source=relative,columns=columns)
                exclusive_json(self.e/'first_outcome_decode.json',event)
                ledger.update(status='opened',first_outcome_decode_started_at_utc=timestamp)
                write_json(self.ledger_path,ledger);self.phase='opened'
            self.decode_calls+=1
        elif self.phase=='armed':raise RuntimeError('Outcome boundary must precede sealed feature read')
        return True
    def arm(self,gate,protocol_hash,code_hash):
        if self.phase!='reconstruct' or self.mode!='open' or len(self.fit_calls)!=5 or not gate['passed']:raise RuntimeError('Opening gate incomplete')
        if access.checksum(self.e/'preopening_verification.json')!=gate['gate_file_sha256']:raise RuntimeError('Gate changed')
        ledger=dict(authorization_stage='Stage 5',authorized_season=SEASON,authorization_recorded_at_utc=now(),authorization_source_sha256=gate['authorization_source_sha256'],candidate_set_sha256=access.checksum(self.root/'docs/stage4a_evidence/candidate_freeze.json'),protocol_sha256=protocol_hash,code_sha256=code_hash,preopening_gate_sha256=gate['gate_file_sha256'],training_seasons=list(access.OPEN[:-1]),metrics=['log_loss','brier_score','accuracy','roc_auc','fixed_bin_calibration'],primary_comparison=list(PRIMARY),target='P(designated home team wins)',expected_games=1230,final_holdout='2025-26 forbidden and untouched',status='authorized_not_decoded',first_outcome_decode_started_at_utc=None,history='First Stage 5 evaluation opening; does not erase Stage 1D/Stage 4 structural label access')
        exclusive_json(self.ledger_path,ledger);self.phase='armed'
    @contextmanager
    def activate(self):
        token=access._STAGE5_SESSION.set(self)
        try:yield self
        finally:access._STAGE5_SESSION.reset(token)

def frozen_runtime(root,session):
    """Execute SHA-exact historical modules; only temporal permission is an overlay."""
    root=Path(root);folder=root/'docs/stage5_evidence/frozen_source';before=json.loads((root/'docs/stage4a_evidence/implementation_code_before.json').read_text())
    package='_nba_stage5_frozen';pkg=types.ModuleType(package);pkg.__path__=[];sys.modules[package]=pkg
    for name in ['features','seasons','multiseason']:
        sys.modules[package+'.'+name]=importlib.import_module('nba_game_prediction.'+name)
    result={}
    for name in ['policy','metrics','elo','evaluation','modeling_data','logistic','boosting']:
        path=folder/(name+'.py');source=path.read_text()
        if sha_bytes(source.encode())!=before['src/nba_game_prediction/'+name+'.py']:raise ValueError('Frozen numerical code mismatch: '+name)
        mod=types.ModuleType(package+'.'+name);mod.__file__=str(path);mod.__package__=package;sys.modules[mod.__name__]=mod
        exec(compile(source,str(path),'exec'),mod.__dict__)
        if name=='policy':mod.require_open=session.check_seasons
        result[name]=mod
    # No tuning route is available through the execution runtime.
    result['elo'].select_parameters=access.no_model_execution
    result['boosting'].select_hgb=access.no_model_execution
    return types.SimpleNamespace(**result)
