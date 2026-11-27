import {pitchIqLink} from './pitchiq.js';
import {aflProfileLink} from './afl-profile-links.js';
import {scoutingConfidence} from './scouting-confidence.js';
import {fangraphsGrades} from './fangraphs-grades.js';
import {aflFanGraphsGrades} from './afl-fangraphs-grades.js';
import {fangraphsGradeSupplements} from './fangraphs-grade-supplements-flat.js';
import {refinedReport,acquisitionContext} from './profile-history.js';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number=(v,places=1)=>v==null?'—':Number(v).toFixed(places);
const date=g=>g.sourceDate?`Published ${esc(g.sourceDate)}`:`Publication date unavailable · retrieved ${esc(g.retrievedDate)}`;
export function reportSources(report){
  if(!report?.sources?.length)return '';
  return `<details><summary>Scouting review sources · ${esc(report.reviewedAsOf)}</summary>${report.sources.map(s=>`<p><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer"><u>${esc(s.label)} ↗</u></a>${s.sourceDate?`<br><small>Published ${esc(s.sourceDate)}</small>`:''}</p>`).join('')}</details>`;
}
export function prospectReport(p){
  const report=refinedReport(p);
  return `<h2>Scouting context & dynasty outlook</h2>${(report?.paragraphs??p.projectionParagraphs??[]).map(s=>`<p>${esc(s)}</p>`).join('')}<p class="muted">${esc(report?.context??p.projectionContext)}</p>${reportSources(report)}${scoutingConfidence(p)}${acquisitionContext(p)}${p.editorialPlacement?`<details><summary>Why this supplemental placement?</summary><p>${esc(p.editorialPlacement.reason)}</p><p>Comparison checkpoint: ${esc(p.editorialPlacement.comparisonPeer)}. Pipeline editorial ordering score ${p.orderingScore}; this is not a DD rank.</p></details>`:''}`;
}

const snap5=value=>value==null?null:Math.round(Number(value)/5)*5;
const profileType=p=>{
 const pos=String(p?.position??p?.rankingPosition??p?.rosterPosition??'').toUpperCase();
 const tokens=pos.replaceAll('/',' ').replaceAll(',',' ').replaceAll('-',' ').split(' ').filter(Boolean);
 if(p?.type==='P'||tokens.some(token=>['P','SP','RP','RHP','LHP'].includes(token)))return 'P';
 if(p?.type==='H')return 'H';
 const groups=p?.seasonStats?.groups??[];
 if(groups.some(group=>group.group==='pitching')&&!groups.some(group=>group.group==='hitting'))return 'P';
 return 'H';
};
const profileText=p=>[
 ...(p?.scoutingParagraphs??[]),
 ...(p?.projectionParagraphs??[]),
 ...(p?.reportSections??[]).map(section=>section?.text??''),
 p?.profileContext??'',
 p?.outcomes?.ceiling??'',
 p?.outcomes?.median??'',
 p?.outcomes?.risk?.reason??'',
 ...(p?.pitchArsenal??[]).flatMap(row=>[row?.pitch??'',row?.assessment??'',row?.velocity??''])
].join(' ');
const gradeNumber=value=>{
 if(value==null)return null;
 const raw=String(value).split('/').at(-1).trim();
 const base=Number.parseFloat(raw);
 if(!Number.isFinite(base))return null;
 return raw.endsWith('+')?base+2.5:base;
};
const futureGrade=value=>{
 if(value==null)return null;
 const raw=String(value).split('/').at(-1).trim();
 return raw||null;
};
const gradeWidth=value=>{
 const grade=gradeNumber(value);
 return grade==null?0:Math.max(0,Math.min(100,(grade-20)/60*100));
};
const gradeTone=value=>{
 const grade=gradeNumber(value);
 if(grade==null)return 'pipeline-grade-fill--missing';
 return grade>=60?'pipeline-grade-fill--plus':grade>=45?'pipeline-grade-fill--average':'pipeline-grade-fill--below';
};
const renderGradeRow=([label,value])=>`<div class="pipeline-grade-row ${value==null?'is-missing':''}"><span class="pipeline-grade-label">${esc(label)}</span><div class="pipeline-grade-track" aria-hidden="true"><i class="pipeline-grade-fill ${gradeTone(value)}" style="width:${gradeWidth(value)}%"></i></div><b class="pipeline-grade-value">${value==null?'—':esc(value)}</b></div>`;
const compactGradeCard=(rows,label='Scouting grades')=>`<section class="pipeline-grade-card pipeline-grade-card--compact" aria-label="${esc(label)}"><div class="pipeline-grade-grid">${rows.map(renderGradeRow).join('')}</div></section>`;

const pitchAliases=[
 ['Fastball',['fastball','four-seam','four seam']],
 ['Sinker',['sinker']],['Cutter',['cutter']],['Slider',['slider']],['Sweeper',['sweeper']],
 ['Curveball',['curveball',' curve ']],['Changeup',['changeup','change-up',' change ']],
 ['Splitter',['splitter','split-finger','split finger']],['Forkball',['forkball',' fork ']],
 ['Breaking Ball',['breaking ball','breaking-ball']]
];
const pitchNames=p=>{
 const text=' '+profileText(p).toLowerCase()+' ';
 const explicit=(p?.pitchArsenal??[]).map(row=>String(row?.pitch??'').trim()).filter(Boolean);
 const names=[];
 const add=name=>{if(name&&!names.some(existing=>existing.toLowerCase()===name.toLowerCase()))names.push(name)};
 explicit.forEach(add);
 for(const [label,terms] of pitchAliases)if(terms.some(term=>text.includes(term)))add(label);
 const legacy=['Fastball','Slider','Curveball','Changeup','Splitter'];
 if(p?.pipelineProjectedGrades?.g)legacy.forEach((name,index)=>{if(p.pipelineProjectedGrades.g[index]!=null)add(name)});
 if(names.some(name=>['Slider','Sweeper','Curveball'].includes(name))) {
  const i=names.indexOf('Breaking Ball'); if(i>=0)names.splice(i,1);
 }
 if(names.includes('Splitter')&&names.includes('Forkball')&&(text.includes('fork/splitter')||text.includes('forkball/splitter')))names.splice(names.indexOf('Forkball'),1);
 return names;
};
const nearbyWindows=(text,needle)=>{
 const low=text.toLowerCase(),term=needle.toLowerCase(),windows=[];let from=0,index;
 while((index=low.indexOf(term,from))>=0){windows.push(low.slice(Math.max(0,index-110),Math.min(low.length,index+210)));from=index+term.length;}
 return windows;
};
const explicitNumericGrade=(text,label)=>{
 const aliases={
  Fastball:'fastball(?: velocity| effectiveness)?',Sinker:'sinker',Cutter:'cutter',Slider:'slider',Sweeper:'sweeper',
  Curveball:'curve(?:ball)?',Changeup:'change(?:up)?',Splitter:'splitter|fork\\/splitter|forkball',Forkball:'fork(?:ball)?',
  'Breaking Ball':'breaking[- ]ball',Control:'(?:control|command)'
 };
 const expr=aliases[label]??label.toLowerCase();
 const re=new RegExp('(?:'+expr+')[^.;:]{0,28}?(\\d{2})(?:\\s*[–-]\\s*(\\d{2}))?','i');
 const m=text.match(re);if(!m)return null;
 const a=Number(m[1]),b=m[2]?Number(m[2]):a;
 if(a<20||a>80||b<20||b>80)return null;
 return snap5((a+b)/2);
};
const pitchGrade=(p,label)=>{
 const legacy={Fastball:0,Slider:1,Curveball:2,Changeup:3,Splitter:4};
 if(p?.pipelineProjectedGrades?.g&&legacy[label]!=null&&p.pipelineProjectedGrades.g[legacy[label]]!=null)return p.pipelineProjectedGrades.g[legacy[label]];
 const text=profileText(p);
 const explicit=explicitNumericGrade(text,label);
 if(explicit!=null)return explicit;
 const searchLabel=label==='Breaking Ball'?'breaking ball':label;
 const windows=nearbyWindows(text,searchLabel);
 if(!windows.length&&label==='Fastball')windows.push(...nearbyWindows(text,'velocity'));
 if(label==='Fastball'){
  const low=text.toLowerCase();
  const mph=[...low.matchAll(/([0-9]{2,3}(?:[.][0-9]+)?) ?mph/g)].map(match=>Number(match[1])).filter(Number.isFinite);
  const kph=[...low.matchAll(/([0-9]{3}) ?km\/h/g)].map(match=>Number(match[1])*0.621371).filter(Number.isFinite);
  const velo=Math.max(-Infinity,...mph,...kph);
  if(velo>=99||low.includes('triple-digit')||low.includes('triple digit'))return 70;
  if(velo>=97.5||low.includes('upper-90')||low.includes('upper 90'))return 65;
  if(velo>=95||low.includes('mid-90')||low.includes('mid 90')||low.includes('premium velocity')||low.includes('power fastball'))return 60;
  if(velo>=93)return 55;
  if(Number.isFinite(velo)||low.includes('low-90')||low.includes('low 90'))return 50;
 }
 const all=windows.join(' ');
 if(/plus-plus|wipeout|elite|dominant/.test(all))return 65;
 if(/above-average|swing-and-miss|bat-missing/.test(all)||/(^|[^a-z])plus([^a-z]|$)/.test(all))return 60;
 if(/solid|usable|feel for|promising|effective/.test(all))return 55;
 if(/below-average|fringy|inconsistent|needs development|development area|less prominent/.test(all))return 45;
 return windows.length?50:null;
};
const commandGrade=p=>{
 if(p?.pipelineProjectedGrades?.g?.[5]!=null)return p.pipelineProjectedGrades.g[5];
 const med=p?.outcomes?.statLines?.median;
 if(med?.type==='P'&&Number.isFinite(Number(med.kPerWalk))){
  const ratio=Number(med.kPerWalk);
  return ratio>=4.5?60:ratio>=3.5?55:ratio>=2.5?50:ratio>=1.8?45:40;
 }
 const season=p?.seasonStats?.groups?.find(group=>group.group==='pitching');
 const native=p?.performance?.stats;
 const k=Number(season?.strikeOuts??native?.K??native?.strikeOuts);
 const bb=Number(season?.walks??season?.baseOnBalls??native?.BB??native?.walks);
 if(!Number.isFinite(k)||!Number.isFinite(bb))return explicitNumericGrade(profileText(p),'Control');
 const ratio=k/Math.max(1,bb);
 return ratio>=4.5?60:ratio>=3.5?55:ratio>=2.5?50:ratio>=1.8?45:40;
};
const pitcherFv=p=>{
 if(p?.pipelineProjectedGrades?.fv!=null)return p.pipelineProjectedGrades.fv;
 const internal=String(p?.internalEvaluation?.fv??'');
 const internalGrades=(internal.match(/[0-9]{2}/g)??[]).map(Number).filter(value=>value>=20&&value<=80);
 if(internalGrades.length)return snap5(internalGrades[0]);
 const med=p?.outcomes?.statLines?.median,ceil=p?.outcomes?.statLines?.ceiling;
 if(med?.type==='P'&&Number.isFinite(Number(med.era))){
  let fv=med.era<=3.40?60:med.era<=3.80?55:med.era<=4.30?50:med.era<=4.80?45:40;
  if((ceil?.era??9)<=3.20&&fv<60)fv+=5;
  return snap5(fv);
 }
 const season=p?.seasonStats?.groups?.find(group=>group.group==='pitching');
 const era=Number(season?.era??p?.performance?.stats?.ERA??p?.performance?.stats?.era);
 if(!Number.isFinite(era))return null;
 let fv=era<=2.25?60:era<=3.00?55:era<=3.75?50:era<=4.50?45:40;
 if(p?.performance&&!p?.seasonStats)fv=Math.min(55,fv);
 return snap5(fv);
};
const projectedPitcherRows=p=>{
 const pitches=pitchNames(p);
 const adjust=(grade,label)=>p?.j15Amateur&&grade!=null&&label!=='Fastball'?Math.max(40,grade-5):grade;
 const rows=pitches.map(name=>[name,adjust(pitchGrade(p,name),name)]).filter(([,grade])=>grade!=null);
 const control=adjust(commandGrade(p),'Control');
 if(control!=null)rows.push(['Control',snap5(control)]);
 return [['Future Value',pitcherFv(p)],...rows];
};

function performanceHitterGrades(p){
 const season=p?.seasonStats?.groups?.find(group=>group.group==='hitting');
 const native=p?.performance?.stats;
 const avg=Number(season?.avg??native?.AVG??native?.avg);
 const obp=Number(season?.obp??native?.OBP??native?.obp);
 const slg=Number(season?.slg??native?.SLG??native?.slg);
 const hr=Number(season?.homeRuns??native?.HR??native?.homeRuns);
 const sb=Number(season?.stolenBases??native?.SB??native?.stolenBases);
 const pa=Number(season?.pa??native?.PA??native?.pa);
 const strikeouts=Number(season?.strikeOuts??native?.K??native?.strikeOuts);
 if(!Number.isFinite(avg)&&!Number.isFinite(slg))return null;
 const internationalPro=!!p?.performance&&!season;
 let hit=Number.isFinite(avg)
  ?(internationalPro?(avg>=.315?60:avg>=.295?55:avg>=.275?50:avg>=.250?45:40):(avg>=.330?70:avg>=.300?65:avg>=.280?60:avg>=.260?55:avg>=.240?50:45))
  :null;
 const kPct=season?.kPercent!=null?Number(season.kPercent):(Number.isFinite(strikeouts)&&Number.isFinite(pa)&&pa>0?100*strikeouts/pa:null);
 if(hit!=null&&kPct!=null){if(kPct>=27)hit-=10;else if(kPct>=22)hit-=5;else if(!internationalPro&&kPct<=15)hit+=5;}
 const raw=Number.isFinite(slg)
  ?(internationalPro?(slg>=.600?65:slg>=.540?60:slg>=.480?55:slg>=.420?50:45):(slg>=.600?70:slg>=.550?65:slg>=.500?60:slg>=.450?55:slg>=.400?50:45))
  :null;
 const hr600=Number.isFinite(hr)&&Number.isFinite(pa)&&pa>0?hr/pa*600:null;
 const game=hr600==null?raw:(hr600>=30?65:hr600>=24?60:hr600>=18?55:hr600>=12?50:45);
 const sb600=Number.isFinite(sb)&&Number.isFinite(pa)&&pa>0?sb/pa*600:null;
 const run=sb600==null?null:(sb600>=35?70:sb600>=25?65:sb600>=15?60:sb600>=8?55:sb600>=3?50:45);
 const ops=Number.isFinite(obp)&&Number.isFinite(slg)?obp+slg:null;
 let fv=ops==null?null:(ops>=.950?60:ops>=.875?55:ops>=.800?50:ops>=.725?45:40);
 if(internationalPro&&fv!=null)fv=Math.min(55,fv);
 return {type:'H',g:[hit,raw,game,run,null,null].map(snap5),fv:snap5(fv)};
}
function modeledHitterGrades(p){
 const o=p?.outcomes,med=o?.statLines?.median,ceil=o?.statLines?.ceiling;
 if(!med||med.type!=='H'||!ceil)return null;
 const season=p?.seasonStats?.groups?.find(group=>group.group==='hitting');
 let hit=med.avg>=.290?65:med.avg>=.275?60:med.avg>=.260?55:med.avg>=.245?50:med.avg>=.225?45:40;
 if(season?.kPercent!=null){if(season.kPercent<=15)hit+=5;else if(season.kPercent>=28)hit-=5;}
 const ceilingHr=ceil.homeRuns/Math.max(1,ceil.pa)*650;
 const medianHr=med.homeRuns/Math.max(1,med.pa)*600;
 const raw=ceilingHr>=35?70:ceilingHr>=30?65:ceilingHr>=25?60:ceilingHr>=20?55:ceilingHr>=15?50:45;
 const game=medianHr>=30?65:medianHr>=25?60:medianHr>=20?55:medianHr>=15?50:medianHr>=10?45:40;
 const steals=med.stolenBases/Math.max(1,med.pa)*600;
 const run=steals>=30?70:steals>=20?65:steals>=15?60:steals>=8?55:steals>=3?50:steals>=1?45:40;
 const cushion=o?.defensiveOpportunity?.cushion;
 const field=cushion==='Strong'?60:cushion==='Moderate'?55:cushion==='Limited'?45:null;
 let fv=med.ops>=.850?60:med.ops>=.800?55:med.ops>=.750?50:med.ops>=.700?45:40;
 if((ceil.ops??0)>=.900&&fv<60)fv+=5;
 return {type:'H',g:[snap5(hit),snap5(raw),snap5(game),snap5(run),snap5(field),null],fv:snap5(fv)};
}
const projectedHitterRows=p=>{
 const row=modeledHitterGrades(p)??performanceHitterGrades(p);
 const labels=['Hit','Raw Power','Game Power','Run','Fielding','Throw'];
 const values=row?.g??Array(labels.length).fill(null);
 return [['Future Value',row?.fv??null],...labels.map((label,index)=>[label,values[index]??null])];
};
export function prospectProjectedGrades(p){
 return compactGradeCard(profileType(p)==='P'?projectedPitcherRows(p):projectedHitterRows(p),'Scouting grades');
}

export function prospectGrades(p){
 const reviewed=p?.reviewedScoutingGrades;
 if(reviewed?.source==='Pipeline scouting assessment'){
  const rows=[['Future Value',reviewed.fv],...Object.entries(reviewed.tools??{})];
  const card=compactGradeCard(rows,'Pipeline scouting estimates · 20–80').replace('<div class="pipeline-grade-grid">','<span class="pipeline-grade-kicker">Pipeline estimates · 20–80</span><div class="pipeline-grade-grid">');
  return card+`<details class="pipeline-grade-basis"><summary>Grade basis & sources</summary><p>${esc(reviewed.basis)}</p><p class="muted">Reviewed ${esc(reviewed.asOf)} · ${esc(reviewed.confidence)} confidence.</p>${Object.entries(reviewed.rationale??{}).map(([label,text])=>`<p><b>${esc(label)}:</b> ${esc(text)}</p>`).join('')}${(reviewed.sources??[]).map(source=>`<p><a href="${esc(source.url)}" target="_blank" rel="noopener noreferrer"><u>${esc(source.label)} ↗</u></a></p>`).join('')}</details>`;
 }
 const existing=p?.scoutingGrades;
 const mlbDraftGrades=String(p?.mlbamId)==='807275'?{
  source:'MLB Pipeline',fv:45,tools:{Hit:40,Power:55,Run:45,Fielding:40,Throw:55},
  retrievedDate:'2026-11-05',scale:'Published MLB Pipeline grades on the 20–80 scale.',
  sourceUrl:'https://www.mlb.com/milb/prospects/2026/draft/dalton-wentz-807275'
 }:null;
 const id=String(p?.mlbamId??'');
 const base=aflFanGraphsGrades[id]??fangraphsGrades[id]??existing??mlbDraftGrades;
 const supplement=fangraphsGradeSupplements[id];
 const g=base&&supplement?{...base,tools:{...(base.tools??{}),...supplement}}:base;
 const tools=g?.tools??{};
 const publishedCount=Object.values(tools).filter(value=>value!=null).length;
 if(!g||publishedCount===0)return prospectProjectedGrades(p);

 if(profileType(p)==='P'){
  const pitchKeys=['Fastball','Four-seam','Sinker','Cutter','Slider','Sweeper','Curveball','Changeup','Splitter','Forkball'];
  const projected=projectedPitcherRows(p);
  const projectedMap=new Map(projected);
  const rows=[['Future Value',futureGrade(g.fv)??projectedMap.get('Future Value')??null]];
  const added=new Set();
  const publishedFor=label=>{
   if(label==='Fastball')return tools.Fastball??tools['Four-seam'];
   return tools[label];
  };
  const canonical=label=>label==='Four-seam'?'fastball':label.toLowerCase();
  // A published single-pitch grade should not suppress the rest of a documented arsenal.
  // Use published grades wherever they exist, then fill only pitches actually identified
  // in the player's report/arsenal. Never manufacture generic Pitch 4 / Pitch 5 rows.
  for(const [label,value] of projected){
   if(label==='Future Value'||label==='Control')continue;
   const published=publishedFor(label);
   rows.push([label,published!=null?futureGrade(published):value]);
   added.add(canonical(label));
  }
  for(const key of pitchKeys){
   if(tools[key]==null||added.has(canonical(key)))continue;
   rows.push([key==='Four-seam'?'Fastball':key,futureGrade(tools[key])]);
   added.add(canonical(key));
  }
  const control=tools.Command??tools.Control;
  const projectedControl=projectedMap.get('Control');
  if(control!=null||projectedControl!=null)rows.push(['Control',control!=null?futureGrade(control):projectedControl]);
  return compactGradeCard(rows,'Scouting grades');
 }

 const mapped={
  Hit:tools.Hit??null,
  'Raw Power':tools['Raw Power']??tools.Power??null,
  'Game Power':tools['Game Power']??null,
  Run:tools.Run??tools.Speed??null,
  Fielding:tools.Fielding??tools.Field??null,
  Throw:tools.Throw??tools.Arm??null
 };
 const rows=[['Future Value',futureGrade(g.fv)],...['Hit','Raw Power','Game Power','Run','Fielding','Throw'].map(key=>[key,futureGrade(mapped[key])])];
 return compactGradeCard(rows,'Scouting grades');
}

export function prospectMetrics(p){
  const s=p.seasonStats;
  const cards=s.groups.map(g=>{
    const facts=g.group==='hitting'?[['PA',g.pa],['AVG / OBP / SLG',`${number(g.avg,3)} / ${number(g.obp,3)} / ${number(g.slg,3)}`],['HR / SB',`${g.homeRuns} / ${g.stolenBases}`],['K%',`${number(g.kPercent)}%`],['BB%',`${number(g.bbPercent)}%`],['BB / K',number(g.bbK,2)],['ISO',number(g.iso,3)]]:[['IP',g.ip],['ERA',number(g.era,2)],['K / BB',`${g.strikeOuts} / ${g.walks}`],['BATTERS FACED',g.battersFaced],['K%',`${number(g.kPercent)}%`],['BB%',`${number(g.bbPercent)}%`],['K–BB%',`${number(g.kMinusBB)}%`]];
    return `<h3>${g.group==='hitting'?'Hitting':'Pitching'} · all verified levels combined</h3><div class="facts metricfacts">${facts.map(([k,v])=>`<div><span>${k}</span><b>${esc(v)}</b></div>`).join('')}</div>`;
  }).join('');
  return `<section class="panel metricssection"><span class="eyebrow">2026 REGULAR SEASON / VERIFIED COUNTS</span><h2>Performance evidence</h2>${cards||'<p>No usable regular-season sample was returned for the checked minor-league levels. Missing data is left missing.</p>'}<p class="muted">${esc(s.queryContext)} Source: ${esc(s.source)} · retrieved ${esc(s.retrievedDate)}.</p>${s.splits.length?`<details><summary>See the level and team splits</summary><div class="tablewrap"><table><thead><tr><th>LEVEL</th><th>TEAM</th><th>TYPE</th><th>SAMPLE</th><th>K / BB</th><th>AVG / SLG OR ERA</th></tr></thead><tbody>${s.splits.map(r=>`<tr><td>${esc(r.level)}</td><td>${esc(r.team)}</td><td>${esc(r.group)}</td><td>${r.group==='hitting'?`${r.pa} PA`:`${r.ip} IP`}</td><td>${r.k} / ${r.bb}</td><td>${r.group==='hitting'?`${r.avg} / ${r.slg}`:r.era}</td></tr>`).join('')}</tbody></table></div></details>`:''}<details><summary>Source records and research references</summary><p><a href="https://www.milb.com/player/${p.mlbamId}" target="_blank" rel="noopener noreferrer"><u>Official player and statistics record ↗</u></a></p>${[...new Set(p.researchReferences??[])].map(u=>`<p><a href="${esc(u)}" target="_blank" rel="noopener noreferrer"><u>${esc(new URL(u).hostname)} · research source ↗</u></a></p>`).join('')}</details></section>`;
}

export function prospectSavantLink(p){
 const id=p?.mlbamId;
 const valid=(typeof id==='number'||typeof id==='string')&&/^[1-9][0-9]*$/.test(String(id))&&Number.isSafeInteger(Number(id));
 return valid?`<div class="external-data"><a href="https://prospectsavant.com/player/${id}" target="_blank" rel="noopener noreferrer"><u>Prospect Savant data ↗</u></a><p class="muted">Opens in a new tab · Data coverage varies by player and level.</p></div>`:'<div class="external-data"><p class="muted">Prospect Savant link unavailable: no matched MLBAM player ID in this profile.</p></div>';
}


// One sidebar layout across all prospect profile families. Player URLs require
// a matched MLBAM identity; an unknown identity is never guessed from a name.
export function underlyingDataSection(p,{aflRoster=null,aflPlayer=null,officialUrl=null}={}){
 const id=p?.mlbamId;
 const valid=(typeof id==='number'||typeof id==='string')&&/^[1-9][0-9]*$/.test(String(id))&&Number.isSafeInteger(Number(id));
 const safeUrl=value=>{try{const u=new URL(value);return u.protocol==='https:'?u.href:null;}catch{return null;}};
 const official=safeUrl(officialUrl);
 const afl=valid&&aflRoster?.season===2026&&aflPlayer?.mlbamId===Number(id)&&aflRoster.players.filter(row=>row.mlbamId===Number(id)).length===1;
 return `<section class="profile-underlying-data" aria-label="Underlying Data"><h2>Underlying Data</h2><div class="profile-data-links">${prospectSavantLink(p)}${pitchIqLink(p)}${official?`<div class="external-data"><a href="${esc(official)}" target="_blank" rel="noopener noreferrer"><u>Official league data ↗</u></a></div>`:''}</div>${afl?`<div class="profile-afl-data"><h3>Underlying AFL Data</h3><div class="profile-data-links"><div class="external-data"><a href="https://pitchiq.prospecttilt.com/#v=afl" target="_blank" rel="noopener noreferrer"><u>PitchIQ — AFL board ↗</u></a><p class="muted">Select AFL and search ${esc(p.name)} if the board does not open directly.</p></div><div class="external-data">${aflProfileLink(p,aflRoster)}</div></div></div>`:''}</section>`;
}
