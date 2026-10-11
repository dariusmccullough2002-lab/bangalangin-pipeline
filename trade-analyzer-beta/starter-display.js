// One-way display adapter. No valuation/catalog/state writes or storage access.
export const assumptions='Assumes availability throughout the season and retention of the stated rotation role. Actual workload may be lower.';
export function qa3Eligible(outs,er){return outs>=15&&er<=2||outs>=18&&er<=3;}
export function projectionViews(asset,source){
 const evidence=asset.audit.MLB||asset.audit,scenario=source.players[asset.id];
 if(evidence.two_way_annual_projection||evidence.role!=='SP'||(!scenario&&asset.audit.kind!=='prospect'))return null;
 const expected=evidence.projection?{...evidence.projection}:null;
 if(scenario&&(!expected||expected.IP<=0))return {scenario:null,expected,unsupported:'Existing MLB talent-rate projection is unavailable; no counting-stat line invented.'};
 if(!scenario)return {scenario:null,expected,unsupported:'No preserved full MLB rotation workload and talent-rate scenario is supported for this prospect. Starts and innings are unknown.'};
 // Existing first-year rate- and aging-adjusted counts supply exactly the same
 // ER/IP and (H+BB)/IP in either view. QA3 is independent of this IP ratio.
 const ratio=scenario.line.IP/expected.IP;
 const line={IP:scenario.line.IP,K:expected.K*ratio,ER:expected.ER*ratio,H:expected.H*ratio,BB:expected.BB*ratio,
  SV:scenario.line.SV,HLD:scenario.line.HLD,QA3:Math.min(scenario.line.IP/5,scenario.starts*scenario.qa3PerStart+scenario.reliefAppearances*scenario.qa3PerRelief)};
 return {scenario:{...scenario,line},expected,unsupported:null};
}
const node=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
const number=(n,d=1)=>Number.isFinite(n)?n.toFixed(d):'Unknown';
function statistics(line){
 const table=node('table',undefined,'scenario-stat-table'),head=node('thead'),hr=node('tr');
 for(const k of ['IP','K','QA3','ERA','WHIP','ER','H','BB','SV','HLD'])hr.append(node('th',k));
 head.append(hr);const body=node('tbody'),tr=node('tr');
 const rate={...line,ERA:line.IP>0?9*line.ER/line.IP:null,WHIP:line.IP>0?(line.H+line.BB)/line.IP:null};
 for(const k of ['IP','K','QA3','ERA','WHIP','ER','H','BB','SV','HLD'])tr.append(node('td',number(rate[k],k==='ERA'?2:k==='WHIP'?3:1)));
 body.append(tr);table.append(head,body);const wrap=node('div',undefined,'scenario-table-scroll');wrap.append(table);return wrap;
}
export function mount(body,asset){
 const views=projectionViews(asset,data);if(!views)return false;
 const section=node('section',undefined,'starter-scenario'),controls=node('div',undefined,'scenario-controls');
 section.setAttribute('aria-label','2027 starter projection scenarios');
 const full=node('button','Full-season scenario'),expected=node('button','Expected-season projection');full.type=expected.type='button';
 controls.append(full,expected);const content=node('div');content.setAttribute('aria-live','polite');
 const render=mode=>{
  full.setAttribute('aria-pressed',String(mode==='full'));expected.setAttribute('aria-pressed',String(mode==='expected'));
  content.replaceChildren();content.append(node('p','2027 · '+(mode==='full'?'ROLE SCENARIO':'EXPECTED SEASON'),'eyebrow'));
  if(mode==='full'){
   const title=views.scenario?.hypothetical||asset.audit.kind==='prospect'?'Hypothetical full MLB rotation season':'Full-season scenario';
   content.append(node('h3',title),node('p',assumptions));
   if(views.scenario){const s=views.scenario;content.append(node('p',number(s.starts)+' assumed starts · '+number(s.line.IP)+' IP · '+number(s.reliefAppearances)+' incidental relief appearances','scenario-workload'),statistics(s.line),
    node('p','Workload source: preserved fitted full-role high-usage proxy. '+data.trainingLimitation,'subtle'),
    node('p','QA3: '+data.qa3Definition+'. Starts × preserved conditional performance yield, bounded by innings.','subtle'),
    node('p','Role evidence: demonstrated MLB usage; not a verified future rotation assignment. '+s.observationStatus+' · source '+(s.sourceDate||'date not recorded')+'.','subtle'));
    if(s.workloadMethod?.startsWith('insufficient'))content.append(node('p','Fallback: '+s.workloadMethod,'warning'));
   }else content.append(node('p',views.unsupported,'warning'));
  }else{
   content.append(node('h3','Expected-season projection'),node('p','Model: '+data.expectedSource+'.','subtle'));
   if(views.expected)content.append(node('p','Starts: not exported by this model · '+number(views.expected.IP)+' expected IP','scenario-workload'),statistics(views.expected));
   else content.append(node('p','No standalone first-year MLB statistical line is exported for this prospect. Its existing arrival and outcome information remains below.','warning'));
  }
  const prior=asset.audit.prospect||asset.audit;
  if(prior.eta!==undefined)content.append(node('p','Existing expected arrival: '+prior.eta+'. A hypothetical MLB season does not change that arrival forecast.','subtle'));
  content.append(node('p','Trade values use separate valuation inputs. Switching these display scenarios does not change dynasty value, rankings, replacement values, or trade calculations.','scenario-valuation-note'));
 };
 full.onclick=()=>render('full');expected.onclick=()=>render('expected');section.append(controls,content);body.append(section);render('full');return true;
}
export const data=await fetch('/data/starter-display-scenarios.json').then(r=>{if(!r.ok)throw Error('Starter scenarios unavailable');return r.json();});
