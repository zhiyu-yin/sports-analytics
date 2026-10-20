"""Reuse hash-matched clock evidence; unchanged clock algorithm for new books."""
import csv
from phase2b.clocks import book_clocks as original
from phase2c.pipeline import manifest as prior_manifest
from injury_warning.pilot_io import ROOT
OLD=None;SM=None
def book_clocks(item):
    global OLD,SM
    if OLD is None:
        with (ROOT/'phase2c/tables/all_acquired_game_clock_audit.csv').open() as f:OLD={r['game_id']:r for r in csv.DictReader(f)}
        SM=prior_manifest()
    gid,entry=item;r=OLD.get(gid)
    if r and SM.get('book_'+gid,{}).get('sha256')==entry.get('sha256') and r.get('book_start_raw') and r.get('book_end_raw'):
        return gid,{k:v for k,v in r.items() if k.startswith('book_') and k not in {'book_start_converted_utc','book_end_converted_utc','book_conversion_rule'}}
    return original(item)
