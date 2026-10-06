import sys,csv,json,concurrent.futures,re,html
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0b_io import *
def main():
    rows=list(csv.DictReader((E/'anthro_sample_predeclared.csv').open()))
    for name,y in [('Daniel Gafford',2019),('Eric Paschall',2019),('Naz Reid',2019),('P.J. Washington',2019),('Andrew Nembhard',2022),('Nikola Jovic',2022)]: rows.append(dict(PLAYER_NAME=name,SEASON=str(y)))
    def f(r):
        name=r['PLAYER_NAME']; year=int(r['SEASON']); slug=name.lower().replace('.','').replace(' ','-')
        url=f'https://www.nba.com/draft/{year}/prospects/{slug}'
        b,m=fetch(url,'Official prospect: '+name,18)
        text=re.sub('<script.*?</script>|<style.*?</style>',' ',b.decode(errors='replace'),flags=re.S)
        text=html.unescape(re.sub('<[^>]+>',' ',text)); text=re.sub(r'\s+',' ',text)
        fragments=re.findall(r'.{0,140}(?:wingspan|without shoes|standing reach|without sneakers).{0,150}',text,flags=re.I)
        m.update(player=name,combine_year=year,measurement_fragments=fragments)
        print(name,m['http_status'],fragments[:2],flush=True); return m
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: out=list(pool.map(f,rows))
    dump(E/'official_profile_retrievals.json',out)
if __name__=='__main__': main()
