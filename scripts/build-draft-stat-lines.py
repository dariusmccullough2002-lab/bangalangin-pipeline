"""Build coherent illustrative MLB role-seasons from individually reviewed inputs.

These are editorial scenario illustrations, not calibrated probability forecasts.
The inputs are selected per player, never generated from draft rank.
"""
from pathlib import Path
import json,math,hashlib
from decimal import Decimal,ROUND_HALF_UP
ROOT=Path(__file__).resolve().parents[1]

def nearest(x):return math.floor(x+0.5)
def rounded(n,d=3):return float(Decimal(str(n)).quantize(Decimal(10)**-d,rounding=ROUND_HALF_UP))
def hitter(values):
 pa,avg,obp,slg,hr,runs,rbi,sb=values
 # No sacrifices or interference other than the explicit SF count.
 hbp=max(1,nearest(pa*.01));sf=max(1,nearest(pa*.006))
 walks=max(0,nearest((obp*pa-avg*(pa-hbp-sf)-hbp)/(1-avg)))
 ab=pa-walks-hbp-sf;hits=nearest(avg*ab)
 # Triples reflect opportunities and running contribution, not an independent skill grade.
 triples=min(7,nearest(sb/7),max(0,hits-hr))
 doubles=nearest(slg*ab)-hits-2*triples-3*hr
 assert 0<=doubles<=hits-hr-triples,(values,doubles)
 singles=hits-doubles-triples-hr;tb=singles+2*doubles+3*triples+4*hr
 return {'type':'H','pa':pa,'ab':ab,'hits':hits,'singles':singles,'doubles':doubles,'triples':triples,'homeRuns':hr,'runs':runs,'rbi':rbi,'stolenBases':sb,'walks':walks,'hitByPitch':hbp,'sacFlies':sf,'avg':rounded(hits/ab,3),'obp':rounded((hits+walks+hbp)/pa,3),'slg':rounded(tb/ab,3),'ops':rounded(rounded((hits+walks+hbp)/pa,3)+rounded(tb/ab,3),3),'totalBases':tb}

def pitcher(values):
 ip,starts,era,whip,k,walks,qa,sv,holds=values
 outs=ip*3;er=nearest(era*ip/9);hits=max(0,nearest(whip*ip)-walks)
 assert qa<=starts and qa*15<=outs
 return {'type':'P','outs':outs,'ip':str(ip)+'.0','gamesStarted':starts,'earnedRuns':er,'era':rounded(er*27/outs,2),'whip':rounded((walks+hits)*3/outs,2),'strikeOuts':k,'walks':walks,'hitsAllowed':hits,'kPerWalk':rounded(k/walks,2) if walks else rounded(k*1.01,2) if k else None,'qa3':qa,'saves':sv,'holds':holds,'svh7':sv*3+holds*2}

def build():
 inputs=json.loads((ROOT/'docs/draft-outcomes-20261019/Stat_Line_Inputs.json').read_text())
 path=ROOT/'data/draft/2026.json';data=json.loads(path.read_text())
 assert {p['id'] for p in data['players']}==set(inputs['players'])
 for p in data['players']:
  source=inputs['players'][p['id']];assert source['type']==p['type']
  p['outcomes']['statLines']={key:(hitter if p['type']=='H' else pitcher)(values) for key,values in source['scenarios'].items()}
  p['outcomes']['statLineAsOf']=inputs['asOf']
  p['outcomes']['statLineBasis']='Individually selected Pipeline illustrations informed by the linked scouting; not published source forecasts, a 2027 projection, or a calibrated career median. Lines assume MLB exposure in the stated role. Runs/RBI depend on lineup context; QA3 and saves/holds are illustrative usage outcomes, not determined by ERA alone. A complete bust can produce zero MLB playing time, with undefined rate statistics.'
 path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 path=ROOT/'docs/draft-outcomes-20261019/Evidence.json';evidence=json.loads(path.read_text());by={p['id']:p for p in data['players']}
 for p in evidence['players']:p['assessmentSha256']=hashlib.sha256(json.dumps(by[p['id']]['outcomes'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
 path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
 print('Built and reconciled 336 stat lines for 112 players.')
if __name__=='__main__':build()
