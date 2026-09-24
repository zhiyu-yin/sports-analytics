from pathlib import Path
import json, subprocess, time, datetime, hashlib
root=Path('/Users/zhiyuyin/Documents/last time job hunting material/proj/sports-analytics/basketball/nba/game-prediction')
out=root/'docs/stage0_evidence'
manifest=json.loads((out/'manifest.json').read_text())
headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36','Accept':'application/json, text/plain, */*','Accept-Language':'en-US,en;q=0.5','Referer':'https://www.nba.com/','Pragma':'no-cache','Cache-Control':'no-cache','Sec-Ch-Ua':'"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"','Sec-Ch-Ua-Mobile':'?0','Sec-Fetch-Dest':'empty'}
url=manifest[0]['url']
cmd=['curl','-sS','--compressed','--max-time','25','-o',str(out/'leaguegamelog_current_headers.json'),'-w','%{http_code}']
for k,v in headers.items(): cmd += ['-H', k+': '+v]
start=time.monotonic(); r=subprocess.run(cmd+[url],capture_output=True,text=True)
record=dict(name='leaguegamelog_current_headers',url=url,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=round(time.monotonic()-start,2),curl_exit=r.returncode,http_status=r.stdout,error=r.stderr.strip(),headers=headers)
p=out/'leaguegamelog_current_headers.json'
if p.exists(): record.update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
manifest.append(record); (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n'); print(record)
