"""Read-only evidence assembly. No model library, sampling, or analytical panel access."""
from pathlib import Path
from datetime import datetime, timezone
import csv, hashlib, json, math, sys
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'docs/manuscript'; F=ROOT/'reports/manuscript'
J='docs/stage3j_evidence/'; JR='docs/stage3jr_evidence/'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads((ROOT/p).read_text())
def save(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def csvread(p):
 with (ROOT/p).open(newline='') as f: return list(csv.DictReader(f))
def csvwrite(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
SOURCES={}; VALUES={}; BINDINGS=[]; MAP=[]
def source(path):
 if path not in SOURCES:
  assert '/models/' not in path and not path.startswith(('models/','data/'))
  SOURCES[path]={'sha256':sha(ROOT/path),'data':csvread(path) if path.endswith('.csv') else load(path)}
 return SOURCES[path]['data']
def val(key,path,locator,operation='identity',locators=None):
 x=source(path)
 def get(loc):
  y=x
  for p in loc: y=y[p]
  return y
 if operation=='identity': out=get(locator)
 elif operation=='percent': out=float(get(locator))*100
 elif operation=='integer_ratio':
  a,b=[float(get(k)) for k in locators]; raw=a/b
  assert abs(raw-round(raw))<1e-8
  out=round(raw)
 elif operation in ('min_percent','max_percent'):
  vs=[float(y[locator[0]]) for y in x];out=(min(vs) if operation=='min_percent' else max(vs))*100
 else: raise ValueError(operation)
 VALUES[key]={'value':out,'source_artifact':path,'source_field':locator,'operation':operation,'input_locators':locators,'sha256':SOURCES[path]['sha256']}
 return out

def bind(rows,row,col,key):
 rows[row][col]=VALUES[key]['value'];BINDINGS.append({'output':None,'row':row,'column':col,'value_id':key})
def write_bound(name,rows,start):
 csvwrite(D/name,rows)
 for x in BINDINGS[start:]: x['output']='docs/manuscript/'+name

def evidence(section,cid,summary,path,field,wording,role='primary',split='replication',limitations='Between-player association; selection and informative opportunity remain.'):
 MAP.append(dict(manuscript_section=section,claim_id=cid,claim_summary=summary,source_artifact=path,source_field_line_table=field,primary_or_secondary=role,development_or_replication=split,limitations=limitations,approved_wording=wording,source_sha256=sha(ROOT/path)))
def mdtable(cols,rows): return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n'
def fmt(x): return f'{float(x):.6f}'

def assemble():
 freeze=load('docs/manuscript/manuscript_freeze.json'); assert sha(D/'manuscript_freeze.json')==load('docs/manuscript/freeze_receipt.json')['sha256']
 p=source(J+'primary_result.json'); b=source(JR+'full_bootstrap_summary.json'); protocol=source(J+'analysis_protocol.json')
 # Original points are retained in every bootstrap row.
 specs=[('Primary grouped-binomial model',J+'primary_result.json',None,'Player-cluster CR1','Primary; development season excluded'),('Primary grouped-binomial model (bootstrap)',J+'primary_result.json',None,'Player bootstrap percentile','Same original primary point estimate'),('Beta-binomial robustness',J+'j2_original_fit_audit.json',None,'Remediated player bootstrap percentile','Secondary; Stage 3J-R numerical remediation'),('First eligible season only',J+'j3_first_season_result.json',None,'HC1','First eligible replication season; zeros not replaced'),('Player-balanced weighting',J+'j4_player_balanced_result.json',None,'Player-cluster CR1','1/T_i likelihood weights; information not equalized'),('FTA >=50 sensitivity',J+'j6_fta_thresholds.csv',0,'Player-cluster CR1','Frozen secondary threshold'),('FTA >=100 sensitivity',J+'j6_fta_thresholds.csv',1,'Player-cluster CR1','Frozen secondary threshold'),('Full panel including development',J+'full_panel_secondary_result.json',None,'Player-cluster CR1','Includes 2013-14 development; not independent replication')]
 robust=[]
 for i,(label,path,index,method,note) in enumerate(specs):
  row={'analysis':label,'beta':None,'odds_ratio':None,'ci_low':None,'ci_high':None,'uncertainty_method':method,'player_seasons':None,'players':None,'contributing_players':None,'FTA':None,'notes':note}
  robust.append(row)
  for field in ['beta','odds_ratio','ci_low','ci_high','player_seasons','players','contributing_players','FTA']:
   loc=([index] if index is not None else [])+[field]; sp=path
   if i in (1,2) and field.startswith('ci_'):
    sp=J+'primary_result.json' if i==1 else JR+'full_bootstrap_summary.json'
    loc=(['bootstrap'] if i==1 else [])+['percentile_CI',0 if field=='ci_low' else 1]
   key=f'robust_{i}_{field}';val(key,sp,loc);row[field]=VALUES[key]['value']
 # Same evidence-backed result records feed both CSVs and figure.
 for name,indices in [('main_table2_primary.csv',[0,1]),('main_table3_robustness.csv',[0,2,3,4,5,6,7]),('figure2_data.csv',list(range(8)))]:
  rows=[dict(robust[i]) for i in indices];start=len(BINDINGS)
  for r,i in enumerate(indices):
   for field in ['beta','odds_ratio','ci_low','ci_high','player_seasons','players','contributing_players','FTA']: bind(rows,r,field,f'robust_{i}_{field}')
  write_bound(name,rows,start)
  rendered=[]
  for r in rows:
   rendered.append([r['analysis'],fmt(r['beta']),fmt(r['odds_ratio']),f"[{fmt(r['ci_low'])}, {fmt(r['ci_high'])}]",r['uncertainty_method'],r['player_seasons'],r['players'],r['FTA']])
  if not name.startswith('figure'):
   title='Primary residual-wingspan association' if 'table2' in name else 'Predeclared robustness analyses'
   note='Beta and its 95% CI are log odds per residual inch. Player-seasons and players are accounting counts; contributing-player counts are retained in CSV. FTA totals are unweighted.'
   if 'table2' in name: note+=f" Both rows use the original primary point estimate. Bootstrap mean {p['bootstrap']['mean']:.8f}, SD {p['bootstrap']['SD']:.8f}; these are resampling summaries, not a second estimator. CR1 p={p['p']:.8f}."
   else: note+=' Beta-binomial is secondary: original full-sample point estimate with the separately remediated bootstrap interval. Historical Stage 3J remains EXECUTION FAIL; Stage 3J-R is NUMERICAL REMEDIATION PASS. The full panel includes the 2013-14 development season and is not independent replication. First-season analysis uses 803 contributing players; player-balanced weights do not equalize total player information.'
   (D/name.replace('.csv','.md')).write_text('# '+title+'\n\n'+mdtable(['Analysis','Beta / inch','OR / inch','95% beta CI','Uncertainty','Player-seasons','Players','FTA'],rendered)+'\n'+note+'\n\nSource: evidence_map.csv, numeric claim IDs robust_*. Exact values are retained in CSV.\n')
 # Table 1, independent persons for anthropometrics; rows for position and FTA.
 rows=[];start=len(BINDINGS)
 def sample_cell(label,key,path,loc,unit='count',operation='identity',locators=None):
  n=len(rows);rows.append({'characteristic':label,'value':None,'unit_or_population':unit});val(key,path,loc,operation,locators);bind(rows,n,'value',key)
 for label,field in [('Replication seasons','seasons'),('Accounting player-seasons','player_seasons'),('Unique accounting players','players'),('Contributing players','contributing_players'),('Positive-FTA player-seasons','positive_FTA_rows'),('Zero-FTA player-seasons','zero_FTA_rows'),('Total free-throw attempts','FTA')]:sample_cell(label,'sample_'+field,J+'primary_result.json',[field])
 anth=source(J+'sample_anthropometrics_unique_players.csv')
 for i,label in enumerate(['Barefoot height','Wingspan','Residual wingspan']):
  for metric in ['mean','std']: sample_cell(label+' '+('SD' if metric=='std' else metric),f'anth_{i}_{metric}',J+'sample_anthropometrics_unique_players.csv',[i,metric],'inches; 857 unique accounting players')
 covpath=J+'selection_coverage_by_season.csv'
 sample_cell('Measurement coverage minimum','coverage_min',covpath,['coverage_rate'],'percent of positive-minute players by season; 14 seasons incl. development','min_percent')
 sample_cell('Measurement coverage maximum','coverage_max',covpath,['coverage_rate'],'percent of positive-minute players by season; 14 seasons incl. development','max_percent')
 obsfile='docs/stage3dr_evidence/d3_joint_PPC_metrics.csv';obs=source(obsfile);where={r['metric']:i for i,r in enumerate(obs)}
 for field,label in [('FTA_mean','FTA mean'),('FTA_SD','FTA SD'),('FTA_q25','FTA Q1'),('FTA_q50','FTA median'),('FTA_q75','FTA Q3')]:sample_cell(label,field,obsfile,[where[field],'observed'],'attempts; all 4117 accounting player-seasons')
 position=[]
 for pos in protocol['positions']:
  a=[where['position_'+pos+'_total'],'observed'];bb=[where['position_'+pos+'_mean'],'observed'];key='position_'+pos
  sample_cell('Original combine position: '+pos,key,obsfile,a,'accounting player-seasons; recovered frozen denominator','integer_ratio',[a,bb]);position.append(VALUES[key]['value'])
 assert sum(position)==p['player_seasons']
 write_bound('main_table1_sample.csv',rows,start)
 compact=[[r['characteristic'],f"{float(r['value']):.2f}" if r['unit_or_population'].startswith(('inches','percent','attempts')) else str(r['value']),r['unit_or_population']] for r in rows]
 (D/'main_table1_sample.md').write_text('# Study sample characteristics\n\nPrimary: 2010-11, 2011-12, 2012-13, and 2014-15 through 2023-24. The 2013-14 development season is excluded.\n\n'+mdtable(['Characteristic','Value','Unit / denominator'],compact)+'\nAnthropometric SDs are sample SDs across unique accounting players. Position counts and FTA distributions describe accounting player-seasons, including zero attempts; they are not unique-player position counts. Position denominators are recovered from existing observed position FTA totals divided by existing observed means, checked to be integer-valued and to sum to the accounting panel. No predictive fields from the failed historical model are used. Measurement coverage displays the approved full season series, explicitly including development; its extrema also occur in replication seasons. No new analytical panel was opened or filtered.\n\nEvidence: sample_*, anth_*, coverage_*, FTA_*, position_* in evidence_map.csv.\n')
 # LOSO complete rows, exact copied values, summary stored in separate fields on every row.
 lpath=J+'j5_leave_one_season_out.csv';lrows=source(lpath);out=[];start=len(BINDINGS)
 for i,row in enumerate(lrows):
  out.append({'omitted_season':row['omitted_season'],'beta':None,'odds_ratio':None,'ci_low':None,'ci_high':None,'range_min_beta':None,'range_max_beta':None,'median_beta':None,'sign_reversals':None})
  for field in ['beta','odds_ratio','ci_low','ci_high']:
   key=f'loso_{i}_{field}';val(key,lpath,[i,field]);bind(out,i,field,key)
  for target,field in [('range_min_beta','min_beta'),('range_max_beta','max_beta'),('median_beta','median_beta'),('sign_reversals','sign_reversals')]:
   key='loso_'+field;val(key,J+'loso_summary.json',[field]);bind(out,i,target,key)
 write_bound('supp_leave_one_season_out.csv',out,start)
 (D/'supp_leave_one_season_out.md').write_text('# Leave-one-season-out sensitivity\n\n'+mdtable(['Omitted season','Beta','OR','95% cluster CI'],[[r['omitted_season'],fmt(r['beta']),fmt(r['odds_ratio']),f"[{fmt(r['ci_low'])}, {fmt(r['ci_high'])}] "] for r in out])+f"\nRange [{VALUES['loso_min_beta']['value']:.8f}, {VALUES['loso_max_beta']['value']:.8f}]; median {VALUES['loso_median_beta']['value']:.8f}; sign reversals {VALUES['loso_sign_reversals']['value']}. Chronological order; the primary panel itself omits no replication season. [Evidence: loso_*]\n")
 # Secondary exposures, already saved scaled ratio fields.
 out=[];start=len(BINDINGS);ap=J+'alternate_exposures_detail.json'
 for i,label in enumerate(['Wingspan advantage, per inch','Wingspan ratio, per 0.01']):
  out.append({'exposure':label,'beta':None,'odds_ratio':None,'ci_low':None,'ci_high':None})
  for field in ['beta','odds_ratio','ci_low','ci_high']:
   key=f'alt_{i}_{field}';val(key,ap,[i]+(['per_001'] if i==1 else [])+[field]);bind(out,i,field,key)
 write_bound('supp_alternate_exposures.csv',out,start)
 # Coverage and observed/fitted diagnostics copied as display data with numeric lineage.
 for name,path,fields in [('figure4_data.csv',covpath,['total_positive_minute_players','measured_eligible_players','coverage_rate']),('supp_figure1_data.csv',J+'residual_diagnostics_by_fta_bin.csv',['player_seasons','FTA','FTM','observed_rate','fitted_rate','observed_minus_fitted'])]:
  old=source(path);out=[];start=len(BINDINGS)
  for i,r in enumerate(old):
   label='season' if 'coverage' in path else 'group';out.append({label:r[label],**{field:None for field in fields}})
   if label=='season':out[-1]['panel_role']='development' if r[label]=='2013-14' else 'replication'
   for field in fields:
    key=f'{name}_{i}_{field}';val(key,path,[i,field]);bind(out,i,field,key)
  write_bound(name,out,start)
 # Flow uses independently frozen source accounting, not invented attrition.
 flow=[];start=len(BINDINGS)
 for label,path,field in [('Observed NBA players, 14-season window','docs/stage3_evidence/shooting_archive_provenance.json','unique_players'),('Positive-minute player-seasons, 14 seasons','docs/stage3_evidence/shooting_archive_provenance.json','player_seasons'),('Measurement-eligible exact-ID player-seasons',J+'full_panel_secondary_result.json','player_seasons'),('Measured players, 14-season panel',J+'full_panel_secondary_result.json','players'),('Primary replication player-seasons',J+'primary_result.json','player_seasons'),('Primary accounting players',J+'primary_result.json','players'),('Primary positive-FTA likelihood rows',J+'primary_result.json','positive_FTA_rows'),('Primary contributing players',J+'primary_result.json','contributing_players'),('Primary zero-FTA accounting rows',J+'primary_result.json','zero_FTA_rows'),('Primary attempts',J+'primary_result.json','FTA')]:
  i=len(flow);flow.append({'quantity':label,'value':None});key=f'flow_{i}';val(key,path,[field]);bind(flow,i,'value',key)
 write_bound('figure1_data.csv',flow,start)
 # Additional exact statistical and validation facts used in prose.
 for field in ['mean','SD','fraction_beta_negative','replicates','failed']:
  val('primary_boot_'+field,J+'primary_result.json',['bootstrap',field]);val('j2_boot_'+field,JR+'full_bootstrap_summary.json',[field])
 for field in ['p','or_low','or_high']:val('primary_'+field,J+'primary_result.json',[field])
 for field in ['kappa','rho']:val('j2_'+field,J+'j2_original_fit_audit.json',[field])
 for field in ['intercept','slope']:val('geometry_'+field,J+'analysis_protocol.json',['residualization',field])
 for field in ['preselected_players','exact_pairs','sourcewide_rows','sourcewide_complete_pairs','reference_population']:val('validation_'+field,'docs/stage0c_evidence/validation_summary.json',[field])
 for k,v in VALUES.items():
  section='Main tables/figures and Methods/Results' if not k.startswith(('alt_','supp_')) else 'Supplement'
  evidence(section,k,'Frozen quantitative value',v['source_artifact'],json.dumps({'locator':v['source_field'],'operation':v['operation'],'input_locators':v['input_locators']}),str(v['value']),role='primary' if k.startswith(('sample','anth','primary','robust_0','robust_1')) else 'secondary/descriptive',split='development included and labeled' if k.startswith(('robust_7','figure4','flow_0','flow_1','flow_2','flow_3','coverage')) else 'replication or source validation',limitations='Display arithmetic only; see source and table denominator. Not a causal estimate.')
 save(D/'numeric_lineage.json',{'values':VALUES,'bindings':BINDINGS})
 save(D/'build_inputs.json',{p:v['sha256'] for p,v in SOURCES.items()})
 csvwrite(D/'evidence_map.csv',MAP)
 return robust,freeze

def figures(robust,freeze):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.style.use('grayscale')
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none','savefig.dpi':400})
 rendered=[]
 def finish(fig,name):
  for ext in ['pdf','png']:fig.savefig(F/(name+'.'+ext),bbox_inches='tight',pad_inches=.12)
  rendered.append(name);plt.close(fig)
 fig,ax=plt.subplots(figsize=(6.6,7.2));ax.set_axis_off();ax.set(xlim=(0,1),ylim=(0,1))
 nums=[int(r['value']) for r in csvread('docs/manuscript/figure1_data.csv')]
 boxes=[f'Observed NBA archive population\n2010-11 through 2023-24: {nums[0]:,} players',f'Positive-minute season eligibility\n{nums[1]:,} player-seasons across 14 seasons',f'Usable combine measurement + exact-ID linkage\n{nums[2]:,} player-seasons; {nums[3]:,} players\nFixed pre-first-observed-season measurement vector',f'Primary replication panel\n2013-14 development season excluded\n13 seasons; {nums[4]:,} player-seasons; {nums[5]:,} players',f'Positive-FTA likelihood\n{nums[6]:,} player-seasons; {nums[7]:,} contributing players\n{nums[9]:,} attempts']
 ys=[.90,.71,.51,.30,.09]
 for i,(y,t) in enumerate(zip(ys,boxes)):
  ax.text(.5,y,t,ha='center',va='center',fontsize=10,bbox=dict(boxstyle='round,pad=.7',facecolor='white',edgecolor='black',linewidth=.8))
  if i<4: ax.annotate('',xy=(.5,ys[i+1]+.073),xytext=(.5,y-.07),arrowprops=dict(arrowstyle='->',linewidth=.8))
 fig.suptitle('Study population and analytical flow',fontsize=12,y=1.01)
 fig.text(.5,-.035,'Eligibility and linkage are a joint intersection; separate attrition counts are not available.\n137 zero-FTA rows remain in primary accounting and bootstrap membership.\nThe full measured panel includes the 2013-14 development season.',ha='center',fontsize=8)
 finish(fig,'figure1_study_flow')
 fig,ax=plt.subplots(figsize=(7.0,4.5));y=list(range(8))
 labels=['Primary: player-cluster CR1','Primary: player bootstrap','Beta-binomial: remediated bootstrap','First eligible season only (HC1)','Player-balanced weighting','FTA >=50 sensitivity','FTA >=100 sensitivity','Full panel (includes development)']
 for i,r in enumerate(robust):
  beta=float(r['beta']);ax.errorbar(beta,i,xerr=[[beta-float(r['ci_low'])],[float(r['ci_high'])-beta]],fmt='o',capsize=3,markersize=4,linewidth=1,color='black')
 ax.axvline(0,linestyle='--',linewidth=.8);ax.set_yticks(y,labels);ax.invert_yaxis();ax.set(xlim=(-.065,.005),xlabel='Log-odds coefficient per residual-wingspan inch',title='Primary association and predeclared robustness')
 fig.text(.5,.015,'Points retain original full-sample estimates; bars show 95% intervals.\nNegative values indicate lower FT odds with greater residual wingspan.\nFull panel includes the 2013-14 development season; beta-binomial remains secondary.',ha='center',fontsize=8)
 fig.tight_layout(rect=(0,.17,1,1));finish(fig,'figure2_robustness_forest')
 loso=csvread('docs/manuscript/supp_leave_one_season_out.csv');fig,ax=plt.subplots(figsize=(4.8,5.2))
 for i,r in enumerate(loso):
  beta=float(r['beta']);ax.errorbar(beta,i,xerr=[[beta-float(r['ci_low'])],[float(r['ci_high'])-beta]],fmt='o',capsize=3,markersize=4,linewidth=1,color='black')
 ax.axvline(float(robust[0]['beta']),linestyle=':',linewidth=1,label='Primary estimate');ax.axvline(0,linestyle='--',linewidth=.8)
 ax.set_yticks(range(13),[r['omitted_season'] for r in loso]);ax.invert_yaxis();ax.set(xlim=(-.06,.003),ylabel='Omitted season',xlabel='Log-odds coefficient per residual inch',title='Leave-one-season-out sensitivity');# Dotted primary reference is explained in the caption
 fig.text(.5,.015,'Bars: 95% player-cluster CR1 intervals. Dotted line: primary estimate.\nAll 13 estimates are negative; development is excluded throughout.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.12,1,1));finish(fig,'figure3_leave_one_season_out')
 c=csvread('docs/manuscript/figure4_data.csv');fig,ax=plt.subplots(figsize=(5.2,4.7));values=[float(r['coverage_rate'])*100 for r in c]
 bars=ax.barh(range(14),values,edgecolor='black',linewidth=.5)
 for i,r in enumerate(c):
  if r['panel_role']=='development':
   bars[i].set_facecolor('white');bars[i].set_hatch('///')
  ax.text(values[i]+1,i,f'{values[i]:.1f}%',va='center',fontsize=8)
 ax.set_yticks(range(14),[r['season']+(' (development)' if r['panel_role']=='development' else '') for r in c]);ax.invert_yaxis();ax.set(xlim=(0,100),xlabel='Positive-minute players with usable measurements (%)',title='Measurement coverage across seasons')
 fig.text(.5,.015,'Approved season-specific coverage; denominator is all positive-minute players.\nHatched bar identifies development. Primary replication excludes that season.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.12,1,1));finish(fig,'figure4_selection_coverage')
 d=csvread('docs/manuscript/supp_figure1_data.csv');fig,ax=plt.subplots(figsize=(4.7,3.8))
 ax.plot(range(5),[float(r['observed_rate'])*100 for r in d],marker='o',label='Observed pooled rate')
 ax.plot(range(5),[float(r['fitted_rate'])*100 for r in d],marker='s',linestyle='--',label='Fitted pooled rate')
 ax.set_xticks(range(5),[r['group'] for r in d]);ax.set(ylim=(60,85),xlabel='Frozen player-season FTA bin',ylabel='Made free throws (%)',title='Attempt-volume calibration');ax.legend(frameon=False,fontsize=8)
 fig.text(.5,.015,'Rates are weighted by attempts, not averages of player-season percentages.\nExisting primary-model diagnostics; no model was refitted.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.16,1,1));finish(fig,'supp_figure1_attempt_volume_diagnostic')
 save(D/'figure_manifest.json',{'figures':rendered,'source_data':dict(zip(rendered,['figure1_data.csv','figure2_data.csv','supp_leave_one_season_out.csv','figure4_data.csv','supp_figure1_data.csv'])),'scale':'log-odds coefficient per residual inch for forest plots','dpi':400,'pdf_vector':True,'style':'matplotlib grayscale; one axes per figure','frozen_result_only':True})

if __name__=='__main__':
 r,f=assemble();figures(r,f)
 save(D/'assembly_receipt.json',dict(completed_at=datetime.now(timezone.utc).isoformat(),freeze_sha256=sha(D/'manuscript_freeze.json'),decoded_inputs=list(SOURCES),statistical_fits=0,bootstrap_runs=0,analytical_panels_decoded=0,new_filters=0,new_thresholds=0,stage4b_started=False))
 print('Created evidence-linked tables and five PDF/PNG figures.')
