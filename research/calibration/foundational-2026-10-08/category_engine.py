"""Exact league category math; no player valuation formula or roster optimizer."""
import numpy as np
def qa3(outs,er):return int((outs>=15 and er<=2) or (outs>=18 and er<=3))
def innings(s):
 text=str(s);a,b=(text.split('.')+['0'])[:2];assert b in ['0','1','2'];return int(a)*3+int(b)
def pitching(x):
 outs=x.get('outs',0);bb=x.get('BB',0);k=x.get('K',0)
 return np.array([x.get('ER',0),k,3*x.get('SV',0)+2*x.get('HLD',0),x.get('QA3',0),k/bb if bb else 1.01*k,3*(x.get('H',0)+bb)/outs if outs else 0.])
def hitting(x):
 ab=x.get('AB',0);h=x.get('H',0);bb=x.get('BB',0);hbp=x.get('HBP',0);sf=x.get('SF',0);den=ab+bb+hbp+sf
 obp=(h+bb+hbp)/den if den else 0;slg=x.get('TB',0)/ab if ab else 0
 return np.array([x.get('HR',0),x.get('R',0),x.get('RBI',0),x.get('SB',0),h/ab if ab else 0,obp+slg])
def points(a,b,family='P',days=7):
 # No innings minimum for hitters. Undefined zero-exposure ratios are scored only for P after eligibility.
 av=pitching(a) if family=='P' else hitting(a);bv=pitching(b) if family=='P' else hitting(b)
 if family=='P':
  if a.get('outs',0)<105*days/7:return np.zeros(6)
  if b.get('outs',0)<105*days/7:return np.ones(6)
 sign=np.array([-1,1,1,1,1,-1]) if family=='P' else np.ones(6)
 delta=(av-bv)*sign;return np.where(delta>1e-10,1,np.where(delta< -1e-10,0,.5))
def combine(*xs):
 result={}
 for x in xs:
  for k,v in x.items():result[k]=result.get(k,0)+v
 return result
