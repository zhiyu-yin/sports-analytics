"""Extract public NBA Next.js article text, including content not server-rendered."""
import json,re,html

def article_text(body):
    s=body.decode(errors='replace') if isinstance(body,bytes) else body
    snippets=[]
    def walk(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if k=='text' and isinstance(v,str):snippets.append(v)
                elif k=='content' and isinstance(v,str):snippets.append(v)
                else:walk(v)
        elif isinstance(o,list):
            for v in o:walk(v)
    match=re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',s,re.S)
    if match:
        walk(json.loads(match[1]))
    plain=re.sub('<script.*?</script>|<style.*?</style>',' ',s,flags=re.S)
    snippets.append(plain)
    return '\n'.join(dict.fromkeys(html.unescape(re.sub('<[^>]+>',' ',t)).strip() for t in snippets))
