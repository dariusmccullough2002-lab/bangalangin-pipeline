// Display-only adapter: reads copied production counts and a scenario sidecar.
// It never writes catalog, probabilities, storage, values, or trade state.
export function hitterRatios(line){return {AVG:line.AB>0?line.H/line.AB:null,OBP:line.AB+line.BB+line.HBP+line.SF>0?(line.H+line.BB+line.HBP)/(line.AB+line.BB+line.HBP+line.SF):null,SLG:line.AB>0?line.TB/line.AB:null};}
export function projectionViews(asset,source){
 const e=asset.audit.MLB||asset.audit,s=source.players[asset.id];
 if(e.two_way_annual_projection||!['H','RP'].includes(e.role)||!s||(e.role==='RP'&&!s.supported))return null;
 const expected=e.projection?{...e.projection}:null;
 const result={kind:e.role,expected,scenario:null,unsupported:s.reason};
 if(!s.supported)return result;
 const key=e.role==='H'?'PA':'IP';
 if(!expected||!Number.isFinite(expected[key])||expected[key]<=0||!Number.isFinite(s.workload)||s.workload<=0){result.unsupported='No positive production exposure supports existing MLB talent rates; no statistical scenario invented.';return result;}
 const factor=s.workload/expected[key],line={};
 if(e.role==='H'){
  for(const k of ['PA','AB','H','HR','R','RBI','SB','BB','HBP','SF','TB','2B','3B'])line[k]=Number.isFinite(expected[k])?expected[k]*factor:null;
  line.otherPA=line.PA-line.AB-line.BB-line.HBP-line.SF;
 }else{
  for(const k of ['IP','K','ER','H','BB'])line[k]=Number.isFinite(expected[k])?expected[k]*factor:null;
  line.SV=Number.isFinite(s.savePerAppearance)?s.appearances*s.savePerAppearance:null;
  line.HLD=Number.isFinite(s.holdPerAppearance)?s.appearances*s.holdPerAppearance:null;
  line.QA3=Number.isFinite(s.qa3PerAppearance)?Math.min(line.IP/5,s.appearances,s.appearances*s.qa3PerAppearance):null;
 }
 result.scenario={...s,line};result.unsupported=null;return result;
}
const node=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
const num=(x,d=1)=>Number.isFinite(x)?x.toFixed(d):'Unavailable';
function table(line,kind){
 const rates=kind==='H'?hitterRatios(line):{ERA:line.IP>0&&Number.isFinite(line.ER)?9*line.ER/line.IP:null,WHIP:line.IP>0&&Number.isFinite(line.H)&&Number.isFinite(line.BB)?(line.H+line.BB)/line.IP:null};
 const keys=kind==='H'?['PA','AB','H','HR','R','RBI','SB','BB','HBP','SF','TB','AVG','OBP','SLG']:['IP','K','ERA','WHIP','ER','H','BB','SV','HLD','QA3'];
 const wrap=node('div',undefined,'scenario-table-scroll'),t=node('table',undefined,'scenario-stat-table'),head=node('thead'),hr=node('tr'),body=node('tbody'),tr=node('tr');
 wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','Scrollable projection statistics');
 for(const key of keys){hr.append(node('th',key));tr.append(node('td',num({...line,...rates}[key],['AVG','OBP','SLG','WHIP'].includes(key)?3:key==='ERA'?2:1)));}
 head.append(hr);body.append(tr);t.append(head,body);wrap.append(t);return wrap;
}
export function mount(body,asset){
 const v=projectionViews(asset,data);if(!v)return false;
 const section=node('section',undefined,'starter-scenario'),controls=node('div',undefined,'scenario-controls');section.setAttribute('aria-label','2027 '+(v.kind==='H'?'hitter':'reliever')+' projection scenarios');
 const full=node('button','Full-role scenario'),expected=node('button','Expected-season projection');full.type=expected.type='button';controls.append(full,expected);const content=node('div');content.setAttribute('aria-live','polite');
 const render=mode=>{
  full.setAttribute('aria-pressed',String(mode==='full'));expected.setAttribute('aria-pressed',String(mode==='expected'));content.replaceChildren();
  content.append(node('p','2027 · '+(mode==='full'?'CONDITIONAL ROLE SCENARIO':'EXPECTED SEASON'),'eyebrow'));
  if(mode==='full'){
   content.append(node('h3',v.scenario?.hypothetical?'Hypothetical full MLB '+(v.kind==='H'?'hitting':'bullpen')+' role':'Full-role scenario'),node('p','Assumes availability throughout the season and retention of the stated role. Actual workload may be lower. This is a conditional scenario, not a newly validated expected-season forecast.'));
   if(v.scenario){const s=v.scenario;
    content.append(node('p',s.roleLabel+' · '+num(s.appearances)+' assumed '+(v.kind==='H'?'games · '+num(s.workload)+' PA':'relief appearances · '+num(s.workload)+' IP · 0 starts'),'scenario-workload'),table(s.line,v.kind),node('p','Workload source: '+s.method+'. '+data.limitation,'subtle'));
    const o=s.observations[0];content.append(node('p','Latest observation: '+o.year+' · '+o.status+' · '+(o.complete?'complete':'incomplete')+' · '+(o.exposure===null?'workload unavailable':num(o.exposure)+' '+(v.kind==='H'?'PA':'IP'))+' · checked '+(o.source_date||'date not recorded')+'. Missing observations are not zero seasons; verified zero does not establish medical absence.','subtle'));
    if(s.catcherSensitivity)content.append(node('p','Catcher sensitivity: games are capped at recent demonstrated total MLB games. Catcher versus DH allocation is unidentifiable; this display fallback is not a validated catcher forecast.','warning'));
    if(v.kind==='H')content.append(node('p','RBI uses the unchanged production RBI/PA rate. More PA can amplify the known high-RBI rate bias.','subtle'));
    else content.append(node('p','Saves and holds use dated, workload-matched bullpen events per appearance, not an innings multiplier. These describe retained historical leverage usage, not a verified future team assignment. Unsupported opportunities remain unavailable. QA3: '+data.qa3Definition+'; preserved performance yield per appearance, bounded by innings.','subtle'));
   }else content.append(node('p',v.unsupported,'warning'));
  }else{content.append(node('h3','Expected-season projection'),node('p','Model: '+data.expectedSource+'.','subtle'));if(v.expected)content.append(table(v.expected,v.kind));else content.append(node('p','No standalone MLB expected-season statistical line is exported. Existing arrival and outcome information remains below.','warning'));}
  const prior=asset.audit.prospect||asset.audit;if(prior.eta!==undefined)content.append(node('p','Existing expected arrival: '+prior.eta+'. A hypothetical MLB role does not change the arrival forecast.','subtle'));
  content.append(node('p','Trade values use separate valuation inputs. Switching views does not change dynasty values, rankings, replacement levels, package totals, outcome probabilities, or multiyear inputs.','scenario-valuation-note'));
 };
 full.onclick=()=>render('full');expected.onclick=()=>render('expected');section.append(controls,content);body.append(section);render('full');return true;
}
export const data=await fetch('/data/role-display-scenarios.json').then(r=>{if(!r.ok)throw Error('Role scenarios unavailable');return r.json();});
