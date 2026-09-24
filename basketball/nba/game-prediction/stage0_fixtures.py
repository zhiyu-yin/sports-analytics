"""Inspect upstream recorded API bodies, not live NBA responses; never replay cookies."""
import json, re, subprocess, hashlib, datetime
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'docs/stage0_evidence'
cases={
 'recorded_teamgamelog':'tests/integration/scenarios/cassettes/test_teamgamelog[Date range filter].yaml',
 'recorded_leaguegamefinder':'tests/integration/scenarios/cassettes/test_leaguegamefinder[Date range filter (issue #526) - DateFrom-DateTo work correctly].yaml',
 'recorded_advanced':'tests/integration/smoke/cassettes/test_endpoints[BoxScoreAdvancedV3].yaml',
 'recorded_four_factors':'tests/integration/smoke/cassettes/test_endpoints[BoxScoreFourFactorsV3].yaml'}
records=[]
for name,path in cases.items():
 url='https://raw.githubusercontent.com/swar/nba_api/master/'+quote(path,safe='/')
 r=subprocess.run(['curl','-fsS','--max-time','20',url],capture_output=True,text=True)
 if r.returncode: raise RuntimeError(r.stderr)
 # These inspected VCR files contain single-quoted YAML scalars with folded lines.
 m=re.search(r"      string: '((?:[^']|'')*)'\n",r.stdout)
 if m:
  body=re.sub(r'\n +',' ',m.group(1)).replace("''", "'")
 else:
  scalar=r.stdout.split('      string: ',1)[1].split('\n    headers:',1)[0].strip()
  scalar=re.sub(r'\\\n +','',scalar)
  body=json.loads(re.sub(r'\n +',' ',scalar))
 obj=json.loads(body)
 raw=(json.dumps(obj,indent=2)+'\n').encode(); (OUT/(name+'.json')).write_bytes(raw)
 request=re.search(r'    uri: (.+)',r.stdout)
 records.append(dict(name=name,source_url=url,source_sha256=hashlib.sha256(r.stdout.encode()).hexdigest(),body_sha256=hashlib.sha256(raw).hexdigest(),original_request=request.group(1) if request else None,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),note='Upstream recorded fixture; not a live NBA response in this audit. Request cookies deliberately not retained.'))
 print(name, list(obj),len(raw))
(OUT/'fixture_provenance.json').write_text(json.dumps(records,indent=2)+'\n')
