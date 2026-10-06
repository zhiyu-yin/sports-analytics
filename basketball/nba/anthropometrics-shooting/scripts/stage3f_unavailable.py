"""Explicit unavailable outputs when a candidate fails the sampler gate."""
import argparse,pandas as pd
from stage3f_common import *
def main(candidate,attempt):
 key=candidate.lower();d=read(E/f'{key}_attempt{attempt}_diagnostics.json');assert not d['numeric_gate_pass'];d.update(sampler_pass=False,visual_review='NOT_RELEASED_FAILED_NUMERIC_GATE',recovery_exhausted=attempt==2);save(key+'_diagnostics.json',d)
 note=dict(candidate=candidate,status='NOT_RUN_FAILED_SAMPLER_GATE',reason='No PPC release or mechanism inference from failed convergence',replicates=0,gate_pass=False)
 for suffix in ['_conditional_accuracy_ppc.json','_joint_opportunity_ppc.json']:save(key+suffix,note)
 save(key+'_random_effect_correlations.json',dict(status='WITHHELD_FAILED_SAMPLER_GATE'))
 pd.DataFrame(columns=['parameter','mean','median','SD','CI95_low','CI95_high']).to_csv(E/(key+'_opportunity_parameters.csv'),index=False)
 if candidate=='F2':save('f2_between_within_parameters.json',dict(status='WITHHELD_FAILED_SAMPLER_GATE'))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('candidate',choices=['F1','F2']);p.add_argument('--attempt',type=int,required=True);a=p.parse_args();main(a.candidate,a.attempt)
