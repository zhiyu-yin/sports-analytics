"""Verify Stage 4A artifact assembly only. Never execute historical scientific code."""
from pathlib import Path
from datetime import datetime,timezone
import ast,csv,hashlib,io,json,math,re,sys,unittest
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs/manuscript';F=ROOT/'reports/manuscript'
CACHE={}
def sha(p):
 if p not in CACHE:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  CACHE[p]=h.hexdigest()
 return CACHE[p]
def load(p):return json.loads((ROOT/p).read_text())
def rows(p):
 with (ROOT/p).open(newline='') as f:return list(csv.DictReader(f))
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
f=load('docs/manuscript/manuscript_freeze.json');lineage=load('docs/manuscript/numeric_lineage.json');values=lineage['values'];bindings=lineage['bindings'];emap=rows('docs/manuscript/evidence_map.csv');prose=load('docs/manuscript/prose_lineage.json');receipt=load('docs/manuscript/assembly_receipt.json');dis=rows('docs/manuscript/content_disposition.csv');protected=load('docs/manuscript/prior_preservation_manifest.json')
scripts=[ROOT/'scripts'/n for n in ['stage4a_freeze.py','stage4a_build.py','stage4a_prose.py','stage4a_verify.py']]
# Token audit concerns scientific paragraphs, not headings, filenames or claim identifiers.
number=re.compile(r'(?<![A-Za-z_])[-+]?\d[\d,]*(?:\.\d+)?(?:e[-+]?\d+)?',re.I)
def numbers(text):return [m.group().replace(',','') for m in number.finditer(text)]
def candidate_numbers(path):
 def walk(x):
  if isinstance(x,dict):
   for key,y in x.items():
    if key=='coverage_rate': yield float(y)*100
    yield from walk(y)
  elif isinstance(x,list):
   for y in x: yield from walk(y)
  elif isinstance(x,(int,float)) and not isinstance(x,bool):yield float(x)
  elif isinstance(x,str):
   try:yield float(x)
   except ValueError:
    for n in numbers(x):yield float(n)
 if path.endswith('.csv'):return list(walk(rows(path)))
 if path.endswith('.json'):return list(walk(load(path)))
 return [float(n) for n in numbers((ROOT/path).read_text())]
def quantify():
 audit=[]
 for r in prose:
  pool=[]
  for path in r['sources']:pool.extend(candidate_numbers(path))
  # Explicit display transform for approximately three percent lower odds.
  if 'approximately 3%' in r['text']:
   pool.append(100*(1-load('docs/stage3j_evidence/primary_result.json')['odds_ratio']))
  for token in numbers(re.sub(r'\b(?:Table|Figure) \d+\b','display reference',r['text'])):
   x=float(token);places=len(token.split('.')[1]) if '.' in token and 'e' not in token.lower() else 0
   # Integer tokens require exact integer equality; 'approximately 3%' is separately justified.
   near=any(math.isclose(x,y,rel_tol=1e-12,abs_tol=.500001*10**(-places) if places else 1e-9) for y in pool)
   if token=='3' and 'approximately 3%' in r['text']:near=abs(100*(1-load('docs/stage3j_evidence/primary_result.json')['odds_ratio'])-3)<.005
   if token=='1' and '1/T_i' in r['text']:near=True # defined inverse-season weight, not a fitted result
   audit.append(dict(output=r['output'],claim_id=r['claim_id'],numeric_token=token,source_artifacts=';'.join(r['sources']),passed=near))
 with (D/'quantitative_claim_audit.csv').open('w',newline='') as s:
  w=csv.DictWriter(s,fieldnames=list(audit[0]));w.writeheader();w.writerows(audit)
 return audit

def resolve(v):
 path=v['source_artifact'];data=rows(path) if path.endswith('.csv') else load(path)
 def get(loc):
  y=data
  for k in loc:y=y[k]
  return y
 op=v['operation'];loc=v['source_field']
 if op=='identity':return get(loc)
 if op=='percent':return float(get(loc))*100
 if op in ['min_percent','max_percent']:return (min if op=='min_percent' else max)(float(r[loc[0]]) for r in data)*100
 if op=='integer_ratio':
  a,b=[float(get(z)) for z in v['input_locators']];x=a/b
  assert abs(x-round(x))<1e-8
  return round(x)
 raise AssertionError(op)

def static():
 # Only authored builders are allowed to run. No statistical packages or dynamic execution.
 trees={p:ast.parse(p.read_text()) for p in scripts}
 return trees
class Stage4A(unittest.TestCase):
 def test_A_all_historical_artifacts_unchanged(self):
  for path,h in protected.items():self.assertEqual(sha(ROOT/path),h,path)
 def test_B_J1_hash_unchanged(self):
  self.assertEqual(sha(ROOT/'docs/stage3j_evidence/primary_result.json'),'79b8f461efcc61e0a6e3ff33728fa0d0019839aae03b9809d530f8c9b6906e02')
  self.assertEqual(f['primary_result_artifact_hash'],sha(ROOT/'docs/stage3j_evidence/primary_result.json'))
 def test_C_J2_remediation_hashes_unchanged(self):
  self.assertEqual(sha(ROOT/'docs/stage3jr_evidence/stage3jr_decision.json'),'3151a7cc931ad1ed5f8777130e6dca39eb85b738e96f7fb6ba9ff1c95215fdb8')
  self.assertEqual(sha(ROOT/'docs/stage3jr_evidence/full_bootstrap_summary.json'),f['J2_remediation_artifact_hash'])
  self.assertEqual(load('docs/stage3jr_evidence/full_bootstrap_summary.json')['decision_sha256'],f['J2_remediation_decision_hash'])
 def test_D_panel_hashes_unchanged(self):
  for path,key in [('stage3_primary_replication_panel.parquet','primary_panel_hash'),('stage3_multiseason_ft_panel.parquet','full_panel_hash')]:self.assertEqual(sha(ROOT/'data/processed'/path),f[key])
 def test_E_numeric_sources_and_prose_traceable(self):
  for key,v in values.items():
   self.assertEqual(sha(ROOT/v['source_artifact']),v['sha256'],key);self.assertEqual(resolve(v),v['value'],key)
  for b in bindings:self.assertEqual(str(rows(b['output'])[b['row']][b['column']]),str(values[b['value_id']]['value']),str(b))
  audit=quantify();self.assertFalse([r for r in audit if not r['passed']])
 def test_F_no_new_statistical_fit(self):
  banned={'statsmodels','scipy','pymc','arviz','sklearn','jax','pytensor'}
  for path,tree in static().items():
   for node in ast.walk(tree):
    if isinstance(node,(ast.Import,ast.ImportFrom)):
     names=[node.module or ''] if isinstance(node,ast.ImportFrom) else [n.name for n in node.names]
     self.assertFalse(any(n.split('.')[0] in banned for n in names),str(path))
    if isinstance(node,ast.Call):
     func=node.func;name=func.attr if isinstance(func,ast.Attribute) else func.id if isinstance(func,ast.Name) else ''
     self.assertNotIn(name,{'fit','fit_bb','minimize','root','sample','GLM','eval','exec'},str(path))
  self.assertEqual(receipt['statistical_fits'],0)
 def test_G_no_new_bootstrap(self):
  for path,tree in static().items():
   for node in ast.walk(tree):
    if isinstance(node,ast.Call):
     name=node.func.attr if isinstance(node.func,ast.Attribute) else ''
     self.assertNotIn(name,{'default_rng','choice','resample','bootstrap','randint','normal','quantile','percentile'},str(path))
  self.assertEqual(receipt['bootstrap_runs'],0)
 def test_H_no_new_filtering(self):
  self.assertEqual(receipt['analytical_panels_decoded'],0);self.assertEqual(receipt['new_filters'],0)
  self.assertFalse(any(p.startswith(('data/','models/')) for p in receipt['decoded_inputs']))
  for path,tree in static().items():
   for node in ast.walk(tree):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):self.assertNotIn(node.func.attr,{'read_parquet','read_feather','read_pickle','from_netcdf','read_hdf'},str(path))
 def test_I_development_explicit_when_included(self):
  full=rows('docs/manuscript/main_table3_robustness.csv')[-1];self.assertIn('2013-14 development',full['notes'])
  cov=rows('docs/manuscript/figure4_data.csv');self.assertEqual([r['panel_role'] for r in cov if r['season']=='2013-14'],['development'])
  for name in ['main_table1_sample.md','main_table3_robustness.md','methods_outline.md','results_outline.md']:self.assertIn('development',(D/name).read_text())
 def test_J_primary_excludes_development(self):
  self.assertEqual(f['primary_seasons'],load('docs/stage3j_evidence/analysis_protocol.json')['seasons']);self.assertNotIn('2013-14',f['primary_seasons']);self.assertEqual(len(f['primary_seasons']),13)
  self.assertEqual([r['omitted_season'] for r in rows('docs/manuscript/supp_leave_one_season_out.csv')],f['primary_seasons'])
 def test_K_J1_primary_and_original_points(self):
  self.assertEqual(f['primary_analysis'],'Stage 3J J1')
  table=rows('docs/manuscript/main_table2_primary.csv');point=load('docs/stage3j_evidence/primary_result.json')['beta']
  self.assertEqual([float(r['beta']) for r in table],[point,point]);self.assertEqual([float(r['odds_ratio']) for r in table],[load('docs/stage3j_evidence/primary_result.json')['odds_ratio']]*2)
 def test_L_J2_secondary_and_original_point(self):
  self.assertIn('J2',f['secondary_analysis']);r=rows('docs/manuscript/main_table3_robustness.csv')[1]
  self.assertIn('Secondary',r['notes']);self.assertEqual(float(r['beta']),load('docs/stage3j_evidence/j2_original_fit_audit.json')['beta'])
  self.assertEqual([float(r['ci_low']),float(r['ci_high'])],load('docs/stage3jr_evidence/full_bootstrap_summary.json')['percentile_CI'])
 def test_M_remediation_disclosed(self):
  for name in ['methods_outline.md','results_outline.md','main_table3_robustness.md','supplement_plan.md']:self.assertIn('remediat',(D/name).read_text().lower())
  self.assertTrue(load('docs/stage3jr_evidence/stage3jr_decision.json')['samples_unchanged'])
 def test_N_historical_failures_preserved(self):
  self.assertEqual(load('docs/stage3j_evidence/execution_decision.json')['execution'],'FAIL')
  self.assertEqual(load('docs/stage3jr_evidence/stage3jr_decision.json')['classification'],'NUMERICAL REMEDIATION PASS')
  self.assertEqual(load('docs/stage3c_evidence/execution_status.json')['stage3c_execution'],'FAIL')
  for stage in ['Stage3F','Stage3FR','Stage3H','Stage3I']:self.assertIn('UNRESOLVED',f['historical_decisions'][stage])
  for name in ['results_outline.md','supplement_plan.md','main_table3_robustness.md']:self.assertIn('EXECUTION FAIL',(D/name).read_text())
 def test_O_conclusion_and_limitations(self):
  text=f['approved_core_conclusion'].lower()
  for word in ['causes','effect of wingspan','mechanically','proves','independent-player']:self.assertNotIn(word,text)
  self.assertIn('associated',text)
  discussion=(D/'discussion_outline.md').read_text().lower()
  for concept in ['between players','informative','selection','unmeasured','does not correct']:self.assertIn(concept,discussion)
 def test_P_figures_from_frozen_values_and_visually_checked(self):
  manifest=load('docs/manuscript/figure_manifest.json');review=load('docs/manuscript/visual_review.json')
  for name in manifest['figures']:
   for ext in ['pdf','png']:self.assertTrue((F/(name+'.'+ext)).is_file())
   self.assertEqual(review['files'][name+'.pdf']['sha256'],sha(F/(name+'.pdf')))
   self.assertTrue(review['files'][name+'.pdf']['passed'])
   data='docs/manuscript/'+manifest['source_data'][name];self.assertTrue(any(b['output']==data for b in bindings),data)
  self.assertEqual(manifest['dpi'],400)
 def test_Q_every_numeric_table_cell_bound(self):
  for name in ['main_table1_sample.csv','main_table2_primary.csv','main_table3_robustness.csv','supp_leave_one_season_out.csv','supp_alternate_exposures.csv']:
   path='docs/manuscript/'+name;lookup={(b['row'],b['column']) for b in bindings if b['output']==path}
   for i,row in enumerate(rows(path)):
    for col,value in row.items():
     try:float(value)
     except ValueError:continue
     self.assertIn((i,col),lookup,(path,i,col))
  pos=[r for r in rows('docs/manuscript/main_table1_sample.csv') if r['characteristic'].startswith('Original combine position:')]
  self.assertEqual(sum(int(r['value']) for r in pos),4117)
 def test_R_evidence_map_covers_main_claims(self):
  ids={r['claim_id'] for r in emap};self.assertTrue(set(values)<=ids)
  for r in prose:
   self.assertIn(r['claim_id'],ids);self.assertIn(r['text'],(ROOT/r['output']).read_text())
  for row in emap:self.assertEqual(sha(ROOT/row['source_artifact']),row['source_sha256'])
  # Frozen figure data all use numeric bindings; every factual outline paragraph has a source identifier.
  for name in ['abstract_skeleton.md','methods_outline.md','results_outline.md','discussion_outline.md']:
   for block in (D/name).read_text().split('\n\n'):
    block=block.strip()
    if block.startswith('#') or block.startswith('Evidence identifiers') or not block.strip():continue
    self.assertRegex(block,r'\[[AMRD]\d+\]')
 def test_S_disposition_complete(self):
  hist=rows('docs/manuscript/historical_artifact_disposition.csv');self.assertEqual({r['artifact'] for r in hist},set(protected))
  self.assertEqual({r['disposition'] for r in dis},{'MAIN','SUPPLEMENT','AUDIT_ONLY','NOT_USE'})
  for record in load('docs/manuscript/audit_chain_inventory.json'):self.assertGreater(record['file_count'],0)
  reports=[p for p in protected if re.match(r'docs/stage.*\.md$',p) and '/' not in p[5:]]
  disposition_paths={r['project_output'] for r in dis}
  required=[p for p in reports if p!='docs/stage0c_reproduction.md'];self.assertTrue(set(required)<=disposition_paths)
  self.assertEqual(f['descriptive_exposure_figure']['status'],'REQUIRES FUTURE ANALYSIS')
 def test_T_stage4_scope_and_freeze_chronology(self):
  self.assertEqual(sha(D/'manuscript_freeze.json'),load('docs/manuscript/freeze_receipt.json')['sha256'])
  self.assertLess(f['frozen_at'],load('docs/manuscript/prose_receipt.json')['assembled_at'])
  self.assertFalse(receipt['stage4b_started']);self.assertEqual(receipt['new_thresholds'],0)
  for path,tree in static().items():
   for node in ast.walk(tree):
    if isinstance(node,ast.Import):self.assertFalse(any(n.name in {'subprocess','socket','requests','urllib'} for n in node.names),str(path))
  self.assertFalse(list((ROOT/'scripts').glob('stage4b*')))

def main():
 stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Stage4A))
 (D/'test_run.txt').write_text(stream.getvalue());print(stream.getvalue())
 passed=result.wasSuccessful();classification='PASS — MANUSCRIPT ANALYSIS FROZEN' if passed else 'FAIL — MANUSCRIPT EVIDENCE INCONSISTENCY'
 save(D/'test_summary.json',{'tests':result.testsRun,'passed':result.testsRun-len(result.failures)-len(result.errors),'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'classification':classification,'historical_artifacts':len(protected),'numeric_source_values':len(values),'numeric_output_bindings':len(bindings),'approved_prose_paragraphs':len(prose),'verification_scope':'Artifact integrity, declared assembly code and local outputs. Static guards are not a universal proof about arbitrary external processes.','verified_at':datetime.now(timezone.utc).isoformat()})
 report=ROOT/'docs/stage4a_manuscript_freeze_report.md';text=report.read_text();before,rest=text.split('## 20. Stage 4A decision\n\n');_,after=rest.split('## 21. Recommended Stage 4B\n\n')
 report.write_text(before+'## 20. Stage 4A decision\n\n'+classification+f'. Checks: {result.testsRun-len(result.failures)-len(result.errors)}/{result.testsRun} passed, {len(result.failures)} failures, {len(result.errors)} errors, {len(result.skipped)} skips. All historical evidence is preserved when check A passes. The descriptive exposure-outcome figure remains explicitly deferred, not fabricated.\n\n## 21. Recommended Stage 4B\n\n'+after)
 CACHE.pop(report,None)
 if passed:
  files=list(D.glob('*'))+list(F.glob('*'))+scripts+[report]
  save(D/'build_manifest.json',{'built_at':datetime.now(timezone.utc).isoformat(),'classification':classification,'historical_artifacts':len(protected),'freeze_sha256':sha(D/'manuscript_freeze.json'),'files':{str(p.relative_to(ROOT)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in files if p.is_file() and p.name!='build_manifest.json'}})
 sys.exit(0 if passed else 1)
if __name__=='__main__':main()
