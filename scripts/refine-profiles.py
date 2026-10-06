"""Build player-specific publication context from dated, already-verified evidence.
No ownership or ranking changes; no new scouting grades or performance data.
"""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1];read=lambda f:json.loads((root/f).read_text())
edition=read('data/editions/october-2026.json');result={}
for p in edition['rankings']:
 s=p['seasonStats'];g=p.get('scoutingGrades');splits=s['splits'];h=next((v for v in s['groups'] if v['group']=='hitting'),None);pitch=next((v for v in s['groups'] if v['group']=='pitching'),None)
 paragraphs=[]
 if h:
  primary=max((v for v in splits if v['group']=='hitting'),key=lambda v:v['pa'],default=None)
  a=f"{p['name']} is a {dict(R='right',L='left',S='switch').get(p['bats'],'unknown')}-handed hitter listed at {p['height']} and {p['weight']} lb, with a {p['rankingPosition']} profile in the {p['mlbOrg']} system."
  if primary:a+=f" The largest verified 2026 sample came with {primary['team']} at {primary['level']}: {primary['pa']} plate appearances, a {primary['avg']} average and {primary['slg']} slugging percentage, {primary['hr']} home runs and {primary['sb']} steals."
  a+=f" Across the checked levels, his {h['kPercent']:.1f}% strikeout rate and {h['bbPercent']:.1f}% walk rate produced a {h['bbK']:.2f} BB/K ratio; his combined ISO was {h['iso']:.3f}."
  if len([v for v in splits if v['group']=='hitting'])>1:a+=' The combined rates mix levels, so the larger sample carries more weight than a brief appearance elsewhere.'
  paragraphs.append(a)
 if pitch:
  a=f"{p['name']} throws {p['throws']} and is listed at {p['height']} and {p['weight']} lb. His verified 2026 pitching sample covers {pitch['ip']} innings, with {pitch['strikeOuts']} strikeouts and {pitch['walks']} walks."
  a+=f" The {pitch['kPercent']:.1f}% strikeout rate and {pitch['bbPercent']:.1f}% walk rate yield a {pitch['kMinusBB']:.1f}-percentage-point K–BB gap; the ERA was {pitch['era']:.2f}."
  primary=max((v for v in splits if v['group']=='pitching'),key=lambda v:float(v['ip']),default=None)
  if primary:a+=f" His largest checked stint was with {primary['team']} at {primary['level']} ({primary['ip']} innings)."
  paragraphs.append(a)
 if not s['groups']:
  paragraphs.append(f"{p['name']} is {p['age']:.1f} on the edition date and is listed as {p['rankingPosition']} in the {p['mlbOrg']} organization. The checked 2026 regular-season requests returned no usable sample. This limits performance-based conclusions; it does not establish an injury, role change or loss of ability.")
 if g:
  tools=g['tools'];date=g.get('sourceDate') or 'an unspecified publication date'
  a=f"{g['source']}'s report dated {date} assigns an overall/FV grade of {g['fv']}"
  if tools:a+=' and lists '+', '.join(f"{k} {v}" for k,v in tools.items())
  a+='. Slash grades are present/future projections, not measurements of his current 2026 results.'
  if h and 'Hit' in tools and 'Game Power' in tools:
   hit=float(str(tools['Hit']).split('/')[-1].replace('+',''));power=float(str(tools['Game Power']).split('/')[-1].replace('+',''))
   if power>hit:a+=' The projected power exceeds the hit grade, so the central offensive question is whether his contact allows that damage to play against advanced pitching.'
   elif hit>power:a+=' The hit projection leads the power projection, putting more of the everyday offensive case on sustained contact and on-base production than on a large home-run total.'
   else:a+=' The hit and game-power projections are balanced; an everyday offensive outcome would require both skills to translate together.'
  if pitch and 'Command' in tools:
   a+=' The dated command projection is particularly relevant to whether the listed pitch tools can support a starting role; the season walk rate is performance evidence, not a replacement command grade.'
  paragraphs.append(a)
 else:
  paragraphs.append(f"No reliably matched numerical scouting report is available for {p['name']} in this edition. His placement is supported by {'the supplied publication inputs' if p['sourceEvidenceCount'] else 'the disclosed supplemental evaluation'}, but bat-speed, pitch-shape, velocity and defensive claims are not added without a report.")
 a=f"For dynasty evaluation, {p['name']}'s next checkpoint is "
 if h:
  if h['pa']<100:a+='a larger competitive sample before treating the current rates as established skill.'
  elif h['kPercent']>=28:a+=f"reducing the swing-and-miss pressure suggested by a {h['kPercent']:.1f}% strikeout rate while preserving extra-base impact."
  elif h['bbPercent']<6:a+=f"improving the on-base margin around a {h['bbPercent']:.1f}% walk rate as opposing pitchers become less forgiving."
  elif h['iso']>=.200:a+=f"carrying his {h['iso']:.3f} ISO into a sustained sample against stronger pitching without a deterioration in contact."
  elif h['stolenBases']>=15:a+=f"maintaining enough on-base production for the speed contribution represented by {h['stolenBases']} steals to remain useful."
  else:a+='building a clearer impact skill while preserving the current contact and approach foundation.'
 elif pitch:
  if float(pitch['ip'])<20:a+='a fuller workload before the short pitching sample can support a reliable role projection.'
  elif pitch['bbPercent']>=10:a+=f"tightening the {pitch['bbPercent']:.1f}% walk rate so strikeout ability is not offset by free baserunners."
  else:a+='maintaining the strikeout-to-walk separation over a sustained workload at his next competitive level.'
 else:a+='a verified return to game action or a new dated scouting report that makes the development path more concrete.'
 a+=f" At {p['age']:.1f} years old, his development needs to be judged against his competition and workload, rather than the strength of the fantasy roster around him."
 paragraphs.append(a)
 result[p['playerId']]={'name':p['name'],'paragraphs':paragraphs,'context':'Pipeline synthesis of the existing dated scouting grades and verified 2026 counts. Projections are conditional; no new grades, injury diagnoses or pitch-tracking measurements are assigned.','evidencePlayerId':p['playerId']}
(root/'data/profile-reports.json').write_text(json.dumps({'asOf':'2026-10-06','profiles':result},ensure_ascii=False,indent=2)+'\n')
print('Refined',len(result),'profiles using player-level evidence.')
