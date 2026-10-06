import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0c import *
def main():
    E.mkdir(parents=True,exist_ok=True)
    protected=E/'prior_preservation_manifest.json'
    if not protected.exists():
        paths=[p for p in ROOT.rglob('*') if p.is_file() and 'stage0c' not in str(p.relative_to(ROOT)) and '__pycache__' not in str(p)]
        dump(protected,{str(p.relative_to(ROOT)):sha(p) for p in paths})
    rows,_=read_combine();selected,reserve=sample(rows)
    p=E/'validation_sample_predeclared.csv'
    if p.exists():raise ValueError('Sample already declared; do not overwrite')
    csvwrite(p,selected);csvwrite(ROOT/'data/interim/stage0c_replacement_pool_predeclared.csv',reserve)
    dump(E/'release_rule_predeclared.json',dict(declared_at=now(),primary_sample=45,sampling='Three eras x three absolute height groups; within each cell select advantage rank .10,.35,.50,.65,.90; lower<.20, middle .20-.80, upper>.80. No outcomes.',replacement_rule='At most one replacement per unavailable original, same era/height/relative stratum, lowest SHA256(ID:year) among unused reserve; preserve original. Only activate if a same-stratum official source route is found. Log every replacement.',pair_identity='same player AND exact combine year; explicit barefoot field only',rounding='difference <=0.125 inches only when source precision <=0.25 inches; coarse source values separately flagged, not counted toward release',pass_rule='At least 30 direct official fine-precision same-year pairs; >=95% exact/rounding-consistent; all three eras and all three height and relative strata represented; no unresolved substantive or systematic discrepancy; reference clean; tests pass; no outcome analysis.',systematic_rule='Flag an unresolved field offset when >=3 nonzero discrepancies share sign within an era or height stratum and their median absolute size exceeds 0.125 inch; also flag any explicit repeated unit/shoe-vs-barefoot mismatch. No significance test.',fail_rule='FAIL — MATERIAL SOURCE CONFLICT when authoritative evidence shows an unresolved systematic discrepancy or a substantive conflict that cannot be safely quarantined without changing the frozen population; otherwise insufficient evidence yields PARTIAL — INSUFFICIENT DIRECT VALIDATION.',minimum_eras=3,minimum_pairs=30,minimum_agreement=.95,no_outcome_access=True,no_residual_fit=True))
    print('Declared',len(selected),'players');print([(r['player_name'],r['combine_year']) for r in selected])
if __name__=='__main__':main()
