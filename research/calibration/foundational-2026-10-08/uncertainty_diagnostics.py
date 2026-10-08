"""Empirical tail ranges, explicitly distinct from bootstrap model intervals."""
import json,math
from pathlib import Path
import numpy as np
from scipy.stats import beta
P=Path(__file__).resolve().parent;O=P/'results';dev=json.load(open(O/'delayed-arrival-diagnostic.json'));final=json.load(open(O/'prospect-calibration.json'))['predictions'];bins=[]
def wilson(k,n):
 z=1.96;p=k/n;den=1+z*z/n;c=(p+z*z/2/n)/den;rad=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return [max(0,c-rad),min(1,c+rad)]
for data,name in [(dev,'development'),(final,'2020_final')]:
 for role in [0,1]:
  for lo,hi in [(1,10),(11,25),(26,50),(51,100)]:
   rows=[r for r in data if r['pitcher']==role and lo<=r['rank']<=hi]
   if not rows:continue
   for window,key in [(5,'five_year_label' if name=='development' else 'actual_five_year_label')]+([(7,'seven_year_label')] if name=='development' else []):
    for threshold,label in [(3,'star_or_superstar'),(4,'superstar')]:
     k=sum(r[key]>=threshold for r in rows);n=len(rows);a={'cohort':name,'pitcher':role,'rank_range':[lo,hi],'window_years':window,'outcome':label,'n':n,'count':k,'rate':k/n,'wilson95':wilson(k,n),'Jeffreys95':beta.ppf([.025,.975],k+.5,n-k+.5).tolist()}
     if name=='2020_final':a['mean_predicted']=float(np.mean([sum(r['probabilities']['expanded_core'][threshold:]) for r in rows]))
     bins.append(a)
(O/'empirical-tail-ranges.json').write_text(json.dumps({'warning':'Ranges estimate bins, not individual player probabilities. Seven-year outcomes are a separate observed diagnostic, not the training target. Model bootstrap bands condition on successful all-class fits and omit source/date/label uncertainty.','bins':bins},indent=2))
print([x for x in bins if x['cohort']=='development' and x['rank_range']==[1,10]])
