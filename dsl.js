import {sectionBanner} from './section-banners.js';
import {jerseySvg} from './jerseys.js';
import {draftOutcomesHtml} from './draft-outcomes.js';
import {scoutingConfidence} from './scouting-confidence.js';
import {pitchIqLink} from './pitchiq.js';
import {prospectGrades,prospectMetrics,prospectSavantLink} from './profile-context.js';
import {resolveDslProfile} from './dsl-profiles.js';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=v=>String(v??'').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase().replace(/[^a-z0-9]/g,'');
const rank=n=>n==null?'—':`#${n}`;
const displayRank=p=>p.ranking?.supplemental?'WATCH':rank(p.compositeRank);
const dslClubs={Royals:'KC',Yankees:'NYY',Phillies:'PHI',Brewers:'MIL',Astros:'HOU',Athletics:'ATH',Giants:'SF',Mets:'NYM',Nationals:'WSH',Reds:'CIN',Cardinals:'STL',Marlins:'MIA',Mariners:'SEA',Rays:'TB','Tampa Bay':'TB',Angels:'LAA',Braves:'ATL',Pirates:'PIT',Dodgers:'LAD','White Sox':'CWS',Rangers:'TEX',Tigers:'DET',Diamondbacks:'ARI','D-backs':'ARI',Arizona:'ARI','Red Sox':'BOS',Rockies:'COL',Colorado:'COL',Cubs:'CHC'};
export const dslJersey=p=>jerseySvg({name:p.name,mlbOrg:dslClubs[p.organization],number:p.jerseyNumber});
export function dslAge(p,asOf=new Date().toLocaleDateString('en-CA',{timeZone:'America/New_York'})){
 const dob=p.identity?.birthDate;
 if(!/^\d{4}-\d{2}-\d{2}$/.test(dob??'')||dob>asOf)return '—';
 const [year,month,day]=asOf.split('-').map(Number),[by,bm,bd]=dob.split('-').map(Number);
 return String(year-by-(month<bm||(month===bm&&day<bd)?1:0));
}
const dslNation=p=>p.identity?.birthCountry??'—';

let dataRequest,renderVersion=0;
const loadData=()=>dataRequest??=fetch('data/dsl/2026.json').then(r=>{if(!r.ok)throw Error('DSL data unavailable');return r.json();}).catch(e=>{dataRequest=undefined;throw e;});
const nav=''; // Cross-section navigation lives in the main header.
const inputs=p=>{if(p.ranking?.supplemental)return `<b>Board status:</b> Supplemental WATCH profile<br><b>Seed Stage supplied-list position:</b> ${rank(p.supplementalSeedRank)} · ${esc(p.supplementalSeedScore)} SSS<br><b>Pipeline rank:</b> Not assigned<br><b>Reason:</b> Added without disturbing the existing 1–40 order`;if(p.ranking?.basis)return `<b>Pipeline rank:</b> ${displayRank(p)}<br><b>Basis:</b> Editorial insertion · ${esc(p.ranking.asOf??'2026-11-15')}<br>${p.rankingInputs?`<b>Seed Stage supplied expanded-list rank:</b> ${rank(p.rankingInputs.suppliedSeedListRank)} · ${esc(p.rankingInputs.suppliedSeedScore)} SSS (separate snapshot)`: `<b>Seed Stage organization hitter rank:</b> ${rank(p.seedOrganizationRank)} (not a DSL-wide rank)`}<br><b>Published DSL composite inputs:</b> Not captured`;return `<b>Pipeline composite:</b> ${displayRank(p)}<br><b>BA rank (55%):</b> ${rank(p.baRank)}<br><b>Seed Stage (45%):</b> ${p.seedRank?`${rank(p.seedRank)} · ${esc(p.seedScore)} SSS`:'Not captured'}`;};
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
  app.innerHTML=`<nav class="editionnav"><a href="#dsl">← 2026 DSL rankings</a></nav><div class="player-nameplate-field"><h1>${esc(p.name)}</h1><div class="player-nameplate-meta"><span class="eyebrow">2026 DSL PROFILE</span><p>${esc(p.position)} · ${esc(p.organization)} · ${esc(resolved.owner)}</p></div></div><div class="profile"><div><section class="panel"><h2>Scouting context & dynasty outlook</h2><p>${esc(p.performanceSummary)}</p>${p.reportSections.map(s=>`<h3>${esc(s.title)}</h3><p>${esc(s.text)}</p>`).join('')}<p class="muted">${esc(p.projectionContext)}</p><details><summary>Scouting references</summary>${p.scoutingSources.map(s=>`<p>${s.url.includes('baseballamerica.com')?esc(s.label)+ ' · subscription source':`<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer"><u>${esc(s.label)} ↗</u></a>`}<br><small>${s.sourceDate?`Published ${esc(s.sourceDate)} · `:''}Retrieved ${esc(s.retrievedDate)}</small></p>`).join('')}</details>${scoutingConfidence(p,'dsl')}</section>${draftOutcomesHtml(p)}${prospectMetrics(p)}</div><aside class="panel">${grades}${prospectSavantLink(p)}${pitchIqLink(p)}<h2>BangaLangin organization</h2><p>${esc(resolved.owner)}</p><p class="muted">Ownership snapshot: October 6, 2026</p><h2>Player information</h2><p>${esc(p.organization)} · ${esc(p.position)}<br>Age ${esc(dslAge(p))} · ${esc(dslNation(p))}<br>Born ${esc(bio.birthDate)}<br>${esc(bio.height)} · ${esc(bio.weight)} lb<br>Bats / throws: ${esc(bio.batSide.code)} / ${esc(bio.pitchHand.code)}</p><h2>Ranking inputs</h2><p>${inputs(p)}</p><p class="muted">Original board: 55% BA / 45% Seed Stage when both ranks are confirmed. November additions use separate Pipeline editorial placements; source organization ranks are not DSL-wide inputs.</p></aside></div>`;
  return;
 }
 app.innerHTML=`${nav}${sectionBanner('dsl')}<p class="muted">2026 DSL class board · BA / Seed Stage inputs with Pipeline editorial placements · Updated November 17, 2026</p><div class="controls"><input id="dsl-search" aria-label="Search DSL prospects" placeholder="Search players or BangaLangin organizations…"><select id="dsl-org" aria-label="Filter by MLB organization"><option value="">All MLB organizations</option>${[...new Set(board.map(p=>p.organization))].sort().map(o=>`<option>${esc(o)}</option>`).join('')}</select></div><div class="dsl-results-toolbar"><p id="dsl-count" class="muted" aria-live="polite"></p><div class="door-view-toggle" role="group" aria-label="DSL rankings view"><button type="button" id="dsl-view-cards" aria-pressed="true">Cards</button><button type="button" id="dsl-view-list" aria-pressed="false">List</button></div></div><div class="dsl-grid" id="dsl-grid"></div><details class="report dsl-method"><summary>Sources and method</summary><p>Baseball America’s September 4, 2026 article supplies 55% of each composite score; Seed Stage’s supplied Aug. 30, 2026 scouting rank supplies 45% where verified. Composite scores are calculated as (BA rank × 0.55) + (Seed Stage rank × 0.45), then ordered ascending. If Seed Stage rank is unavailable, the BA rank carries forward unchanged.</p><p class="muted">All 46 verified participants are ranked together. Six former WATCH profiles were integrated on November 17 using age-relative contact, usable power, BB/K, physical projection and defensive opportunity. Preferred hitter screens are ISO ≥ .250, K ≤ 18% and BB/K ≥ 1.00, with ages 16–17 favored; these guide judgment rather than act as automatic eligibility rules. The existing 40-player relative order is preserved. Original composite scores remain historical inputs; new editorial placements are not outputs of the 55/45 formula. Expanded supplied Seed Stage list ranks are shown separately from the original August snapshot. Luis Hernández (SF) is intentionally excluded from this DSL board because his 2026 assignment was stateside rather than in the DSL. Inputs: Baseball America Top 35 article (paywalled), supplied Seed Stage material and official 2026 player records. Profile reports combine attributed scouting, official 2026 counts and conditional Pipeline analysis. Ownership: October 6 roster snapshot.</p></details>`;
 const search=app.querySelector('#dsl-search'),org=app.querySelector('#dsl-org');
 let view='cards';
 const render=()=>{
  const q=norm(search.value),o=org.value;
  const rows=board.map(p=>({p,resolved:resolveDslProfile(p,edition,organizations)})).filter(({p,resolved})=>norm(`${p.name} ${resolved.owner}`).includes(q)&&(!o||p.organization===o));
  app.querySelector('#dsl-count').textContent=`${rows.length} of ${board.length} players shown`;
  const results=app.querySelector('#dsl-grid');
  results.className=view==='cards'?'dsl-grid':'dsl-list';
  if(view==='list'){
   results.innerHTML=rows.length?`<div class="dsl-table-scroll"><table class="dsl-table"><caption class="sr-only">2026 DSL rankings</caption><thead><tr><th scope="col">Rank / status</th><th scope="col">Prospect</th><th scope="col">Age</th><th scope="col" title="Country of birth listed by MLB">Nation</th><th scope="col">MLB organization</th><th scope="col">BangaLangin organization</th><th scope="col">Profile</th></tr></thead><tbody>${rows.map(({p,resolved})=>`<tr><td class="dsl-list-rank">${displayRank(p)}</td><td><strong>${esc(p.name)}</strong><small>${esc(p.position)} · ${esc(p.identity?.batSide?.code??'—')}-${esc(p.identity?.pitchHand?.code??'—')}</small></td><td class="dsl-age" title="Born ${esc(p.identity?.birthDate)}">${esc(dslAge(p))}</td><td>${esc(dslNation(p))}</td><td>${esc(p.organization)}</td><td>${esc(resolved.owner)}</td><td><a href="${esc(resolved.route)}" aria-label="Open ${esc(p.name)} profile"><u>Open profile →</u></a></td></tr>`).join('')}</tbody></table></div>`:'<p>No prospects match these filters.</p>';
   return;
  }
  results.innerHTML=rows.map(({p,resolved})=>`<article class="panel dsl-card"><div class="dsl-rank">${displayRank(p)}</div><div class="dsl-card-copy"><h2>${esc(p.name)}</h2><p class="muted">${esc(p.position)} · ${esc(p.organization)} · ${esc(p.identity?.batSide?.code??'—')}-${esc(p.identity?.pitchHand?.code??'—')}</p><p class="dsl-bio"><span><strong>Age</strong> ${esc(dslAge(p))}</span><span><strong>Nation</strong> ${esc(dslNation(p))}</span></p><p class="dsl-owner"><span>BANGALANGIN ORGANIZATION</span><b>${esc(resolved.owner)}</b></p><a href="${esc(resolved.route)}"><u>Open profile →</u></a></div><a class="dsl-jersey" href="${esc(resolved.route)}" aria-label="Open ${esc(p.name)} profile" title="${esc(p.name)} · ${esc(p.organization)} organization jersey · ${esc(p.jerseyNumberSource?.team)} #${esc(p.jerseyNumber)}">${dslJersey(p)}</a></article>`).join('')||'<p>No prospects match these filters.</p>';
 };
 const setView=next=>{view=next;for(const mode of ['cards','list'])app.querySelector(`#dsl-view-${mode}`).setAttribute('aria-pressed',String(view===mode));render();};
 app.querySelector('#dsl-view-cards').onclick=()=>setView('cards');
 app.querySelector('#dsl-view-list').onclick=()=>setView('list');
 search.oninput=render;org.onchange=render;render();
}
