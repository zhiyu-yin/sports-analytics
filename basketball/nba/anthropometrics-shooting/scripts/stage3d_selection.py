"""Pure adequacy gates. This module has no trace, filesystem or parameter access."""
from dataclasses import dataclass
from math import ceil,isfinite

@dataclass(frozen=True,slots=True)
class CandidateGate:
 prior_pass: bool
 sampler_pass: bool
 conditional_accuracy_pass: bool
 joint_opportunity_pass: bool
 no_posthoc_change: bool
 firewall_intact: bool
 def __post_init__(self):
  if any(type(getattr(self,k)) is not bool for k in self.__slots__):raise TypeError('Gate input must be Boolean only')

def accuracy_gate(*,pooled_rate_99_pass,global_metrics_99_fail_count,season_rate_99_fail_count,season_count,FTA_bin_99_fail_count,systematic_volume_pattern):
 if season_count<=0:raise ValueError('Missing seasons')
 return bool(pooled_rate_99_pass and global_metrics_99_fail_count<3 and season_rate_99_fail_count<ceil(season_count/3) and FTA_bin_99_fail_count<2 and not systematic_volume_pattern)

def opportunity_gate(*,zero_frequency_99_pass,quantile_99_fail_count,season_totals_outside_99_low,season_totals_outside_99_high,season_count):
 if season_count<=0:raise ValueError('Missing seasons')
 return bool(zero_frequency_99_pass and quantile_99_fail_count<3 and max(season_totals_outside_99_low,season_totals_outside_99_high)<ceil(season_count/3))

def systematic_volume_pattern(observed,replicated_mean,mcse):
 if not (len(observed)==len(replicated_mean)==len(mcse)==5):raise ValueError('Exactly five frozen bins required')
 direction=[]
 for obs,rep,se in zip(observed,replicated_mean,mcse):
  if not all(isfinite(x) for x in [obs,rep,se]) or se<0:raise ValueError('Finite metric/MCSE required')
  bias=rep-obs;direction.append(1 if bias>2.576*se else -1 if bias< -2.576*se else 0)
 return bool(direction[0]!=0 and direction[0]==direction[1] and direction[3]==direction[4]==-direction[0])

def select_future_model(candidates):
 if set(candidates)!={'D0','D1','D2','D3'}:raise ValueError('Frozen candidate ladder required')
 if any(type(x) is not CandidateGate for x in candidates.values()):raise TypeError('Only typed adequacy gates accepted')
 final=candidates['D3']
 passed=all(getattr(final,k) for k in CandidateGate.__slots__)
 return dict(selected_future_model='D3' if passed else 'NONE',stage3e_authorized=passed,scientific_parameter_status='SEALED_PENDING_STAGE3E' if passed else 'NOT_AUTHORIZED',classification='ADEQUACY RESOLVED — D3 PASSES' if passed else 'ADEQUACY UNRESOLVED — D3 FAILS')
