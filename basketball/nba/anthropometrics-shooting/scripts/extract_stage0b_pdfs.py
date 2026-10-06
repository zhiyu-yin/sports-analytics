"""Offline text extraction from SHA-verified PDFs; page images inspected separately."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from anthropometrics_shooting.stage0b_io import ROOT,E,sha,dump
from pypdf import PdfReader

def main():
    sources=json.loads((E/'official_retrievals.json').read_text())+json.loads((E/'supplemental_retrievals.json').read_text())
    for label,out in [('warriors_2016_17_guide','warriors_2016_17_pages.json'),('NBA-authored 2013 combine PDF, independent secondary mirror','combine_2013_mirror_pages.json')]:
        m=next(m for m in sources if m['source']==label);p=ROOT/m['raw_path']
        assert sha(p)==m['raw_sha256']
        dump(ROOT/'data/interim'/out,[page.extract_text() for page in PdfReader(p).pages])
if __name__=='__main__':main()
