"""Deterministic DD rank curve correction; archived source snapshots, no network."""
from pathlib import Path
import json,re,gzip,base64,copy,csv,math,collections,subprocess
import numpy as np
from scipy.interpolate import PchipInterpolator
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
unpack=lambda h:json.loads(gzip.decompress(base64.b64decode(re.search("const packed='([^']+)'",h)[1])))
basehtml=gzip.decompress((ROOT/'docs/curve-correction-20261013/baselines/26a1d75.html.gz').read_bytes()).decode();base=unpack(basehtml)
rhtml=(ROOT/'docs/research-layer-20261013/Calculator.html').read_text();research=unpack(rhtml)
points=read(ROOT/'docs/value-audit-20261012/Curves.json')['overall_curve'];x=np.array([p['rank'] for p in points]);y=np.array([p['value'] for p in points]);last=float(x[-1]);old=lambda r:float(np.interp(r,x,y))
# Preserve ranks 1-32 exactly. Above rank32, knots follow fixed geometric spacing,
# independent of player identity and tier labels. Log-log PCHIP preserves monotonicity.
def make_curve(octaves):
 knots=[32.];k=32.*2**octaves
 while k<last:knots.append(k);k*=2**octaves
 knots.append(last);prices=[old(k) for k in knots];f=PchipInterpolator(np.log(knots),np.log(prices))
 def value(rank):
  rank=min(last,max(1.,float(rank)))
  return old(rank) if rank<=32 else float(np.exp(f(np.log(rank))))
 return value,knots
bymap={a['id']:a for a in base['assets']};rmap={a['id']:a for a in research['assets']}
records=[];variants={};curves={}
for octaves in [.5,1.,1.5]:
 value,knots=make_curve(octaves);rows=[]
 for a in base['assets']:
  p=a.get('ranking_policy')
  if not p:continue
  b=rmap[a['id']];rl=b.get('research_layer');rank=p.get('effective_overall_rank')
  if rl:
   anchor=rl['DD_rank'];mult=b['values']['neutral']['display']/old(anchor);v=value(anchor)*mult;rank=rl['effective_rank']
  elif rank is not None:anchor=rank;mult=a['values']['neutral']['display']/old(rank);v=value(rank)*mult
  else:continue
  before=a['values']['neutral']['display'];rv=b['values']['neutral']['display'];rows.append(dict(id=a['id'],name=a['name'],role=a['audit']['role'],source_scope=p['source_scope'],source_rank=p['source_rank'],effective_rank=rank,before=before,research_only=rv,new_baseline=value(anchor),research_multiplier=mult,after=v,curve_effect=v-rv,delta=v-before))
 variants[str(octaves)]=rows;curves[str(octaves)]=dict(knots=[dict(rank=k,value=old(k)) for k in knots],largest_changes=sorted(rows,key=lambda r:abs(r['delta']),reverse=True)[:25],maximum_change=max(abs(r['delta']) for r in rows))
 for r in rows:assert math.isfinite(r['after']) and r['after']>0
 grid=np.geomspace(32,last,10001);assert np.all(np.diff([value(t) for t in grid])<0)
# Choose one-octave knots: half-octave retains broad compressed spans; 1.5 octaves
# moves more distant anchor structure. One octave is an explicit spacing policy.
chosen=variants['1.0'];value,knots=make_curve(1.);cat=copy.deepcopy(research);by={a['id']:a for a in cat['assets']}
for r in chosen:
 a=by[r['id']];v=r['after'];prior=a['values']['neutral']['display'];factor=v/prior
 for z in a['values'].values():z['display']=v;z['meaning']='DD anchored value with monotone log-rank spacing and bounded research departure; policy scale, not observed transaction price'
 for side in a['range'].values():
  for m in side:side[m]*=factor
 a['curve_correction']=r;a['ranking_policy']['curve_version']='log-pchip-octave-20261013'
 if 'valuation_quantities' in a:a['valuation_quantities']['ranking_led_trade_value']=v
 if 'research_layer' in a:
  a['research_layer'].update(DD_baseline=r['new_baseline'],research_adjustment=v-r['new_baseline'],candidate_value=v,delta=r['delta'])
 # Updating the policy price does not change graduation eligibility, observed exposure,
 # prospect outcome distributions, or talent forecasts.
 if 'archived_policy_value' in a['ranking_policy']:a['ranking_policy']['archived_policy_value']=v
trades=[]
for t in cat['trades']:
 before=next(z for z in base['trades'] if z['id']==t['id']) if 'id' in t else base['trades'][cat['trades'].index(t)]
 sums=[sum(by[i]['values']['neutral']['display'] for i in ids) for ids in t['identities']];trades.append(dict(name=t.get('name',t.get('id','saved trade')),before=before['neutral_transfer_packages'],after=sums,delta=[sums[i]-before['neutral_transfer_packages'][i] for i in range(2)]));t['neutral_transfer_packages']=sums
 for m in t['modes'].values():m['neutral_transfer_change']=sums[1]-sums[0]
def ties(rows,key,rounding=None):
 groups=collections.defaultdict(list)
 for r in rows:groups[round(r[key],rounding) if rounding is not None else r[key]].append(r['name'])
 return [{'value':v,'players':n} for v,n in groups.items() if len(n)>1]
summary=dict(version='curve-correction-20261013',baseline_commit='26a1d75',affected=len(chosen),changed=sum(abs(r['delta'])>1e-10 for r in chosen),source_anchor_policy='DD dominates; inherited evidence weights and rank departure bounds unchanged',curve_policy='Ranks1-32 unchanged; log-log monotone PCHIP at 32,64,128,256,500; endpoints preserved; no tier-triggered steps or manual player prices',largest_changes=curves['1.0']['largest_changes'],exact_ties_before=ties(chosen,'before'),exact_ties_after=ties(chosen,'after'),rounded_ties_before=ties(chosen,'before',1),rounded_ties_after=ties(chosen,'after',1),trade_effects=trades,forecast_changes=0,limitations='Curve is transparent valuation policy, not empirically calibrated trade pricing. Archived provider date uncertainty persists. Original 11.40393583209115 result cannot be reproduced from preserved generating code and is superseded by these complete comparisons.')
cat['curve_correction_release']={k:summary[k] for k in ['version','baseline_commit','curve_policy','forecast_changes']};cat['research_layer_release']={'version':'dd-research-20261013','forecast_changes':0};cat['ranking_policy_release']['production_deployed']=True
for n,obj in [('Summary.json',summary),('Sensitivity.json',curves),('Comparison.json',chosen),('Trade_Comparison.json',trades),('Curve.json',[dict(rank=float(k),value=value(k)) for k in np.linspace(1,last,4991)])]:(D/n).write_text(json.dumps(obj,indent=2,ensure_ascii=False))
for label,rows in [('Comparison',chosen)]+[('Sensitivity_'+k,rows) for k,rows in variants.items()]:
 with (D/(label+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
packed=base64.b64encode(gzip.compress(json.dumps(cat,separators=(',',':'),ensure_ascii=False).encode(),mtime=0)).decode();html=re.sub("const packed='[^']+'","const packed='"+packed+"'",rhtml)
html=re.sub('<base href="[^"]+">','',html);html=re.sub('<div style="padding:12px;background:#fff1bd;color:#332600">.*?</div>','',html);html=html.replace('Research preview — ','');html=html.replace("['Source scope',a.ranking_policy.source_scope]","['Source scope',a.ranking_policy.source_scope],['Value curve','Monotone DD rank spacing · October 13, 2026']")
(ROOT/'trade-analyzer-beta/index.html').write_text(html)
(D/'Report.md').write_text('# Rank curve correction — October 13, 2026\n\n'+summary['curve_policy']+'\n\n'+summary['limitations']+'\n\n## Largest changes\n\n|Player|Before|After|Change|\n|---|---:|---:|---:|\n'+''.join(f"|{r['name']}|{r['before']:.2f}|{r['after']:.2f}|{r['delta']:+.2f}|\n" for r in summary['largest_changes'])+'\nAll ranked assets and alternative curves are saved in CSV and JSON; saved trade effects and exact/rounded ties are recorded separately. Forecasts, roles, availability, competitive scores and prospect distributions are preserved. DD weights and research confidence are unchanged; the correction applies equally before and after debut.\n')
# Explicitly retain the requested original265 cohort and tier-boundary audit.
original=unpack(gzip.decompress((D/'baselines/4607c16.html.gz').read_bytes()).decode());cohort={a['id'] for a in original['assets'] if a.get('ranking_policy')}
subset=[r for r in chosen if r['id'] in cohort];assert len(subset)==265
with (D/'Prospect_265_Comparison.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(subset[0]));w.writeheader();w.writerows(subset)
boundaries=[]
for scope in sorted({r['source_scope'] for r in chosen}):
 ordered=sorted([r for r in chosen if r['source_scope']==scope],key=lambda r:r['source_rank'])
 for left,right in zip(ordered,ordered[1:]):
  lt=bymap[left['id']]['ranking_policy'].get('source_tier');rt=bymap[right['id']]['ranking_policy'].get('source_tier')
  if lt!=rt:boundaries.append(dict(scope=scope,left_name=left['name'],right_name=right['name'],left_rank=left['source_rank'],right_rank=right['source_rank'],left_tier=lt,right_tier=rt,before_step=left['before']-right['before'],after_step=left['after']-right['after'],tier_bonus=0))
(D/'Tier_Boundaries.json').write_text(json.dumps(boundaries,indent=2))
with (D/'Report.md').open('a') as f:
 f.write('\n## Original prospect cohort and display rounding\n\nAll 265 original ranked prospects are included in Prospect_265_Comparison.csv. Tier boundaries have no bonus or discontinuity; each observed boundary comparison is in Tier_Boundaries.json.\n\n')
 for stage in ['before','after']:
  groups=summary['rounded_ties_'+stage];f.write(f"{stage.capitalize()}: {len(summary['exact_ties_'+stage])} exact tie groups; {len(groups)} one-decimal tie groups; largest rounded group {max(map(lambda g:len(g['players']),groups),default=1)} players. Group counts alone can rise when one broad crowd breaks into several small pairs.\n\n")
 f.write('Largest mover Mason Miller is DD overall rank69: the curve raises his baseline, with no fresh RP premium or changed saves/holds forecast. This is a rank-spacing assumption, not verification that his league resale price is44.38. Rafael Devers at rank70 changes for the same curve reason. Research and curve components are separately recorded for every player. Replacement accessibility remains the inherited league evidence; no arbitrary RP haircut is added.\n')
print(json.dumps({k:summary[k] for k in ['affected','changed','largest_changes']},indent=2))
