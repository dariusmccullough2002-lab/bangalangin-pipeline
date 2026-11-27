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
const projectedTone=grade=>grade==null?'missing':grade>=60?'plus':grade>=45?'average':'below';
const projectedPct=grade=>grade==null?0:Math.max(0,Math.min(100,(Number(grade)-20)/60*100));

function performanceHitterGrades(p){
  const s=p?.seasonStats?.groups?.find(group=>group.group==='hitting');
  if(!s)return null;
  const avg=Number(s.avg),obp=Number(s.obp),slg=Number(s.slg),hr=Number(s.homeRuns),sb=Number(s.stolenBases),pa=Number(s.pa);
  const hit=Number.isFinite(avg)?(avg>=.330?70:avg>=.300?65:avg>=.280?60:avg>=.260?55:avg>=.240?50:45):null;
  const raw=Number.isFinite(slg)?(slg>=.600?70:slg>=.550?65:slg>=.500?60:slg>=.450?55:slg>=.400?50:45):null;
  const hr600=Number.isFinite(hr)&&Number.isFinite(pa)&&pa>0?hr/pa*600:null;
  const game=hr600==null?raw:(hr600>=30?65:hr600>=24?60:hr600>=18?55:hr600>=12?50:45);
  const sb600=Number.isFinite(sb)&&Number.isFinite(pa)&&pa>0?sb/pa*600:null;
  const run=sb600==null?null:(sb600>=35?70:sb600>=25?65:sb600>=15?60:sb600>=8?55:sb600>=3?50:45);
  const ops=Number.isFinite(obp)&&Number.isFinite(slg)?obp+slg:null;
  const fv=ops==null?null:(ops>=.950?60:ops>=.875?55:ops>=.800?50:ops>=.725?45:40);
  return {type:'H',g:[hit,raw,game,run,null,null].map(snap5),fv:snap5(fv),c:'Performance-informed'};
}
function performancePitcherGrades(p){
  const s=p?.seasonStats?.groups?.find(group=>group.group==='pitching');
  if(!s)return null;
  const era=Number(s.era),k=Number(s.strikeOuts),bb=Number(s.walks),bf=Number(s.battersFaced);
  const ratio=Number.isFinite(k)&&Number.isFinite(bb)?k/Math.max(1,bb):null;
  const command=ratio==null?null:(ratio>=4.5?60:ratio>=3.5?55:ratio>=2.5?50:ratio>=1.8?45:40);
  const fv=Number.isFinite(era)?(era<=2.75?60:era<=3.50?55:era<=4.15?50:era<=4.75?45:40):null;
  return {type:'P',g:[null,null,null,null,null,snap5(command)],fv:snap5(fv),c:'Performance-informed'};
}
export function prospectProjectedGrades(p){
  const row=p?.type==='P'?performancePitcherGrades(p):performanceHitterGrades(p);
  const labels=p?.type==='P'?['Fastball','Slider','Curveball','Changeup','Splitter','Control']:['Hit','Raw power','Game power','Run','Arm','Field'];
  const hasAny=row&&(row.fv!=null||row.g?.some(value=>value!=null));
  const header=`<div class="pipeline-grade-heading"><div><span class="pipeline-grade-kicker">BANGALANGIN PIPELINE</span><h2>Projected scouting grades</h2></div><span class="pipeline-grade-confidence">${esc(row?.c??'Evidence limited')}</span></div>`;
  if(!hasAny)return `<section class="pipeline-grade-card pipeline-grade-card--empty" aria-label="Projected scouting grades">${header}<p class="pipeline-grade-empty">Not graded yet</p></section>`;
  const grades=labels.map((label,index)=>[label,row.g?.[index]??null]).concat([['Overall FV',row.fv]]);
  const rows=grades.map(([label,grade])=>`<div class="pipeline-grade-row ${grade==null?'is-missing':''}"><span class="pipeline-grade-label">${esc(label)}</span><div class="pipeline-grade-track" aria-hidden="true"><i class="pipeline-grade-fill pipeline-grade-fill--${projectedTone(grade)}" style="width:${projectedPct(grade)}%"></i></div><b class="pipeline-grade-value">${grade==null?'—':esc(grade)}</b></div>`).join('');
  return `<section class="pipeline-grade-card" aria-label="Projected scouting grades">${header}<div class="pipeline-grade-grid">${rows}</div></section>`;
}

export function prospectGrades(p){
  const existing=p.scoutingGrades;
  const mlbDraftGrades=String(p.mlbamId)==='807275'?{
    source:'MLB Pipeline',fv:45,tools:{Hit:40,Power:55,Run:45,Fielding:40,Throw:55},
    retrievedDate:'2026-11-05',scale:'Published MLB Pipeline grades on the 20–80 scale.',
    sourceUrl:'https://www.mlb.com/milb/prospects/2026/draft/dalton-wentz-807275'
  }:null;
  const id=String(p.mlbamId);
  const base=aflFanGraphsGrades[id]??fangraphsGrades[id]??existing??mlbDraftGrades;
  const supplement=fangraphsGradeSupplements[id];
  const g=base&&supplement?{...base,tools:{...(base.tools??{}),...supplement}}:base;
  if(!g)return '<p class="muted empty-grade-note">FanGraphs FV and tool grades have not yet been verified for this profile.</p>';
  if(g!==mlbDraftGrades&&!/fangraphs/i.test(g.source||''))return '<p class="muted empty-grade-note">A FanGraphs future-value grade is not currently verified for this player. Tool grades will appear here when a FanGraphs report is verified.</p>';

  const tools=g.tools??{};
  const hitterKeys=['Hit','Raw Power','Game Power','Run','Fielding','Throw'];
  const isHitter=hitterKeys.some(key=>Object.prototype.hasOwnProperty.call(tools,key));
  let rows;

  if(g===mlbDraftGrades){
    rows=Object.entries(tools);
  }else if(isHitter){
    rows=hitterKeys.map(key=>[key,tools[key]??null]);
  }else{
    const pitchOrder=['Fastball','Sinker','Cutter','Slider','Sweeper','Curveball','Changeup','Splitter'];
    const publishedPitches=pitchOrder.filter(key=>Object.prototype.hasOwnProperty.call(tools,key));
    const chosen=publishedPitches.slice(0,5);
    while(chosen.length<5)chosen.push(null);
    rows=chosen.map((key,index)=>[key??`Pitch ${index+1}`,key?tools[key]:null]);
    rows.push(['Command',tools.Command??null]);
  }

  const gradeNumber=value=>{
    if(value==null)return null;
    const raw=String(value).split('/').at(-1).trim();
    const base=Number.parseFloat(raw);
    if(!Number.isFinite(base))return null;
    return raw.endsWith('+')?base+2.5:base;
  };
  const widthFor=value=>{
    const grade=gradeNumber(value);
    return grade==null?0:Math.max(0,Math.min(100,(grade-20)/60*100));
  };
  const toneFor=value=>{
    const grade=gradeNumber(value);
    if(grade==null)return 'pipeline-grade-fill--missing';
    return grade>=60?'pipeline-grade-fill--plus':grade>=45?'pipeline-grade-fill--average':'pipeline-grade-fill--below';
  };
  const renderRow=([label,value])=>{
    if(value==null)return `<div class="pipeline-grade-row is-missing"><span class="pipeline-grade-label">${esc(label)}</span><div class="pipeline-grade-track" aria-hidden="true"><i class="pipeline-grade-fill pipeline-grade-fill--missing" style="width:0%"></i></div><b class="pipeline-grade-value">—</b></div>`;
    return `<div class="pipeline-grade-row"><span class="pipeline-grade-label">${esc(label)}</span><div class="pipeline-grade-track" aria-hidden="true"><i class="pipeline-grade-fill ${toneFor(value)}" style="width:${widthFor(value)}%"></i></div><b class="pipeline-grade-value">${esc(value)}</b></div>`;
  };

  const completeness=rows.some(([,value])=>value==null)
    ? 'Six-tool layout standardized across Pipeline profiles. “—” means the cited report or verified import did not publish that individual tool grade; Pipeline does not invent a replacement.'
    : '';
  const gradeRows=(g.fv!=null?[[g.source.includes('FanGraphs')?'Future Value':'Overall',g.fv]]:[]).concat(rows);
  return `<section class="pipeline-grade-card pipeline-grade-card--published" aria-label="Published scouting grades">
    <div class="pipeline-grade-grid">${gradeRows.map(renderRow).join('')}</div>
    ${completeness?`<p class="pipeline-grade-note">${esc(completeness)}</p>`:''}
  </section>`;
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
