from hybrid import *
from run_helpers import saveout
valid={'mlbam_id':694973,'evidence_kind':'roster','published_date':'2026-10-09','source_url':'https://www.mlb.com/pirates/roster/depth-chart','target_year':2027,'fact_or_assumption':'verified_fact','status':'listed in observed rotation; not a guaranteed2027 role'}
EvidenceContract.validate([valid],'2026-10-09',2027)
rejected=0
for bad in [valid|{'published_date':'2026-10-10'},valid|{'target_year':2028},valid|{'source_url':''}]:
 try:EvidenceContract.validate([bad],'2026-10-09',2027)
 except AssertionError:rejected+=1
assert rejected==3
rows=EvidenceContract.allocate_team([{'id':1,'healthy_slots':30,'max_slots':34},{'id':2,'healthy_slots':20,'max_slots':34},{'id':3,'healthy_slots':10,'max_slots':34}],162)
assert abs(sum(a['allocated_slots'] for a in rows)+rows[0]['team_unallocated_slots']-162)<1e-10
# These are allocation weights, not physical player forecasts; normalizer
# consumers still enforce player appearance caps and mark uncovered reserves.
assert max(a['allocated_slots'] for a in rows)<=34 and rows[0]['team_unallocated_slots']==60
saveout('Evidence_Contract_Verification.json',{'future_date_wrong_year_missing_source_rejected':rejected,'team_budget_sum':sum(a['allocated_slots'] for a in rows),'source':'synthetic contract fixture, not actual player allocation','passed':True})
print('Evidence contract passed')
