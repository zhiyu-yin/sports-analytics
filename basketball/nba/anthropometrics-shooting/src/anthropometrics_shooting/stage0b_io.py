"""Stage 0B isolated IO. Stage 0 evidence is read-only."""
import csv,hashlib,json,subprocess,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
E0=ROOT/'docs/stage0_evidence'
E=ROOT/'docs/stage0b_evidence'
RAW=ROOT/'data/raw/stage0b'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def csvwrite(path,rows,fields=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0])); w.writeheader(); w.writerows(rows)
def archive(meta):
    p=ROOT/meta['raw_path']
    if sha(p)!=meta['sha256']: raise ValueError('Source checksum mismatch: '+str(p))
    return list(csv.DictReader(p.open()))
def fetch(url,label,timeout=25):
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    RAW.mkdir(parents=True,exist_ok=True)
    r=subprocess.run(['curl','-L','-sS','--max-time',str(timeout),'-A','Mozilla/5.0','-H','Referer: https://www.nba.com/','-w','%{stderr}\nHTTP_STATUS:%{http_code}',url],capture_output=True)
    diag=r.stderr.decode(errors='replace'); status=int(diag.rsplit('HTTP_STATUS:',1)[1]) if 'HTTP_STATUS:' in diag else None
    digest=hashlib.sha256(r.stdout).hexdigest() if r.stdout else None
    p=RAW/(digest+'.payload') if digest else None
    if p and not p.exists():
        with p.open('xb') as f: f.write(r.stdout)
    m=dict(source=label,url=url,retrieval_timestamp=now,http_status=status,transport_exit=r.returncode,error=diag.split('HTTP_STATUS:')[0].strip(),raw_sha256=digest,raw_path=str(p.relative_to(ROOT)) if p else None,bytes=len(r.stdout))
    dump(RAW/(hashlib.sha256((url+now).encode()).hexdigest()[:20]+'.manifest.json'),m)
    return r.stdout,m
