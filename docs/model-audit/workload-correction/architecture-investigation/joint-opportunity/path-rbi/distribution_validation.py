"""Score saved one-year role mixtures as discrete workload distributions."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent))
from continuation import *

def crps(p,x,y):return float(p@abs(x-y)-.5*np.sum(p[:,None]*p[None,:]*abs(x[:,None]-x[None,:])))
def run():
 result={};cases=[]
 for fam,xs in [('P',pcases),('H',hcases+[z for z in hextra if z['anchor']+1!=2020])]:
  for z in xs:
   rr=z['role'];key='PA' if rr=='H' else 'IP';c=z['components']['past_only'];p,w,_,scale=conditional_states(c,rr);actual=z['actual'].get(key,0);q={'mlbam_id':z['mlbam_id'],'anchor':z['anchor'],'role':rr,'groups':z['groups'],'CRPS_mean':abs(c[key]-actual),'CRPS_mixture':crps(p,w,actual),'mean_error':c[key]-actual,'conditional_scale':scale}
   q['PIT_lower']=float(p[w<actual].sum());q['PIT_upper']=float(p[w<=actual].sum());cases.append(q)
  ys=[z for z in cases if ('H' if z['role']=='H' else 'P')==fam];out={}
  for g in sorted({g for z in ys for g in z['groups']}):
   a=[z for z in ys if g in z['groups']];out[g]={'n':len(a),'mean_CRPS':float(np.mean([z['CRPS_mean'] for z in a])),'mixture_CRPS':float(np.mean([z['CRPS_mixture'] for z in a])),'mean_PIT_midpoint':float(np.mean([(z['PIT_lower']+z['PIT_upper'])/2 for z in a]))}
  result[fam]=out
 put('Distribution_Validation.json',{'scores':result,'scope':'Discrete role means omit within-role continuous variability. CRPS improvement alone does not certify dispersion or eight-year coverage. PIT uses ties interval; reported midpoint is diagnostic only.'});put('Distribution_Cases.json.gz',cases)
 print({k:out.get('all') for k,out in result.items()},flush=True)
if __name__=='__main__':run()
