"""Immutable, content-addressed local retrieval; failures are not empty datasets."""
import datetime, hashlib, json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw'
EVIDENCE = ROOT / 'docs/stage0_evidence'

def retrieve(url, source, parameters=None, timeout=25):
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(['curl', '-L', '--silent', '--show-error', '--max-time', str(timeout),
        '-w', '%{stderr}\nHTTP_STATUS:%{http_code}', '-A', 'Mozilla/5.0', '-H', 'Referer: https://www.nba.com/', url], capture_output=True)
    body = result.stdout
    diagnostic=result.stderr.decode(errors='replace')
    http_status=int(diagnostic.rsplit('HTTP_STATUS:',1)[1]) if 'HTTP_STATUS:' in diagnostic else None
    digest = hashlib.sha256(body).hexdigest() if body else None
    path = RAW / (digest + '.payload') if body else None
    RAW.mkdir(parents=True, exist_ok=True)
    if path and not path.exists():
        with path.open('xb') as f: f.write(body)
    meta = dict(source=source,url=url,parameters=parameters or {},retrieved_at=stamp,
                sha256=digest,raw_path=str(path.relative_to(ROOT)) if path else None,
                transport_exit=result.returncode,http_status=http_status,error=diagnostic.split('HTTP_STATUS:')[0].strip(),bytes=len(body))
    key = hashlib.sha256((stamp+url).encode()).hexdigest()[:16]
    (RAW / (key+'.manifest.json')).write_text(json.dumps(meta,indent=2))
    return body, meta

def tables(body):
    data = json.loads(body)
    rs = data.get('resultSets',data.get('resultSet',[]))
    if isinstance(rs,dict): rs=[rs]
    if not isinstance(rs,list): raise ValueError('No NBA result sets')
    output={}
    for r in rs:
        h=r['headers']
        if not all(isinstance(x,str) for x in h):
            output[r['name']]={'schema':h,'row_count':len(r['rowSet']),'rows':None}
        else:
            if any(len(v)!=len(h) for v in r['rowSet']): raise ValueError('Row width mismatch')
            output[r['name']]={'schema':h,'row_count':len(r['rowSet']),'rows':[dict(zip(h,v)) for v in r['rowSet']]}
    if not output: raise ValueError('No NBA result sets')
    return output
