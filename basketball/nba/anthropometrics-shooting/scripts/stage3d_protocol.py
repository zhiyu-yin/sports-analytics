"""Prospective Stage 3D specification, provenance and input checks."""
import json,hashlib,platform,sys,subprocess
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/stage3d_evidence';M=ROOT/'models/stage3d';F=ROOT/'docs/stage3d_figures'
PANEL=ROOT/'data/processed/stage3_primary_replication_panel.parquet'
EXPECTED='1c34331385e459ac5da67105658730d31d96c8114bd25fcb3b31cea52f1a1871'
BINS=[(1,9,'1-9'),(10,49,'10-49'),(50,99,'50-99'),(100,299,'100-299'),(300,None,'300+')]
def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def save(name,value):
 path=E/name;path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def fixed_data():
 assert sha(PANEL)==EXPECTED
 d=pd.read_parquet(PANEL);assert len(d)==4117 and d.player_id.nunique()==857 and d.season.nunique()==13
 assert '2013-14' not in set(d.season) and d.fta.sum()==469099
 assert (d.games_played>0).all() and np.isfinite(np.log(d.games_played)).all()
 assert ((d.ftm>=0)&(d.ftm<=d.fta)&(d.fta%1==0)&(d.ftm%1==0)).all()
 np.testing.assert_array_equal(d.residual_wingspan,d.wingspan_inches-(4.574910520685837+1.0013410045156863*d.height_wo_shoes_inches))
 return d
def protocol():
 p=read(E/'model_adequacy_protocol.json');assert sha(E/'model_adequacy_protocol.json')==read(E/'protocol_freeze_receipt.json')['sha256'];return p
def setup():
 E.mkdir(exist_ok=True);M.mkdir(parents=True,exist_ok=True);F.mkdir(exist_ok=True)
 assert not (E/'model_adequacy_protocol.json').exists(),'Refuse to overwrite frozen protocol'
 preserved={}
 for path in ROOT.rglob('*'):
  rel=path.relative_to(ROOT)
  if not path.is_file() or any(x.startswith('.venv') or x in {'environment','__pycache__','.git'} for x in rel.parts) or 'stage3d' in str(rel):continue
  preserved[str(rel)]=sha(path)
 save('prior_preservation_manifest.json',preserved)
 assert read(ROOT/'docs/stage3c_evidence/execution_status.json')['stage3c_execution']=='FAIL'
 c=read(ROOT/'docs/stage3c_evidence/model_protocol.json');diagnostic=read(ROOT/'docs/stage3c_evidence/primary_diagnostics.json');ppc=read(ROOT/'docs/stage3c_evidence/primary_posterior_predictive_summary.json')
 assert diagnostic['numeric_gate_pass'] and ppc['serious_failure_by_frozen_rule']
 release=read(ROOT/'docs/stage3b_evidence/panel_release_receipt.json')['panels']['replication'];assert release['sha256']==EXPECTED
 d=fixed_data();positive=d[d.fta>0];assert len(positive)==3980
 gp=pd.read_csv(ROOT/'docs/stage3_evidence/shooting_census_crosscheck.csv',dtype={'player_id':str});gp=gp[gp.field=='games_played'];assert len(gp)==1510 and (gp.archive==gp.official).all() and (gp.difference==0).all() and gp['match'].all()
 join=d.merge(gp[['season','player_id','official']],on=['season','player_id'],how='inner');assert (join.games_played==join.official).all()
 save('gp_offset_validation.json',dict(panel_rows=4117,GP_positive=True,log_GP_finite=True,GP_min=int(d.games_played.min()),GP_max=int(d.games_played.max()),official_GP_comparisons=1510,official_GP_exact=True,panel_rows_with_direct_census_match=len(join),validation_seasons=sorted(gp.season.unique()),scope='Exact official validation in three previously audited seasons, not a new universal official census.',offset='log(games_played)',coefficient=1,minutes_used=False,eligibility_changed=False))
 ids=sorted(d.player_id.unique(),key=int);pd.DataFrame({'player_index':range(len(ids)),'player_id':ids}).to_csv(E/'player_index.csv',index=False)
 center=float(np.log1p(d.fta).mean());baseline=pd.read_csv(ROOT/'docs/stage3c_evidence/primary_PPC_metrics.csv');rows=[]
 for lo,hi,label in BINS:
  sub=positive[(positive.fta>=lo)&(True if hi is None else positive.fta<=hi)];rates=sub.ftm/sub.fta;old=baseline.set_index('metric').loc['FTA_'+label+'_pooled']
  value=float(sub.ftm.sum()/sub.fta.sum());assert abs(value-old.observed)<1e-14
  rows.append(dict(bin=label,player_seasons=len(sub),FTA=int(sub.fta.sum()),FTM=int(sub.ftm.sum()),pooled_rate=value,rate_mean=float(rates.mean()),rate_SD=float(rates.std()),rate_Q05=float(rates.quantile(.05)),rate_Q50=float(rates.quantile(.5)),rate_Q95=float(rates.quantile(.95)),fraction_zero=float((rates==0).mean()),fraction_perfect=float((rates==1).mean()),D0_replicated_mean=float(old.replicated_mean),D0_predictive_99_low=float(old.predictive_99_low),D0_predictive_99_high=float(old.predictive_99_high),D0_outside_99=bool(old.outside_99)))
 pd.DataFrame(rows).to_csv(E/'frozen_attempt_volume_problem.csv',index=False)
 save('d0_saved_ppc_summary.json',dict(source='Stage 3C saved PPC; no baseline refit or new simulation',source_sha256=sha(ROOT/'docs/stage3c_evidence/primary_PPC_metrics.csv'),source_draws=1000,sampler_pass=True,pooled_rate_99_pass=False,global_metrics_99_fail_count=2,season_rate_99_fail_count=0,FTA_bin_99_fail_count=sum(x['D0_outside_99'] for x in rows),systematic_volume_pattern=True,systematic_pattern_basis='Both low-bin observed values are below their saved 99% predictive intervals and both high-bin values above; no new baseline MCSE estimated.',overall_adequacy=False,eligible_for_Stage3E=False,original_PPC=ppc,bins=rows,global_rate_mean_unavailable_in_saved_baseline=True))
 shared=dict(intercept=['Normal',0,2.5],residual_wingspan_slope=['Normal',0,.5],height_slope=['Normal',0,.5],position=['Normal',0,1],season=['Normal',0,1],log_kappa=['Normal',3,2])
 candidates={
 'D0':dict(definition='Exact failed Stage 3C; reuse saved diagnostics/PPC without refitting',eligible=False),
 'D1':dict(definition='Stage 3C accuracy mean plus gamma_FTA * centered_log1p_FTA',eligible=False,priors=dict(shared_accuracy=shared,sigma_player=['HalfNormal',1],gamma_FTA=['Normal',0,.5]),sampling=dict(chains=4,tune=1500,draws=1500,target_accept=.95,seed=20260928)),
 'D2':dict(definition='Unchanged Stage 3C accuracy mean; log(kappa_it)=gamma_0 + gamma_k * centered_log1p_FTA',eligible=False,priors=dict(shared_accuracy={k:v for k,v in shared.items() if k!='log_kappa'},sigma_player=['HalfNormal',1],gamma_0=['Normal',3,2],gamma_k=['Normal',0,.5]),sampling=dict(chains=4,tune=1500,draws=1500,target_accept=.95,seed=20260928)),
 'D3':dict(definition='Joint NegativeBinomial FTA with fixed log(GP) offset and BetaBinomial FTM|FTA; correlated non-centered player opportunity/accuracy intercepts',eligible=True,accuracy_rows=3980,opportunity_rows=4117,accuracy_priors=shared,opportunity_priors=dict(a_0=['Normal',0,2.5],a_RW=['Normal',0,.5],a_H=['Normal',0,.5],a_position=['Normal',0,1],a_season=['Normal',0,1],alpha_FTA=['HalfNormal',5]),random_effects=dict(construction='LKJCholeskyCov; [u,v]=z @ chol.T; rows=players, columns=[accuracy,opportunity]',eta=2,SD_priors=['HalfNormal',1],noncentered=True),sampling=dict(chains=4,tune=2000,draws=2000,target_accept=.95,seed=20260928),recovery=dict(max_runs=1,target_accept=.99,tune=4000,draws=4000,trigger='Generic sampler diagnostic failure only'))}
 p=dict(frozen_at=now(),purpose='Attempt-volume/model-adequacy investigation, not a new scientific exposure test',primary_panel_sha256=EXPECTED,accounting=dict(seasons=13,rows=4117,players=857,FTA=469099,positive_FTA=3980,zero_FTA=137),height_center=c['height_center'],log1p_FTA_center=center,center_population='All 4117 primary accounting rows including zero FTA; outcomes not used',positions=c['position_levels'],position_reference='C',seasons=c['season_levels'],season_reference=c['season_reference'],frozen_exposure=c['residualization'],bins=BINS,candidates=candidates,
  prior_predictive=dict(draws=2000,seed=20260928,order=['D1','D2','D3'],all_prior_checks_before_any_posterior=True,accuracy_gate='Same gross screen as Stage 3C: all mu finite; at most 25% below .01 and at most 25% above .99',opportunity_gate=dict(all_finite_nonnegative_integer=True,max_fraction_implied_rate_over_100_per_game=.01,max_fraction_simulated_count_over_1000000=.001),rationale='100 expected FTA per player per game is an intentionally very generous gross-scale bound, not an empirical NBA record or a fit target. More than 1% prior mass above that sustained rate, or more than 0.1% simulated seasons above one million attempts, is grossly implausible. Neither bound is derived from the observed accuracy association.',failure_action='STOP before any outcome posterior fitting. Retain the suggested priors and record the failure; no automatic prior amendment in this run.'),
  diagnostics=dict(max_rhat=1.01,min_bulk_ESS=400,min_tail_ESS=400,max_divergences=0,max_treedepth_hits=0,min_BFMI=.3,finite_covariance=True,visual_review=True,sealed_parameter_handling='Include anonymous convergence diagnostics for the sealed slope; never export its location, scale, interval, sign or posterior probability; no raw trace plot of that parameter'),
  PPC=dict(draws=2000,seed=20260929,global_metrics=['rate_mean','rate_SD','rate_q05','rate_q50','rate_q95','rate_zero_fraction','rate_one_fraction'],accuracy_failure_rules=dict(pooled_outside_99=True,global_outside_99_at_least=3,season_outside_99_fraction=1/3,FTA_bin_outside_99_at_least=2,systematic_directional_pattern=True),pattern_definition='For each bin, bias=replicate mean minus observed. Evidence of direction requires abs(bias)>2.576*MCSE(replica mean), MCSE estimated by 40 consecutive batch means of 50 replicates in chain-major draw order. Both low bins same sign and both high bins opposite sign triggers failure. This is Monte Carlo uncertainty, not posterior predictive interval width.',joint_failure_rules=dict(zero_fraction_outside_99=True,quantiles=[.25,.5,.75,.9,.95],quantiles_outside_99_at_least=3,season_total_gross_rule='At least ceil(n_seasons/3) season totals outside 99% predictive intervals in the same direction'),conditional_accuracy='Hold observed FTA fixed, using joint posterior',joint_generation='Simulate all FTA then FTM conditional on simulated FTA and the same correlated player draw',opportunity_checks=['overall distribution','season distributions/totals','original-position distributions','zero fraction','Q25','Q50','Q75','Q90','Q95'],baseline_policy='Reuse original 1000 saved D0 replications; no re-evaluation to seek a different baseline outcome'),
  selection=dict(only_eligible='D3',inputs='Typed gate booleans/counts only; no parameter summaries or traces',requires=['prior_pass','sampler_pass','conditional_accuracy_pass','joint_opportunity_pass','no_posthoc_change','firewall_intact'],D1_D2_diagnostic_only=True,add_candidates_after_results=False,scientific_parameter_status='SEALED_PENDING_STAGE3E'),
  prohibitions=['full_panel','2013-14','FTA_threshold_filter','alternate_exposure','grouped_position','leave_one_season_out','new_confounders','minutes_predictor','scientific_effect_unsealing','Stage3E_execution'],minute_limitation=c['minute_limitation'],prior_amendments=[],prior_stage3c_status='EXECUTION FAIL — PRIMARY PPC ADEQUACY GATE FAILED')
 save('model_adequacy_protocol.json',p);save('protocol_freeze_receipt.json',dict(frozen_at=p['frozen_at'],sha256=sha(E/'model_adequacy_protocol.json')))
 for key in ['D1','D2','D3']:save(key.lower()+'_protocol.json',dict(frozen_at=p['frozen_at'],parent_protocol_sha256=sha(E/'model_adequacy_protocol.json'),**candidates[key]))
 from importlib.metadata import version
 env=dict(python=platform.python_version(),executable=sys.executable,packages={x:version(x) for x in ['pymc','arviz','numpy','scipy','pandas','pyarrow','matplotlib','pytensor','numba','llvmlite','h5py']},environment_policy='Reuse the pinned Stage 3C environment without installations or modifications; Stage 3D caches and outputs are separate')
 req=ROOT/'requirements-stage3d.txt';req.write_bytes((ROOT/'requirements-stage3c.txt').read_bytes());env['requirements_sha256']=sha(req);save('environment.json',env)
 check=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True);(E/'pip_check.txt').write_text(check.stdout+check.stderr);assert check.returncode==0
 print(json.dumps(dict(protocol_sha256=sha(E/'model_adequacy_protocol.json'),historical_artifacts_protected=len(preserved),log1p_FTA_center=center,GP_checks=read(E/'gp_offset_validation.json')),indent=2))
if __name__=='__main__':setup()
