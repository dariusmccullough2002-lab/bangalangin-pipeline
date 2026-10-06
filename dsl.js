import {prospectGrades,prospectMetrics,prospectSavantLink} from './profile-context.js';
import {resolveDslProfile} from './dsl-profiles.js';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=v=>String(v??'').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase().replace(/[^a-z0-9]/g,'');
const rank=n=>n==null?'—':`#${n}`;
let dataRequest,renderVersion=0;
const loadData=()=>dataRequest??=fetch('data/dsl/2026.json').then(r=>{if(!r.ok)throw Error('DSL data unavailable');return r.json();}).catch(e=>{dataRequest=undefined;throw e;});
const nav='<nav class="editionnav" aria-label="International editions"><a href="#draft">2026 Draft class</a><a href="#international">2027 International</a><a href="#dsl" aria-current="page">2026 DSL rankings</a><a href="#international-professionals">International Professionals</a><a href="#october">October Pipeline</a></nav>';
const inputs=p=>`<b>Pipeline composite:</b> ${rank(p.compositeRank)}<br><b>BA rank (55%):</b> ${rank(p.baRank)}<br><b>Seed Stage (45%):</b> ${p.seedRank?`${rank(p.seedRank)} · ${esc(p.seedScore)} SSS`:'Not captured'}`;
export async function showDsl(app,page='dsl',id,players=[],edition,organizations=[]){
 const version=++renderVersion,hash=typeof location==='undefined'?null:location.hash;
 app.innerHTML='<p class="muted" role="status">Loading DSL profiles…</p>';
 let data;
 try{data=await loadData();}catch{if(version===renderVersion&&(hash===null||location.hash===hash))app.innerHTML='<h1>DSL profiles temporarily unavailable</h1><p>Please reload to try again.</p>';return;}
 if(version!==renderVersion||(hash!==null&&location.hash!==hash))return;
 const board=data.players;
 if(page==='dsl-player'){
  let lookup;try{lookup=decodeURIComponent(id??'');}catch{lookup='';}
  const p=board.find(p=>p.id===lookup||norm(p.name)===norm(lookup));
  if(!p){app.innerHTML='<h1>DSL profile not found</h1><a href="#dsl">Return to DSL rankings</a>';return;}
  const resolved=resolveDslProfile(p,edition,organizations);
  if(resolved.current){location.hash=resolved.route;return;}
  // BA attribution is retained without adding the paywalled buttons the user removed.
  const grades=p.scoutingGrades?.source==='Baseball America'?prospectGrades(p).replace(/<a href="[^\"]+" target="_blank" rel="noopener noreferrer"><u>Read the scouting source ↗<\/u><\/a>/,''):prospectGrades(p);
  const bio=p.identity;
  app.innerHTML=`<nav class="editionnav"><a href="#dsl">← 2026 DSL rankings</a></nav><span class="eyebrow">2026 DSL PROFILE</span><h1>${esc(p.name)}</h1><p class="muted">${esc(p.position)} · ${esc(p.organization)} · ${esc(resolved.owner)}</p><div class="profile"><div><section class="panel"><h2>Scouting context & dynasty outlook</h2><p>${esc(p.performanceSummary)}</p>${p.reportSections.map(s=>`<h3>${esc(s.title)}</h3><p>${esc(s.text)}</p>`).join('')}<p class="muted">${esc(p.projectionContext)}</p><details><summary>Scouting references</summary>${p.scoutingSources.map(s=>`<p>${s.url.includes('baseballamerica.com')?esc(s.label)+ ' · subscription source':`<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer"><u>${esc(s.label)} ↗</u></a>`}<br><small>${s.sourceDate?`Published ${esc(s.sourceDate)} · `:''}Retrieved ${esc(s.retrievedDate)}</small></p>`).join('')}</details></section>${prospectMetrics(p)}</div><aside class="panel">${grades}${prospectSavantLink(p)}<h2>BangaLangin organization</h2><p>${esc(resolved.owner)}</p><p class="muted">Ownership snapshot: October 6, 2026</p><h2>Player information</h2><p>${esc(p.organization)} · ${esc(p.position)}<br>Born ${esc(bio.birthDate)}<br>${esc(bio.height)} · ${esc(bio.weight)} lb<br>Bats / throws: ${esc(bio.batSide.code)} / ${esc(bio.pitchHand.code)}</p><h2>Ranking inputs</h2><p>${inputs(p)}</p><p class="muted">55% BA / 45% Seed Stage when both ranks are confirmed. Missing Seed Stage ranks retain the BA input.</p></aside></div>`;
  return;
 }
 app.innerHTML=`${nav}<span class="eyebrow">INTERNATIONAL / DOMINICAN SUMMER LEAGUE</span><h1>2026 DSL rankings</h1><p class="muted">Baseball America’s Top 35 with Seed Stage scouting context · Updated October 6, 2026</p><div class="notice"><b>Read the sources together.</b> BA supplies 55% of the Pipeline composite and Seed Stage scouting supplies 45% when a rank is confirmed in the supplied Aug. 30 video. Players without a confirmed Seed Stage rank retain their BA input. League ownership is shown separately from the MLB organization.</div><div class="controls"><input id="dsl-search" aria-label="Search DSL prospects" placeholder="Search players or BangaLangin organizations…"><select id="dsl-org" aria-label="Filter by MLB organization"><option value="">All MLB organizations</option>${[...new Set(board.map(p=>p.organization))].sort().map(o=>`<option>${esc(o)}</option>`).join('')}</select></div><p id="dsl-count" class="muted" aria-live="polite"></p><div class="dsl-grid" id="dsl-grid"></div><article class="report"><h2>Sources and method</h2><p>Baseball America’s September 4, 2026 article supplies 55% of each composite score; Seed Stage’s supplied Aug. 30, 2026 scouting rank supplies 45% where verified. Composite scores are calculated as (BA rank × 0.55) + (Seed Stage rank × 0.45), then ordered ascending. If Seed Stage rank is unavailable, the BA rank carries forward unchanged.</p><p class="muted">Inputs: Baseball America Top 35 article (paywalled) and the supplied Seed Stage scouting video. Profile reports combine attributed scouting, official 2026 counts and conditional Pipeline analysis. Ownership: October 6 roster snapshot.</p></article>`;
 const search=app.querySelector('#dsl-search'),org=app.querySelector('#dsl-org');
 const render=()=>{
  const q=norm(search.value),o=org.value;
  const rows=board.map(p=>({p,resolved:resolveDslProfile(p,edition,organizations)})).filter(({p,resolved})=>norm(`${p.name} ${resolved.owner}`).includes(q)&&(!o||p.organization===o));
  app.querySelector('#dsl-count').textContent=`${rows.length} of ${board.length} players shown`;
  app.querySelector('#dsl-grid').innerHTML=rows.map(({p,resolved})=>`<article class="panel dsl-card"><div class="dsl-rank">${rank(p.compositeRank)}</div><div><h2>${esc(p.name)}</h2><p class="muted">${esc(p.position)} · ${esc(p.organization)}</p><p class="dsl-owner"><span>BANGALANGIN ORGANIZATION</span><b>${esc(resolved.owner)}</b></p><p>${inputs(p)}</p><a href="${esc(resolved.route)}"><u>Open profile →</u></a></div></article>`).join('')||'<p>No prospects match these filters.</p>';
 };
 search.oninput=render;org.onchange=render;render();
}
