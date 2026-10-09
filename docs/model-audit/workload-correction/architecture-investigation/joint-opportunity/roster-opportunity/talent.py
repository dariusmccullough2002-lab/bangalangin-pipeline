"""Rate-engine boundary. Reuse Pipeline's independent existing talent estimate.
This adapter does not recollect Statcast, change prospect translations, or
apply availability to rates. Age adjustments already in the preserved rate
estimate are retained once. New ability research can replace this contract
without retraining organizational opportunity.
"""
from dataclasses import dataclass
from engine import stats
@dataclass(frozen=True)
class TalentRateForecast:
 role: str
 preserved_stats: dict
 asof_features: dict
 @property
 def rates_per_opportunity(self):
  key='PA' if self.role=='H' else 'IP';denom=self.preserved_stats.get(key,0)
  return {k:v/denom for k,v in self.preserved_stats.items()} if denom else None
 def project(self,opportunity):
  # The preserved QA3 conditional yields (exact league definition), state
  # appearance bounds, and SV/HLD caps accompany the opportunity components.
  # Scaling cancels the old workload total and preserves its per-unit talent
  # rates. Neither age nor availability is applied again here.
  return stats(self.preserved_stats,opportunity,self.role,self.asof_features)
 @property
 def evidence(self):
  return {'rate_source':'preserved independent Pipeline talent/aging estimate','rate_unit':'PA' if self.role=='H' else 'IP','new_statcast_collection':False,'availability_discount_on_rates':False,'missing_statcast_does_not_become_zero_skill':True}
