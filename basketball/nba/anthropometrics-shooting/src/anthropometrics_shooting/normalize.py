import math, re, unicodedata

def number(value):
    if value is None or str(value).strip().lower() in {'','nan','none','null','na','n/a','-'}: return None
    n=float(value)
    return n if math.isfinite(n) else None

def inches(value, unit='in'):
    if unit=='cm':
        n=number(value); return None if n is None else n/2.54
    if unit!='in': raise ValueError('Unsupported unit')
    if isinstance(value,str) and ("'" in value or '"' in value):
        match=re.fullmatch(r'''\s*(\d+)\s*'\s*(\d+(?:\.\d+)?)\s*(?:"|'')?\s*''',value)
        if not match or float(match[2])>=12: raise ValueError('Malformed feet/inches')
        return int(match[1])*12+float(match[2])
    return number(value)

def player_id(value):
    n=number(value)
    if n is None: return None
    if n<=0 or n!=int(n): raise ValueError('Invalid player ID')
    return str(int(n))

def name_key(value):
    # Preserve suffixes; accent/punctuation folding can create collisions.
    s=unicodedata.normalize('NFKD',str(value or '')).casefold()
    return ''.join(c for c in s if c.isalnum() and not unicodedata.combining(c))

def season(value):
    s=str(value)
    if not re.fullmatch(r'\d{4}-\d{2}',s) or int(s[-2:])!=(int(s[:4])+1)%100:
        raise ValueError('Invalid season label')
    return s
