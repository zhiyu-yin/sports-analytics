"""Declare samples using separate domains: no exposure/outcome association."""
import sys,json,csv,collections,datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0b_io import *
from anthropometrics_shooting.normalize import number

def declared_csv(path,rows):
    if path.exists():
        previous=list(csv.DictReader(path.open()))
        expected=[{k:str(v) for k,v in r.items()} for r in rows]
        if previous!=expected:raise ValueError('Predeclared sample changed; versioned amendment required')
    else:csvwrite(path,rows)

def main():
    baseline=E/'stage0_preservation_manifest.json'
    if not baseline.exists():
        paths=[ROOT/'docs/stage0_data_audit.md']+list(E0.glob('*'))+[p for p in (ROOT/'data/raw').iterdir() if p.is_file()]
        dump(baseline,{str(p.relative_to(ROOT)):sha(p) for p in paths})
    cm=json.loads((E0/'archive_sources.json').read_text())[0]; rows=archive(cm)
    fields=['PLAYER_ID','PLAYER_NAME','SEASON','HEIGHT_WO_SHOES','HEIGHT_W_SHOES','WINGSPAN','STANDING_REACH','WEIGHT']
    sample=[]
    # Nine quantile ranks within each time band; only complete body measurements.
    for label,lo,hi in [('early',2000,2007),('middle',2008,2014),('recent',2015,2022)]:
        pool=[r for r in rows if lo<=int(r['SEASON'])<=hi and number(r['HEIGHT_WO_SHOES']) and number(r['WINGSPAN'])]
        pool.sort(key=lambda r:(float(r['WINGSPAN'])-float(r['HEIGHT_WO_SHOES']),r['SEASON'],r['PLAYER_NAME']))
        for idx,quantile in enumerate([.02,.10,.20,.35,.50,.65,.80,.90,.98]):
            r=pool[round(quantile*(len(pool)-1))]
            sample.append({**{k:r[k] for k in fields},'era':label,'selection_rule':f'advantage quantile rank {quantile}','stratum':['short','middle','long'][idx//3]})
    declared_csv(E/'anthro_sample_predeclared.csv',sample)
    names=['Kevin Durant','Stephen Curry','Klay Thompson','Andre Iguodala','David West','Shaun Livingston','Anderson Varejao','Andrew Bogut','Draymond Green','JaVale McGee','Nemanja Nedovic','Ian Clark']
    totals={}; allnames={}
    for m in json.loads((E0/'shooting_archive_sources.json').read_text()):
        for r in archive(m):
            pid=r['personId']; allnames[pid]=r['personName']
            if r['season_year']!='2013-14': continue
            t=totals.setdefault(pid,dict(player_id=pid,player_name=r['personName'],FTM=0,FTA=0,FG3M=0,FG3A=0,GP=0,seconds=0,position_rows=0))
            parts=r['minutes'].split(':') if r['minutes'] else []
            sec=int(parts[0])*60+int(parts[1]) if len(parts)==2 else 0
            if sec<=0: continue
            t['GP']+=1; t['seconds']+=sec; t['position_rows']+=bool(r['position'])
            for a,b in [('FTM','freeThrowsMade'),('FTA','freeThrowsAttempted'),('FG3M','threePointersMade'),('FG3A','threePointersAttempted')]: t[a]+=int(r[b])
    csvwrite(ROOT/'data/interim/stage0b_nba_2013_14_totals.csv',list(totals.values()))
    csvwrite(ROOT/'data/interim/stage0b_nba_identities.csv',[dict(player_id=k,player_name=v) for k,v in allnames.items()])
    chosen=[dict(r,volume_band='high' if r['FTA']>=300 else 'medium' if r['FTA']>=50 else 'low_nonzero' if r['FTA'] else 'zero') for r in totals.values() if r['player_name'] in names]
    declared_csv(E/'shooting_sample_predeclared.csv',chosen)
    if not (E/'sample_protocol.json').exists():dump(E/'sample_protocol.json',dict(declared_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),anthro_rule='27 quantile-rank players: 9 in each of 2000-07, 2008-14, 2015-22; sorted by wingspan minus barefoot height. No shooting data used. Additional recognizable official-source examples may be reported separately, never replacing unavailable selected records.',shooting_rule='12 named players spanning guards/wings/bigs and FT volume; selected for expected official media-guide availability, not combine measurements or accuracy. Compare all six fields including unavailable values.',shooting_names=names,forbidden='No exposure-outcome estimates or comparisons.'))
    print('Anthro sample:',[(r['PLAYER_NAME'],r['SEASON'],r['stratum']) for r in sample]);print('Shooting:',[(r['player_name'],r['FTA']) for r in chosen])
    print('Discrepancies:',[{k:r[k] for k in ['PLAYER_ID','PLAYER_NAME','SEASON','HEIGHT_WO_SHOES','HEIGHT_WO_SHOES_FT_IN','WINGSPAN','WINGSPAN_FT_IN']} for r in rows if r['PLAYER_ID'] in ['1629655','1629672','1629023','1629675']])
if __name__=='__main__': main()
