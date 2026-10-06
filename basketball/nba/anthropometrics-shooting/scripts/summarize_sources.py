"""Summarize documentation and observed probe status without inferring availability."""
import sys,json,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.provenance import EVIDENCE

def main():
    docs=json.loads((EVIDENCE/'endpoint_documentation.json').read_text())
    probes=json.loads((EVIDENCE/'endpoint_probes.json').read_text())
    corrected=EVIDENCE/'combine_corrected_probes.json'
    if corrected.exists(): probes+=json.loads(corrected.read_text())
    anthropo=[]; shooting=[]
    for ep,d in docs.items():
        pp=[p for p in probes if p['source']==ep]
        # Incorrect exploratory YYYY-YY combine parameters remain in original logs only.
        valid=[p for p in pp if not ep.startswith('draftcombine') or len(p['parameters'].get('SeasonYear',''))==4]
        years=sorted({p['parameters'].get('Season',p['parameters'].get('SeasonYear')) for p in valid})
        schema=[]
        for line in d['documented_schemas']:
            try: schema.append(ast.literal_eval(line))
            except (ValueError,SyntaxError): pass
        out=dict(endpoint=ep,url='https://stats.nba.com/stats/'+ep,documentation_url=d['provenance']['url'],evidence_type='documented schema; live request outcomes separate',documented_schemas=schema,earliest_tested=years[0] if years else None,latest_tested=years[-1] if years else None,tested_seasons=years,valid_probes=len(valid),successful_responses=sum(p['status']=='ok' for p in valid),observed_rows=None,empty_historical_response_observed=False,empty_response_assessment='No successful response; cannot distinguish unavailable history from network failure',identifier='PLAYER_ID; anthro also has TEMP_PLAYER_ID (not a join key)',programmatic=True,reliability='No successful live sample from this host on 2026-09-28',notes=[])
        if ep=='leaguedashptstats':
            out['notes']=['Published sample schema is Team/SpeedDistance; it is NOT evidence of CatchShoot or PullUpShot fields.','Requested Player + Totals + CatchShoot and PullUpShot separately. Actual shot count schemas remain unverified.']
        if ep=='shotchartdetail': out['notes']=['Test player 201939, TeamID=0, ContextMeasure=FGA; event coordinates and distance documented; free throws are not the shot-chart primary outcome.']
        (anthropo if ep.startswith('draftcombine') else shooting).append(out)
    cm=json.loads((EVIDENCE/'archive_sources.json').read_text())[0]
    anthropo.append(dict(source='ianstack NBA-Draft-Combine-Analysis',evidence_type='observed secondary archive',provenance=cm,coverage='2000–2022 inclusive',schema_evidence='combine_schema.json',coverage_evidence='coverage_by_year.csv',validation='Numeric/schema/join checks passed with flagged exceptions; full official reconciliation pending',redistribution='Raw CSV ignored locally; summary evidence only'))
    anthropo.append(dict(source='NBA AWS Combine Data Hub',url='https://combine.nba.com/',evidence_type='official web interface inspected; no tabular export validated',coverage=None,player_count=None,identifier_quality=None))
    shooting.append(dict(source='NocturneBear NBA-Data-2010-2024',evidence_type='observed secondary archive',provenance=json.loads((EVIDENCE/'shooting_archive_sources.json').read_text()),coverage='2010-11 through 2023-24',grain='player-game; aggregated for audit only',schema_evidence='shooting_schema.json',reliability='Pinned static CSVs downloadable; official completeness and lineage not independently established'))
    for name,obj in [('anthropometric_sources.json',anthropo),('shooting_sources.json',shooting)]: (EVIDENCE/name).write_text(json.dumps(obj,indent=2)+'\n')
if __name__=='__main__': main()
