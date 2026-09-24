"""One-shot authorized transport process; launch only with -I -S.
SSL is initialized before the unchanged project policy. No scientific execution.
"""
import ssl,socket  # Deliberately before adding project/site-package paths.
ORIGINAL_SOCKET=socket.socket
import sys,os,json,hashlib,time,contextlib,tempfile,subprocess,threading
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/stage6r_evidence'
AUTH='8337cbd0b269ad28750d1c04fbdfb9f5304a613c514fd0e840613cbc0f5e2a2c'
PARAMS=dict(Counter=0,Direction='ASC',LeagueID='00',PlayerOrTeam='T',Season='2025-26',SeasonType='Regular Season',Sorter='DATE',DateFrom='',DateTo='')
def now():return datetime.now(timezone.utc).isoformat(timespec='microseconds')
def sha(b):return hashlib.sha256(b).hexdigest()
def durable(p,d,exclusive=True):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x' if exclusive else 'w') as f:json.dump(d,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=os.open(p.parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def approve(request):
 if not sys.flags.isolated or not sys.flags.no_site:raise RuntimeError('Isolated no-site startup required')
 if sha((E/'authorization.txt').read_bytes())!=AUTH:raise RuntimeError('Recovery authorization required')
 ident=request.get('id','')
 if len(ident)!=32 or any(c not in '0123456789abcdef' for c in ident):raise RuntimeError('Invalid capability')
 path=E/'capabilities'/(ident+'.json');cap=json.loads(path.read_text())
 if request.get('nonce')!=cap['nonce'] or cap['authorization_sha256']!=AUTH or cap['mode'] not in ['local_tls','part_b']:raise RuntimeError('Capability mismatch')
 if cap['worker_sha256']!=sha(Path(__file__).read_bytes()):raise RuntimeError('Worker changed')
 if cap['mode']=='part_b':
  gate=E/'part_a_exit_gate.json';ledger=E/'recovery_opening_ledger.json'
  if not json.loads(gate.read_text())['passed'] or cap['gate_sha256']!=sha(gate.read_bytes()):raise RuntimeError('Part A gate required')
  d=json.loads(ledger.read_text())
  if d['status']!='armed' or d['first_physical_data_access_at_utc'] is not None or d['scientific_protocol_changed'] or d['final_outcome_previously_decoded']:raise RuntimeError('Part B ledger required')
  if cap['ledger_sha256']!=sha(ledger.read_bytes()):raise RuntimeError('Ledger changed')
  durable(E/'recovery_acquisition_consumed.json',dict(at_utc=now(),capability=ident),True)
 durable(path.with_suffix('.consumed.json'),dict(at_utc=now(),mode=cap['mode']),True)
 return cap,path

def main():
 request=json.loads(sys.stdin.read());cap,path=approve(request)
 # Add dependencies explicitly, then install the SAME unchanged development guard.
 sys.path[:0]=[str(ROOT/'src'),str(ROOT/'.venv/lib/python3.10/site-packages')]
 from nba_game_prediction import sealed_access as access
 import requests
 from nba_api.stats.library.http import NBAStatsHTTP
 from nba_api.stats.endpoints.leaguegamelog import LeagueGameLog
 from importlib.metadata import version
 blocked=socket.socket
 active=False;approved_ips=set();dns_calls=[];connects=[]
 original_dns=socket.getaddrinfo
 mode=cap['mode']
 def dns(host,port,*args,**kw):
  allowed=host in ('localhost','127.0.0.1','::1') if mode=='local_tls' else host=='stats.nba.com'
  if not active or not allowed:raise RuntimeError('DNS outside capability denied')
  results=original_dns(host,port,*args,**kw);approved_ips.update(x[4][0] for x in results);dns_calls.append([host,port]);return results
 def audit(event,args):
  if event=='socket.connect':
   addr=args[1]
   if not active or not isinstance(addr,tuple) or addr[0] not in approved_ips or (mode=='part_b' and addr[1]!=443):raise RuntimeError('Connect outside capability denied')
   connects.append(list(addr))
  if event=='socket.bind' and (mode!='local_tls' or not active or args[1][0]!='127.0.0.1'):raise RuntimeError('Bind outside capability denied')
 sys.addaudithook(audit)
 class Restricted(requests.Session):
  def __init__(self):super().__init__();self.trust_env=False
  def request(self,method,url,**kw):
   if mode=='part_b':ok=method.upper()=='GET' and url=='https://stats.nba.com/stats/leaguegamelog' and dict(kw.get('params',{}))==PARAMS
   else:ok=method.upper()=='GET' and url==local_url
   if not ok:raise RuntimeError('Unapproved endpoint or parameters')
   kw['allow_redirects']=False
   return super().request(method,url,**kw)
 result={'mode':mode,'ssl_mro':[c.__module__+'.'+c.__qualname__ for c in ssl.SSLSocket.__mro__],'ssl_base_is_original_socket':ssl.SSLSocket.__mro__[1] is ORIGINAL_SOCKET,'normal_socket_is_blocked':blocked.__name__=='BlockedSocket','nba_api_version':version('nba_api'),'authorization_sha256':AUTH}
 if not result['ssl_base_is_original_socket'] or any('BlockedSocket' in x for x in result['ssl_mro']):raise RuntimeError('Stale SSL inheritance')
 try:
  active=True;socket.socket=ORIGINAL_SOCKET;socket.getaddrinfo=dns
  if mode=='local_tls':
   from http.server import HTTPServer,BaseHTTPRequestHandler
   class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
     body=b'local synthetic TLS fixture';self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def log_message(self,*a):pass
   with tempfile.TemporaryDirectory() as temp:
    t=Path(temp);conf=t/'openssl.cnf';conf.write_text('[req]\ndistinguished_name=dn\nx509_extensions=ext\nprompt=no\n[dn]\nCN=localhost\n[ext]\nsubjectAltName=DNS:localhost,IP:127.0.0.1\nbasicConstraints=CA:TRUE\n')
    subprocess.run(['/usr/bin/openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1','-keyout',str(t/'key.pem'),'-out',str(t/'cert.pem'),'-config',str(conf)],check=True,capture_output=True)
    server=HTTPServer(('127.0.0.1',0),Handler);ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.load_cert_chain(t/'cert.pem',t/'key.pem');server.socket=ctx.wrap_socket(server.socket,server_side=True)
    local_url='https://localhost:'+str(server.server_port)+'/synthetic'
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
     with Restricted() as client:
      response=client.get(local_url,verify=str(t/'cert.pem'),timeout=5)
      assert response.status_code==200 and response.content==b'local synthetic TLS fixture'
      result.update(real_tls_handshake=True,https_fixture=True,certificate_verified=True,response_status=200)
      try:client.get('https://stats.nba.com/stats/leaguegamelog',params=PARAMS)
      except RuntimeError:result['part_a_final_endpoint_rejected']=True
      else:raise AssertionError('Part A admitted NBA')
    finally:server.shutdown();server.server_close();thread.join(timeout=5)
  else:
   client=LeagueGameLog(counter=0,direction='ASC',league_id='00',player_or_team_abbreviation='T',season='2025-26',season_type_all_star='Regular Season',sorter='DATE',date_from_nullable='',date_to_nullable='',get_request=False)
   assert client.parameters==PARAMS
   with Restricted() as transport:
    NBAStatsHTTP.set_session(transport)
    start=now();ledger_path=E/'recovery_opening_ledger.json';ledger=json.loads(ledger_path.read_text());ledger['first_physical_data_access_at_utc']=start;ledger['status']='access_started';durable(ledger_path,ledger,False)
    durable(E/'first_access.json',dict(timestamp_utc=start,event='immediately before recovery NBA LeagueGameLog call',parameters=PARAMS))
    response=NBAStatsHTTP().send_api_request(endpoint=client.endpoint,parameters=PARAMS,timeout=30)
    received=now();durable(E/'first_response.json',dict(timestamp_utc=received,status=response._status_code,url=response.get_url()))
    body=response.get_response().encode('utf-8');raw=ROOT/'data/raw/stage6r/leaguegamelog_response.json';raw.parent.mkdir(parents=True,exist_ok=True)
    with raw.open('xb') as f:f.write(body);f.flush();os.fsync(f.fileno())
    result.update(endpoint='LeagueGameLog',parameters=PARAMS,http_status=response._status_code,url=response.get_url(),retrieval_started_utc=start,retrieved_at_utc=received,sha256=sha(body),raw_bytes=len(body),raw_file=str(raw.relative_to(ROOT)),response_decoded=False)
    durable(E/'acquisition.json',result)
    if response._status_code!=200:raise RuntimeError('Non-200 NBA response; STOP')
 finally:
  active=False;socket.socket=blocked;socket.getaddrinfo=original_dns
  try:socket.socket()
  except RuntimeError:result['revocation_blocks_socket']=True
  else:raise AssertionError('Capability revocation failed')
  durable(path.with_suffix('.revoked.json'),dict(at_utc=now(),socket_block_restored=True))
 result.update(passed=True,dns_calls=dns_calls,connects=connects,final_data_access=(mode=='part_b'));print(json.dumps(result))
if __name__=='__main__':
 try:main()
 except Exception as e:
  print(json.dumps(dict(passed=False,error_type=type(e).__name__,error=str(e))));sys.exit(1)
