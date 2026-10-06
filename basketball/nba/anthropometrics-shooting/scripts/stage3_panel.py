"""Outcome-independent measurement selection and candidate panel accounting.

A failed source gate produces a hashed CANDIDATE only, never an inferential release.
"""
import json
import numpy as np
import pandas as pd
from stage3_sources import ROOT,E,sha,save

def select_vectors(measurements,first_seasons):
 selected=[]; alternatives=[]
 for pid,first in sorted(first_seasons.items()):
  rows=measurements[measurements.player_id==pid].sort_values('combine_year'); prior=rows[rows.combine_year<=int(first[:4])]
  chosen=None if prior.empty else prior.iloc[-1]
  for r in rows.to_dict('records'): alternatives.append(dict(**r,first_observed_season=first,chosen=chosen is not None and r['combine_year']==chosen.combine_year,eligible_timing=r['combine_year']<=int(first[:4])))
  if chosen is not None: selected.append(dict(**chosen.to_dict(),first_observed_season=first))
 return pd.DataFrame(selected),pd.DataFrame(alternatives)

def summary(d):
 counts=d.groupby('player_id').size()
 return dict(seasons=sorted(d.season.unique()),player_seasons=len(d),unique_players=d.player_id.nunique(),median_seasons_per_player=float(counts.median()),max_seasons_per_player=int(counts.max()),FTA=int(d.fta.sum()),FTA_zero=int((d.fta==0).sum()),likelihood_rows=int((d.fta>0).sum()),FTA_ge50=int((d.fta>=50).sum()),FTA_ge100=int((d.fta>=100).sum()),players_one_season=int((counts==1).sum()),players_two_four_seasons=int(counts.between(2,4).sum()),players_five_plus_seasons=int((counts>=5).sum()),measurement_year_distribution_unique_players={str(k):int(v) for k,v in d.drop_duplicates('player_id').combine_year.value_counts().sort_index().items()},status='CANDIDATE ONLY — source gate unresolved')

def main():
 prior=json.loads((E/'prior_preservation_manifest.json').read_text()); assert all(sha(ROOT/p)==h for p,h in prior.items())
 d=pd.read_parquet(ROOT/'data/interim/stage3_all_player_seasons.parquet'); measurements=pd.read_csv(ROOT/'data/interim/stage3_validated_measurements.csv',dtype={'player_id':str},keep_default_na=False)
 assert not measurements.duplicated(['player_id','combine_year']).any()
 first=d.groupby('player_id').season.min().to_dict(); vectors,alternatives=select_vectors(measurements,first)
 alternatives.to_csv(ROOT/'data/interim/stage3_measurement_selection_audit.csv',index=False); vectors.to_csv(ROOT/'data/interim/stage3_frozen_player_vectors.csv',index=False)
 panel=d.merge(vectors,on='player_id',how='inner',validate='many_to_one'); assert (panel.combine_year<=panel.season.str[:4].astype(int)).all()
 g=json.loads((ROOT/'docs/stage1_evidence/residualization_model.json').read_text()); panel['residual_wingspan']=panel.wingspan_inches-(g['intercept']+g['slope']*panel.height_wo_shoes_inches)
 panel['wingspan_advantage']=panel.wingspan_inches-panel.height_wo_shoes_inches; panel['wingspan_ratio']=panel.wingspan_inches/panel.height_wo_shoes_inches
 panel['combine_position']=panel.combine_position.replace('','unknown'); panel['descriptive_ft_pct']=panel.ftm/panel.fta.replace(0,np.nan); panel['join_status']='exact ID'; panel['source_flags']='pinned_archive;Stage3_official_core_anthro;shooting_MIN_validation_pending'; panel['likelihood_eligible']=panel.fta>0
 panel=panel.sort_values(['player_id','season']).reset_index(drop=True)
 for field in ['height_wo_shoes_inches','wingspan_inches','residual_wingspan','combine_year','combine_position']: assert (panel.groupby('player_id')[field].nunique()==1).all()
 paths={'full':ROOT/'data/processed/stage3_multiseason_ft_panel.parquet','replication':ROOT/'data/processed/stage3_primary_replication_panel.parquet'}
 panel.to_parquet(paths['full'],index=False); rep=panel[panel.season!='2013-14'].copy(); rep.to_parquet(paths['replication'],index=False)
 save('primary_replication_panel_summary.json',summary(rep)); save('full_panel_summary.json',summary(panel))
 quality=[]; coverage=[]
 for season,rows in d.groupby('season'):
  measured=rows.player_id.isin(set(vectors.player_id)); p=panel[panel.season==season]
  quality.append(dict(season=season,player_seasons=len(p),unique_players=p.player_id.nunique(),FTA=int(p.fta.sum()),FTA_zero=int((p.fta==0).sum()),FTA_ge50=int((p.fta>=50).sum()),FTA_ge100=int((p.fta>=100).sum()),primary_replication=season!='2013-14'))
  rec=dict(season=season,total_positive_minute_players=len(rows),measured_eligible_players=int(measured.sum()),unmeasured_players=int((~measured).sum()),coverage_rate=float(measured.mean()))
  for label,sub in [('measured',rows[measured]),('unmeasured',rows[~measured])]:
   rec.update({label+'_median_minutes':float(sub.minutes.median()),label+'_mean_minutes':float(sub.minutes.mean()),label+'_median_GP':float(sub.games_played.median()),label+'_mean_GP':float(sub.games_played.mean()),label+'_position_available_fraction':float((sub.position_games>0).mean())})
  coverage.append(rec)
 pd.DataFrame(quality).to_csv(E/'panel_quality_by_season.csv',index=False); pd.DataFrame(coverage).to_csv(E/'selection_coverage_by_season.csv',index=False)
 excluded=d[~d.player_id.isin(vectors.player_id)].copy(); excluded['reason']=excluded.player_id.map(lambda pid:'no validated complete measurement before first observed season' if pid in set(measurements.player_id) else 'no exact-ID validated complete measurement; cross-ID links not applied'); excluded[['player_id','player_name','season','reason']].to_csv(ROOT/'data/interim/stage3_panel_exclusions.csv',index=False)
 gate=json.loads((E/'multi_season_source_validation.json').read_text()); freeze=dict(status='CANDIDATE_HASHED_NOT_RELEASED',part_A_pass=False,part_B_authorized=False,reason='shooting source validation has unresolved minute discrepancies; do not fit',candidate_paths={k:str(p.relative_to(ROOT)) for k,p in paths.items()},candidate_hashes={k:sha(p) for k,p in paths.items()},reference_hash=g['reference_hash'],geometric_intercept=g['intercept'],geometric_slope=g['slope'],residualization_refitted=False,source_protocol_hash=sha(E/'source_validation_protocol.json'),stage1_result_hash=sha(ROOT/'docs/stage1_evidence/primary_result.json'),stage2_result_hash=sha(ROOT/'docs/stage2_evidence/primary_robustness_result.json'),model_executed=False)
 save('panel_freeze.json',freeze)
 print(json.dumps({'replication':summary(rep),'full':summary(panel)},indent=2))
if __name__=='__main__': main()
