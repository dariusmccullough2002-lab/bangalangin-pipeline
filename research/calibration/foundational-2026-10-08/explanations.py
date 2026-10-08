"""Offline explanation renderer. Never mutates the production analyzer."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent

def explain(owner,strategy,sent,received,delta,drivers=(),interval=None,provisional=True):
 relative=abs(delta)/max(abs(sent),abs(received),1)
 if interval is not None and interval[0]<=0<=interval[1]:verdict='has an uncertain net result; the tested range includes both a gain and a loss'
 elif abs(delta)<1e-8:verdict='is approximately neutral in this scenario'
 elif delta>0:verdict=('slightly benefits' if relative<.05 else 'benefits')+' in this scenario'
 else:verdict=('is slightly worse off' if relative<.05 else 'is worse off')+' in this scenario'
 s=f'{owner}, using a {strategy} strategy, {verdict} (modeled change {delta:+.2f}).'
 if drivers:s+=' '+' '.join(drivers)
 if provisional:s+=' This is an offline scenario, not a validated fairness verdict; ownership, replacement access and legal roster capacity still need verification.'
 return s

def main():
 base=P.parent/'phase1-calibration'
 if not base.exists():base=P.parent/'phase1-2026-10-08'
 old=json.load(open(base/'results/saved-U2-comparisons.json'));case=old['cases'][0];a=case['comparisons']['contender']['B'];b=case['comparisons']['rebuild']['B']
 # First recorded side sends the package; receives Josuar. Read actual numeric direction, never hard-code a winner.
 texts=[explain('Shea Stadiums','Contender',a['surrendered'][0],a['received'][0],a['net'][0],['Receiving Josuar concentrates the prospect exposure into one player. His possible star outcome is counted once; near-term timing and any freed-slot opportunity are separate considerations.']),explain('The Sandlot Sluggers','Rebuild',b['surrendered'][1],b['received'][1],b['net'][1],['The return spreads future exposure across Celesten, Wenninger and three tradable FYPD picks. It gives up Josuar’s upper tail; the value of the fifth-round outcomes and additional player capacity remains uncertain.'])]
 out={'source':'Preserved U2 scenario only; not a new calibrated trade forecast','trade':case['sends'],'owner_explanations':texts,'uncertainty_example':explain('Example owner','Balanced',20,20.3,.3,['Immediate category gains may conflict with long-term upside.'],[-2,3]),'required_production_inputs':['each owner strategy and sent/received value','model provenance and uncertainty range','separate category/timing/replacement/acquisition/capacity contributions','ownership/eligibility evidence and missing-data flags'],'status':'OFFLINE SPECIFICATION AND RENDERER ONLY'}
 (P/'results/trade-explanation-examples.json').write_text(json.dumps(out,indent=2));print('\n\n'.join(texts))
if __name__=='__main__':main()
