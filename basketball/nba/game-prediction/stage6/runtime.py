"""Explicit one-time Stage 6 capability; normal development guards stay installed.
Only this executor admits its fixed raw cache and fixed prediction destination.
Historical numerical modules remain byte-exact. No model fitting is available.
"""
import contextlib, hashlib, io, json, os, pickle, socket, sys
from pathlib import Path
from importlib.metadata import version
from unittest.mock import patch
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from nba_game_prediction import sealed_access as access
from nba_game_prediction.stage5a import ROOT,E as E5,freeze_spec,protected,canonical_hash
from nba_game_prediction.stage5_access import NAMES,PRIMARY,IDENTITY,now,frozen_runtime,verify_recipes
from nba_game_prediction.stage5 import prediction_frame
from nba_game_prediction import features,normalize,validate,seasons
E=ROOT/'docs/stage6_evidence'
SEASON='2025-26'
RAW=ROOT/'data/raw/stage6/leaguegamelog_response.json'
PRED=ROOT/'data/processed/stage6_predictions_2025_26.parquet'
AUTH_HASH=''
PARAMS=dict(Counter=0,Direction='ASC',LeagueID='00',PlayerOrTeam='T',Season=SEASON,SeasonType='Regular Season',Sorter='DATE',DateFrom='',DateTo='')

def sha(b):return hashlib.sha256(b).hexdigest()
def read_json(p):return json.loads(p.read_text())
def durable(p,obj,exclusive=False):
    p.parent.mkdir(parents=True,exist_ok=True)
    if exclusive:
        with p.open('x') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    else:
        tmp=p.with_name(p.name+'.tmp')
        with tmp.open('w') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
    fd=os.open(p.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)

def checkpoint():return {str(p.relative_to(ROOT)):access.checksum(p) for p in sorted((ROOT/'stage6').glob('*.py'))}
def verify():
    saved=read_json(E5/'final_holdout_freeze.json')
    if freeze_spec()!=saved:raise ValueError('Final freeze mismatch: STOP before access')
    verify_recipes(ROOT)
    before=read_json(E/'preimplementation_verification.json')
    if access.checksum(E5/'final_holdout_freeze.json')!=before['final_freeze_sha256']:raise ValueError('Freeze document changed')
    if access.checksum(E/'authorization.txt')!=before['authorization_sha256']:raise ValueError('Authorization changed')
    return dict(passed=True,verified_at_utc=now(),final_freeze_sha256=before['final_freeze_sha256'],protocol_sha256=saved['protocol_sha256'],candidate_freeze_sha256=saved['full_candidate_freeze_sha256'],model_c_recipe_sha256=saved['model_c_recipe_sha256'],raw_elo_recipe_sha256=saved['raw_elo_recipe_sha256'],saved_estimators_sha256=saved['saved_estimators_sha256'],feature_allowlist_sha256=saved['feature_allowlist_sha256'],metrics_implementation=saved['metrics_implementation'],calibration_implementation=saved['calibration_implementation'],uncertainty_protocol_sha256=saved['uncertainty_protocol_sha256'],versions={k:version(k) for k in ['numpy','pandas','scikit-learn','pyarrow','nba_api','scipy','joblib','threadpoolctl']},historical_code_checkpoint=saved['current_code_checkpoint'],stage6_code_sha256=checkpoint(),protected_artifacts=len(protected()),historical_results_unchanged=True,authorization_sha256=before['authorization_sha256'])

class Session:
    def __init__(self,e=E):self.e=e;self.ledger=e/'final_opening_ledger.json';self.phase='preflight';self.fit_calls=[]
    def arm(self,authorization,gate,season=SEASON,season_type='Regular Season'):
        if season!=SEASON or season_type!='Regular Season':raise ValueError('Only authorized regular season')
        if not authorization or sha(authorization)!=gate['authorization_sha256']:raise ValueError('Explicit exact authorization required')
        if not gate.get('passed') or not gate.get('preflight_passed'):raise ValueError('Preflight gate required')
        f=read_json(E5/'final_holdout_freeze.json')
        # Stage 5A schema fields retained; supplemental provenance lives inside its object fields.
        ledger=dict(explicit_user_authorization=dict(text_sha256=sha(authorization),text=authorization.decode(),recorded_at_utc=now(),final_freeze_sha256=gate['final_freeze_sha256'],candidate_freeze_sha256=f['full_candidate_freeze_sha256'],training_policy=f['training_policy'],saved_estimators_sha256=f['saved_estimators_sha256']),authorized_season=SEASON,protocol_sha256=f['protocol_sha256'],confirmatory_candidate_sha256=f['model_c_recipe_sha256'],benchmark_sha256=f['raw_elo_recipe_sha256'],code_sha256=dict(historical=f['current_code_checkpoint'],executor=checkpoint(),dependency_versions=gate['versions'],dependency_versions_sha256=canonical_hash(gate['versions'])),metric_definitions=dict(primary=f['primary_metrics'],secondary=f['secondary_metrics'],implementation=f['metrics_implementation'],calibration=f['calibration_implementation']),uncertainty_method=f['uncertainty_protocol'],expected_dataset_scope=dict(season=SEASON,season_type='Regular Season',league='NBA',complete_season_required=True,observed_games=None),first_physical_data_access_at_utc=None,first_outcome_decode_at_utc=None,aggregate_results_persisted_at_utc=None)
        durable(self.ledger,ledger,True);self.phase='armed'
    def access_start(self):
        if self.phase!='armed' or not self.ledger.exists():raise RuntimeError('Durable ledger must precede access; duplicate opening forbidden')
        d=read_json(self.ledger)
        if d['first_physical_data_access_at_utc'] is not None:raise RuntimeError('Opening consumed')
        t=now();d['first_physical_data_access_at_utc']=t;durable(self.ledger,d)
        durable(self.e/'first_access.json',dict(timestamp_utc=t,event='immediately before NBA LeagueGameLog request',season=SEASON,parameters=PARAMS),True);self.phase='accessed'
    def decode_start(self):
        if self.phase!='accessed':raise RuntimeError('Decode order')
        t=now();d=read_json(self.ledger);d['first_outcome_decode_at_utc']=t;durable(self.ledger,d)
        durable(self.e/'first_outcome_decode.json',dict(timestamp_utc=t,event='raw JSON outcome decode begins',reason='Existing canonical structural validation and rolling history require scores/WL before model evaluation; no individual prediction errors inspected'),True);self.phase='decoded'
    def check_seasons(self,values):
        if self.phase not in ('validated','replay','synthetic') or any(s not in access.OPEN+('2024-25',SEASON) for s in values):raise RuntimeError('Season/phase not authorized')
    def model_call(self,original,method,estimator,*args,**kw):
        if method=='fit':raise RuntimeError('Stage 6 permits zero fit calls')
        if self.phase not in ('validated','replay','synthetic') or type(estimator).__name__ not in ('LogisticRegression','HistGradientBoostingClassifier'):raise RuntimeError('Prediction not authorized')
        return original(estimator,*args,**kw)
    def admit_read(self,*args):return False
    @contextlib.contextmanager
    def activate(self):
        t=access._STAGE5_SESSION.set(self)
        try:yield
        finally:access._STAGE5_SESSION.reset(t)
    def inspect_individual_errors(self):
        if not read_json(self.ledger)['aggregate_results_persisted_at_utc']:raise RuntimeError('Individual error inspection forbidden before aggregate persistence')
    def begin_replay(self):
        if not (self.e/'build_manifest.json').exists() or not read_json(self.e/'build_manifest.json').get('passed'):raise RuntimeError('Only a completed evaluation can replay')
        durable(self.e/'replay_started.json',dict(timestamp_utc=now(),independent_confirmation=False,cached_only=True),True);self.phase='replay'


def acquire(session):
    from nba_api.stats.endpoints.leaguegamelog import LeagueGameLog
    from nba_api.stats.library.http import NBAStatsHTTP
    import requests
    client=LeagueGameLog(counter=0,direction='ASC',league_id='00',player_or_team_abbreviation='T',season=SEASON,season_type_all_star='Regular Season',sorter='DATE',date_from_nullable='',date_to_nullable='',timeout=30,get_request=False)
    if client.parameters!=PARAMS:raise ValueError('Unexpected API parameters')
    class RestrictedTransport(requests.Session):
        def request(self,method,url,**kw):
            if method.upper()!='GET' or url!='https://stats.nba.com/stats/leaguegamelog' or dict(kw['params'])!=PARAMS:raise RuntimeError('Unapproved network request')
            kw['allow_redirects']=False
            # Scoped, single-request exception to the unchanged offline development policy.
            original_socket=socket.socket.__mro__[1]
            if socket.socket.__name__!='BlockedSocket':raise RuntimeError('Unexpected network policy')
            with patch.object(socket,'socket',original_socket):return super().request(method,url,**kw)
    session.access_start()
    transport=RestrictedTransport();http=NBAStatsHTTP();http.set_session(transport)
    meta=dict(source='NBA Stats via maintained nba_api',nba_api_version=version('nba_api'),endpoint='LeagueGameLog',parameters=PARAMS,retrieval_started_utc=now())
    try:
        response=http.send_api_request(endpoint=client.endpoint,parameters=client.parameters,timeout=30)
        body=response.get_response().encode('utf-8')
        RAW.parent.mkdir(parents=True,exist_ok=True)
        with RAW.open('xb') as f:f.write(body);f.flush();os.fsync(f.fileno())
        meta.update(http_status=response._status_code,url=response.get_url(),sha256=sha(body),raw_bytes=len(body),raw_file=str(RAW.relative_to(ROOT)),retrieved_at_utc=now())
        durable(E/'acquisition.json',meta,True)
        if response._status_code!=200:raise RuntimeError('NBA endpoint did not return HTTP 200; no outcome decode')
        session.decode_start()
        return body
    except Exception as exc:
        durable(E/'acquisition_failure.json',dict(**meta,error_type=type(exc).__name__,error=str(exc),failed_at_utc=now()),True)
        raise
    finally:transport.close()

@contextlib.contextmanager
def scope_overlay(scope,rt=None):
    original=seasons.get_scope
    def scoped(s):return scope if s==SEASON else original(s)
    with contextlib.ExitStack() as st:
        for mod in [normalize,validate,features]+([rt.elo] if rt else []):st.enter_context(patch.object(mod,'get_scope',scoped))
        yield

def validate_body(body,out=E):
    from nba_game_prediction.ingest import extract_table
    headers,rows=extract_table(body)
    raw=pd.DataFrame(rows,columns=headers)
    dates=pd.to_datetime(raw.GAME_DATE,format='%Y-%m-%d',errors='raise')
    if not dates.between('2025-07-01','2026-06-30').all():raise ValueError('Season dates outside year envelope')
    scope=seasons.SeasonScope(SEASON,str(dates.min().date()),str(dates.max().date()))
    with scope_overlay(scope):
        norm=normalize.normalize(body,season=SEASON);teams,games,anomalies=validate.validate_and_pair(norm,season=SEASON)
    counts=norm.groupby('team_id').size();rejects=anomalies[anomalies.severity.eq('reject')]
    valid=not len(rejects) and len(counts)==30 and counts.eq(82).all() and len(teams)==len(norm) and len(games)*2==len(norm)
    summary=dict(team_game_rows=len(norm),unique_games=int(norm.game_id.nunique()),accepted_games=len(games),teams=len(counts),first_game_date=scope.start,last_game_date=scope.end,games_per_team={str(k):int(v) for k,v in counts.items()},missingness={k:int(v) for k,v in norm.isna().sum().items()},anomaly_counts={str(k):int(v) for k,v in anomalies.groupby(['severity','reason']).size().items()},passed=bool(valid),completeness_rule='Actual observed rows; every registered NBA team must have 82 regular-season games; no rejected records or subset scoring',neutral_site_policy='Original MATCHUP designated-home contract; unresolved both-away or other structural issues stop evaluation; no inferred designation')
    durable(out/'validation.json',summary)
    anomalies.to_csv(out/'structural_anomalies.csv',index=False)
    if not valid:raise ValueError('Incomplete or structurally unresolved season: STOP without scoring')
    return scope,teams,games

def bootstrap(pred):
    if pred.empty or pred.duplicated(['season','game_id']).any():raise ValueError('Empty/duplicate keys')
    dates=pd.to_datetime(pred.game_date,errors='raise')
    if dates.isna().any() or not dates.eq(dates.dt.normalize()).all():raise ValueError('Missing/noncalendar dates')
    y=pred.home_win.to_numpy(float);c=pred[NAMES[PRIMARY[0]]].to_numpy(float);e=pred[NAMES[PRIMARY[1]]].to_numpy(float)
    if not np.isfinite(np.column_stack([y,c,e])).all() or not np.isin(y,[0,1]).all() or not ((c>=0)&(c<=1)&(e>=0)&(e<=1)).all():raise ValueError('Invalid paired input')
    def ll(p):
        q=np.clip(p,1e-15,1-1e-15);return -(y*np.log(q)+(1-y)*np.log1p(-q))
    diff=np.column_stack([ll(c)-ll(e),(c-y)**2-(e-y)**2]);unique,indices=np.unique(dates.to_numpy(),return_inverse=True);g=len(unique)
    if g<2:raise ValueError('At least two date clusters required')
    sums=np.zeros((g,2));np.add.at(sums,indices,diff);counts=np.bincount(indices)
    rng=np.random.default_rng(0);rep=np.empty((10000,2))
    for b in range(10000):
        draw=rng.integers(0,g,size=g);rep[b]=sums[draw].sum(axis=0)/counts[draw].sum()
    rows=[]
    for j,metric in enumerate(['log_loss','brier_score']):
        q25,q75=np.quantile(diff[:,j],[.25,.75],method='linear');lo,hi=np.quantile(rep[:,j],[.025,.975],method='linear')
        rows.append(dict(metric=metric,n_games=len(pred),n_unique_dates=g,observed_mean_difference=float(diff[:,j].mean()),median_difference=float(np.median(diff[:,j])),q25_difference=float(q25),q75_difference=float(q75),interquartile_range=float(q75-q25),bootstrap_replicates=10000,bootstrap_seed=0,bootstrap_mean=float(rep[:,j].mean()),bootstrap_standard_error=float(rep[:,j].std(ddof=1)),ci_lower_2_5=float(lo),ci_upper_97_5=float(hi),includes_zero=bool(lo<=0<=hi),label='DATE-CLUSTERED DESCRIPTIVE BOOTSTRAP INTERVAL'))
    return pd.DataFrame(rows)

def runtime(session):
    rt=frozen_runtime(ROOT,session)
    for mod in [rt.elo,rt.logistic,rt.boosting]:
        for name in list(vars(mod)):
            if name.startswith('select_') or name.startswith('fit_'):setattr(mod,name,access.no_model_execution)
    return rt

def predict(session,scope,teams,games):
    rt=runtime(session)
    bundle=pickle.loads((ROOT/'docs/stage5_evidence/frozen_estimators.pkl').read_bytes())
    fits=bundle['fits'];before=sha(pickle.dumps(fits,protocol=5))
    if list(fits)!=list(NAMES)[2:]:raise ValueError('Candidate set mismatch')
    with scope_overlay(scope,rt),session.activate(),threadpool_limits(limits=1):
        _,f=features.build_features(teams,games,games[['game_id','home_pts','away_pts','home_win']])
        # Prefix invariance exercises the unchanged rolling code without error inspection.
        cutoff=games.game_date.sort_values().iloc[len(games)//2];pg=games[games.game_date<=cutoff];pt=teams[teams.game_id.isin(pg.game_id)]
        _,pf=features.build_features(pt,pg,pg[['game_id','home_pts','away_pts','home_win']])
        pd.testing.assert_frame_equal(f[f.game_id.isin(pg.game_id)].reset_index(drop=True),pf)
        d=f[IDENTITY+features.GAME_FEATURES].merge(games[['game_id','home_win']],on='game_id',validate='one_to_one')
        # Exact, already-opened previous-season prediction artifact supplies only Elo identities/y.
        historical_path=ROOT/'data/processed/stage5_predictions_2024_25.parquet'
        expected=read_json(E5/'final_holdout_freeze.json')['stage5_evidence_sha256'][str(historical_path.relative_to(ROOT))]
        if access.checksum(historical_path)!=expected:raise ValueError('Historical input changed')
        token=access._ACTIVE.set(True)
        try:
            with access._RAW_OPEN(historical_path,'rb') as handle:past=pd.read_parquet(handle,columns=IDENTITY+['home_win'])
        finally:access._ACTIVE.reset(token)
        full=pd.concat([bundle['history'],past,d],ignore_index=True)
        aug=rt.modeling_data.add_frozen_elo(full);final=aug[aug.season.eq(SEASON)].reset_index(drop=True)
        pred=prediction_frame(rt,fits,final,bundle['prior'])
        if len(pred)!=len(games) or set(pred.game_id)!=set(games.game_id):raise ValueError('Incomplete predictions')
        if sha(pickle.dumps(fits,protocol=5))!=before:raise ValueError('Estimator state changed')
    return rt,pred

def save_results(rt,pred,out):
    out.mkdir(parents=True,exist_ok=True)
    # Fixed-name capability for the explicitly requested final artifact only.
    destination=PRED if out==E else out/'predictions.parquet'
    with access._RAW_OPEN(destination,'xb') as handle:pred.to_parquet(handle,index=False);handle.flush();os.fsync(handle.fileno())
    metrics=pd.DataFrame([dict(model=m,split='2025-26 final holdout',**rt.metrics.evaluate(pred,col)) for m,col in NAMES.items()])
    metrics.to_csv(out/'final_holdout_metrics.csv',index=False)
    ix=metrics.set_index('model');delta={f'delta_{dest}':float(ix.loc[PRIMARY[0],src]-ix.loc[PRIMARY[1],src]) for src,dest in [('log_loss','log_loss'),('brier_score','brier'),('accuracy','accuracy'),('roc_auc','roc_auc')]}
    status='replicated' if delta['delta_log_loss']<0 and delta['delta_brier']<0 else ('not replicated' if delta['delta_log_loss']>=0 and delta['delta_brier']>=0 else 'mixed')
    pd.DataFrame([dict(comparison='features_plus_elo_logistic vs raw_elo',**delta,directional_replication_status=status)]).to_csv(out/'primary_comparison.csv',index=False)
    bs=bootstrap(pred);bs.to_csv(out/'date_cluster_bootstrap.csv',index=False);bs.iloc[:,:8].to_csv(out/'paired_loss_summary.csv',index=False)
    summaries=[]
    for m,col in NAMES.items():
        t=rt.metrics.calibration(pred,col);t.to_csv(out/('calibration_model_c.csv' if m==PRIMARY[0] else f'calibration_{m}.csv'),index=False)
        summaries.append(dict(model=m,**rt.metrics.calibration_summary(t),mean_predicted_probability=float(pred[col].mean()),observed_designated_home_win_rate=float(pred.home_win.mean())))
    pd.DataFrame(summaries).to_csv(out/'calibration_summary.csv',index=False)
    rows=[]
    for role,table in [('2023-24 development validation',pd.read_csv(ROOT/'docs/stage4_evidence/validation_metrics.csv',float_precision='round_trip').set_index('model')),('2024-25 pre-holdout',pd.read_csv(ROOT/'docs/stage5_evidence/preholdout_metrics.csv',float_precision='round_trip').set_index('model')),('2025-26 final holdout',ix)]:
        row={'split':role}
        for src,dest in [('log_loss','log_loss'),('brier_score','brier'),('accuracy','accuracy'),('roc_auc','auc')]:
            row['raw_elo_'+dest]=float(table.loc[PRIMARY[1],src]);row['model_c_'+dest]=float(table.loc[PRIMARY[0],src])
            if dest in ('log_loss','brier'):row['delta_'+dest]=row['model_c_'+dest]-row['raw_elo_'+dest]
        rows.append(row)
    pd.DataFrame(rows).to_csv(out/'cross_season_confirmation.csv',index=False)
    hashes={p.name:access.checksum(p) for p in out.glob('*.csv') if p.name not in ('structural_anomalies.csv',)}
    with access._RAW_OPEN(destination,'rb') as handle:hashes['predictions.parquet']=sha(handle.read())
    return hashes
