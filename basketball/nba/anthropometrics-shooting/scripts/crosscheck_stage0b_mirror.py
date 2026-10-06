"""Compare a checksum-pinned secondary-host copy; never label this official retrieval."""
import sys,json,re,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0b_io import *
from anthropometrics_shooting.normalize import name_key,inches,number

def main():
    cr=archive(json.loads((E0/'archive_sources.json').read_text())[0])
    meta=next(m for m in json.loads((E/'supplemental_retrievals.json').read_text()) if 'mirror' in m['source'])
    pages=json.loads((ROOT/'data/interim/combine_2013_mirror_pages.json').read_text())
    aliases={'Otto Porter Jr.':'Otto Porter','Glen Rice Jr.':'Glen Rice','Dennis Schroeder':'Dennis Schroder'}
    dim=r"\d+'\s*\d+(?:\.\d+)?''"
    pattern=re.compile(r'^(.*?), (.*?) ('+dim+r'|N/A) ('+dim+r'|N/A) (\d+(?:\.\d+)?|N/A) ('+dim+r'|N/A) ('+dim+r'|N/A) ')
    checks=[];unmatched=[]
    for page,text in enumerate(pages,1):
        for line in text.splitlines():
            m=pattern.match(line)
            if not m:continue
            name=m[2]+' '+m[1];key=name_key(aliases.get(name,name))
            matches=[r for r in cr if r['SEASON']=='2013' and name_key(r['PLAYER_NAME'])==key]
            if len(matches)!=1:unmatched.append(name);continue
            r=matches[0]
            for field,value in zip(['HEIGHT_WO_SHOES','HEIGHT_W_SHOES','WEIGHT','WINGSPAN','STANDING_REACH'],m.groups()[2:]):
                v=number(value) if field=='WEIGHT' else inches(value);a=number(r.get(field));d=a-v if a is not None and v is not None else None
                checks.append(dict(player_id=r['PLAYER_ID'],player_name=r['PLAYER_NAME'],source_player_name=name,combine_year=2013,field=field,archive_value=a,secondary_value=v,difference=d,match_status='unavailable' if d is None else 'exact' if d==0 else 'conflict',source_class='NBA-authored PDF on independent secondary host; lineage not authenticated',source_url=meta['url']+'#page='+str(page),retrieval_timestamp=meta['retrieval_timestamp'],raw_sha256=meta['raw_sha256'],name_mapping='explicit audit-only spelling/suffix mapping' if name in aliases else 'same-year exact normalized name; not an ID bridge'))
    csvwrite(E/'anthro_secondary_crosscheck.csv',checks)
    summary=dict(players=len(checks)//5,unmatched=unmatched,statuses=dict(collections.Counter(r['match_status'] for r in checks)),core_conflicts=[r for r in checks if r['match_status']=='conflict' and r['field'] in ['HEIGHT_WO_SHOES','WINGSPAN']],interpretation='Secondary corroboration only. Does not count as successful retrieval from official NBA host.')
    dump(E/'anthro_secondary_summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
