#!/usr/bin/env python3
import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from phase1c.sources import acquire
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fetch',action='store_true');a=p.parse_args();print(acquire(a.fetch))
