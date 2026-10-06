import {refinedReport,acquisitionContext} from './profile-history.js';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number=(v,places=1)=>v==null?'—':Number(v).toFixed(places);
const date=g=>g.sourceDate?`Published ${esc(g.sourceDate)}`:`Publication date unavailable · retrieved ${esc(g.retrievedDate)}`;
export function prospectReport(p){
  const report=refinedReport(p);
  return `<h2>Scouting context & dynasty outlook</h2>${(report?.paragraphs??p.projectionParagraphs??[]).map(s=>`<p>${esc(s)}</p>`).join('')}<p class="muted">${esc(report?.context??p.projectionContext)}</p>${acquisitionContext(p)}${p.editorialPlacement?`<details><summary>Why this supplemental placement?</summary><p>${esc(p.editorialPlacement.reason)}</p><p>Comparison checkpoint: ${esc(p.editorialPlacement.comparisonPeer)}. Pipeline editorial ordering score ${p.orderingScore}; this is not a DD rank.</p></details>`:''}`;
}
export function prospectGrades(p){
  const g=p.scoutingGrades;
  if(!g)return '<h2>Published scouting grades</h2><p class="muted">No reliably matched published tool grades were found. This player remains ranked; missing grades are not assigned a value.</p>';
  return `<h2>Published scouting grades</h2><p><b>${esc(g.source)}</b><br><small>${date(g)}</small></p>${g.fv?`<div class="gradefv"><span>${g.source.includes('FanGraphs')?'FUTURE VALUE':'OVERALL'}</span><b>${esc(g.fv)}</b></div>`:''}<div class="toolgrades">${Object.entries(g.tools).map(([k,v])=>{const future=Number(String(v).split('/').at(-1));const width=Math.max(0,Math.min(100,(future-20)/60*100));return `<div class="toolgrade"><span>${esc(k)}</span><b>${esc(v)}</b><div class="gradebar" aria-hidden="true"><i style="width:${width}%"></i></div></div>`}).join('')}</div><p class="muted">${esc(g.scale)}</p>${g.hideSourceLink?'':`<a href="${esc(g.sourceUrl)}" target="_blank" rel="noopener noreferrer"><u>Read the scouting source ↗</u></a>`}`;
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
