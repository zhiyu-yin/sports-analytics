"""Factual comparisons only. Never combines body measurements with shooting accuracy."""
import sys,json,csv,re,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0b_io import *
from anthropometrics_shooting.normalize import inches,name_key,number
from anthropometrics_shooting.official_text import article_text

def main():
    cr=archive(json.loads((E0/'archive_sources.json').read_text())[0])
    sampled=list(csv.DictReader((E/'anthro_sample_predeclared.csv').open()))
    profiles=json.loads((E/'official_profile_retrievals.json').read_text())
    fields=['HEIGHT_WO_SHOES','HEIGHT_W_SHOES','WINGSPAN','STANDING_REACH','WEIGHT']
    anthropo=[]
    def append(r,field,official,meta,group,precision=None,notes=''):
        v=number(r.get(field));diff=v-official if v is not None and official is not None else None
        status='official-source-unavailable' if diff is None else 'exact' if abs(diff)<1e-8 else 'rounding-consistent' if precision and abs(diff)<=precision/2+1e-8 else 'conflict'
        anthropo.append(dict(player_id=r['PLAYER_ID'],player_name=r['PLAYER_NAME'],combine_year=r['SEASON'],field=field,archive_value=v,official_value=official,difference=diff,source_url=meta['url'],retrieval_timestamp=meta['retrieval_timestamp'],raw_sha256=meta['raw_sha256'],match_status=status,sample_group=group,notes=notes))
    # Contemporary narrative values are not same-year combine measurements unless explicitly stated.
    narrative={'Ayo Dosunmu':{'WINGSPAN':80,'WEIGHT':200},'Scottie Barnes':{'WINGSPAN':86,'WEIGHT':225},'Andrew Nembhard':{'HEIGHT_W_SHOES':76.5,'WINGSPAN':77.75,'WEIGHT':196},'Nikola Jovic':{'HEIGHT_W_SHOES':83,'WINGSPAN':84.25,'WEIGHT':223}}
    for r in sampled:
        m=next(x for x in profiles if x['player']==r['PLAYER_NAME'] and x['combine_year']==int(r['SEASON']))
        for field in fields:
            val=narrative.get(r['PLAYER_NAME'],{}).get(field)
            append(r,field,val,m,'predeclared_stratified',1 if val is not None else None,'Rounded narrative; not explicitly same-year combine' if val is not None else 'Requested page did not expose this factual measurement')
    for name in ['Andrew Nembhard','Nikola Jovic']:
        r=next(x for x in cr if x['PLAYER_NAME']==name and x['SEASON']=='2022');m=next(x for x in profiles if x['player']==name)
        for field in fields:append(r,field,narrative[name].get(field),m,'supplemental_2022',1 if field=='WEIGHT' else None,'Explicit 2022 combine narrative; no barefoot/reach value')
    # Include all rows explicitly labeled Combine measurements in the three discovered 2012 articles.
    metas=[json.loads((E/'rockets_sf_source.json').read_text())]+[m for m in json.loads((E/'supplemental_retrievals.json').read_text()) if m['source'].startswith('Rockets')]
    for m in metas:
        lines=article_text((ROOT/m['raw_path']).read_bytes()).splitlines()
        for i,line in enumerate(lines):
            if not line.startswith('Combine measurements:'):continue
            name=lines[i-1].split(',')[0].strip(); candidates=[r for r in cr if r['SEASON']=='2012' and name_key(r['PLAYER_NAME'])==name_key(name)]
            if len(candidates)!=1: print('Unmapped official article name',name); continue
            r=candidates[0]
            pattern=r"(\d+\s*'\s*\d+(?:\.\d+)?\s*'')"
            ht=re.search(r'Height:\s*'+pattern,line,re.I); ws=re.search(r'Wingspan:?\s*'+pattern,line,re.I);reach=re.search(r'Standing [Rr]each:\s*'+pattern,line);weight=re.search(r'Weight:\s*(\d+(?:\.\d+)?)',line)
            vals={'HEIGHT_W_SHOES':inches(ht[1]) if ht else None,'WINGSPAN':inches(ws[1]) if ws else None,'STANDING_REACH':inches(reach[1]) if reach else None,'WEIGHT':float(weight[1]) if weight else None}
            for field in fields:append(r,field,vals.get(field),m,'supplemental_official_2012',None,'Article specifies shoe height; barefoot not provided. All labeled rows included, no selection by outcome.')
    csvwrite(E/'anthro_official_crosscheck.csv',anthropo)
    # All four remain unresolved: available generic pages do not distinguish quarter-inch values.
    discrepancies=[]
    for pid,field in [('1629655','WINGSPAN'),('1629672','WINGSPAN'),('1629023','WINGSPAN'),('1629675','HEIGHT_WO_SHOES')]:
        r=next(r for r in cr if r['PLAYER_ID']==pid and r['SEASON']=='2019')
        m=next(x for x in profiles if name_key(x['player'])==name_key(r['PLAYER_NAME']))
        discrepancies.append(dict(player_id=pid,player_name=r['PLAYER_NAME'],combine_year=2019,field=field,archive_numeric=float(r[field]),archive_display=r[field+'_FT_IN'],archive_display_inches=inches(r[field+'_FT_IN']),resolution_status='unresolved',supported_value='',source_url=m['url'],retrieval_timestamp=m['retrieval_timestamp'],action='quarantine 2019 measurement; no impact on <=2013 analysis/reference',notes='No accessible official same-year precise measurement. Numeric and display preserved. 2018 Washington row agrees internally at 86.5; does not resolve 2019. ' if pid=='1629023' else 'No accessible official same-year precise measurement; no correction guessed.'))
    csvwrite(E/'measurement_discrepancy_review.csv',discrepancies)
    # Official guide page numbers are PDF 1-based; values parsed from visually inspected rows.
    page_map={'Ian Clark':39,'Stephen Curry':51,'Kevin Durant':57,'Draymond Green':63,'Andre Iguodala':69,'Shaun Livingston':75,'Klay Thompson':91,'Anderson Varejao':95,'David West':101,'JaVale McGee':106,'Andrew Bogut':292,'Nemanja Nedovic':329}
    pages=json.loads((ROOT/'data/interim/warriors_2016_17_pages.json').read_text())
    m=next(m for m in json.loads((E/'official_retrievals.json').read_text()) if m['source']=='warriors_2016_17_guide')
    shooting=[]
    for r in csv.DictReader((E/'shooting_sample_predeclared.csv').open()):
        page=page_map[r['player_name']];text=pages[page-1]
        if r['player_name']=='Andrew Bogut':line=next(l for l in text.splitlines() if l.startswith('Bogut '));nums=line.split()[1:]
        elif r['player_name']=='Nemanja Nedovic':
            text=text[text.index('NEMANJA NEDOVIC'):];line=next(l for l in text.splitlines() if l.startswith('13-14 ')); nums=line.split()[1:]
        else:
            line=next(l for l in text.splitlines() if re.match(r'^13-14 ',l));nums=re.findall(r'(?<!\S)(?:\d+(?:\.\d+)?|\.\d+|---)(?!\S)',line.split(' ',1)[1])
        vals={'GP':int(nums[0]),'MIN':int(nums[1]),'FG3M':int(nums[5]),'FG3A':int(nums[6]),'FTM':int(nums[8]),'FTA':int(nums[9])}
        for field in ['FTM','FTA','FG3M','FG3A','GP','MIN']:
            actual=int(r[field]) if field!='MIN' else int(r['seconds'])/60;v=vals[field];diff=actual-v
            shooting.append(dict(player_id=r['player_id'],player_name=r['player_name'],season='2013-14',volume_band=r['volume_band'],field=field,archive_value=actual,official_value=v,difference=round(diff,8),match_status='exact' if diff==0 else 'rounding-consistent' if field=='MIN' and abs(diff)<=.5 else 'conflict',source_url=m['url']+'#page='+str(page),retrieval_timestamp=m['retrieval_timestamp'],raw_sha256=m['raw_sha256'],notes='Regular-season record; full page visually inspected; MIN printed as whole minutes.'))
    csvwrite(E/'shooting_official_crosscheck.csv',shooting)
    print('Players with at least one agreeing official field (not full validation):',len({(r['player_id'],r['combine_year']) for r in anthropo if r['match_status'] in ['exact','rounding-consistent']}))
    print('Anthro field statuses:',collections.Counter(r['match_status'] for r in anthropo));print('Anthro conflicts:',[(r['player_name'],r['field'],r['archive_value'],r['official_value']) for r in anthropo if r['match_status']=='conflict'])
    print('Shooting',collections.Counter(r['match_status'] for r in shooting));print('Shooting conflicts:',[r for r in shooting if r['match_status']=='conflict'])
if __name__=='__main__':main()
