from collections import Counter
from .normalize import number

def anthropometrics(row):
    issues=[]
    for field,lo,hi in [('height_inches',60,96),('wingspan_inches',60,108)]:
        n=row.get(field)
        if n is None: issues.append(field+':missing')
        elif n<=0: issues.append(field+':nonpositive')
        elif not lo<=n<=hi: issues.append(field+':review_range')
    # A wingspan below height is not intrinsically invalid; never clip.
    return issues

def shooting(row):
    issues=[]
    for made,attempt,pct in [('FTM','FTA','FT_PCT'),('FG3M','FG3A','FG3_PCT'),('FGM','FGA','FG_PCT')]:
        m,a,p=map(number,(row.get(made),row.get(attempt),row.get(pct)))
        if m is None or a is None: issues.append(made+':missing_counts'); continue
        if m<0 or a<0 or m>a: issues.append(made+':invalid_counts')
        if m!=int(m) or a!=int(a): issues.append(made+':noninteger_totals')
        if a>0 and p is not None and abs(p-m/a)>0.00051: issues.append(pct+':disagreement')
    return issues

def duplicate_keys(rows,keys):
    return {str(k):n for k,n in Counter(tuple(r.get(f) for f in keys) for r in rows).items() if n>1}
