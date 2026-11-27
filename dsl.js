import {sectionBanner} from './section-banners.js';
import {jerseySvg} from './jerseys.js';
import {draftOutcomesHtml} from './draft-outcomes.js';
import {scoutingConfidence} from './scouting-confidence.js';
import {prospectGrades,prospectMetrics,underlyingDataSection} from './profile-context.js?v=20261126-scouting-card-final3';
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
const inputs=p=>`<b>Pipeline rank:</b> ${displayRank(p)}<br><b>Basis:</b> Full-board dynasty review · ${esc(p.ranking?.asOf??'2026-11-17')}<br><b>Previous Pipeline rank:</b> ${rank(p.ranking?.previousRank)}<br><b>Historical BA rank:</b> ${rank(p.baRank)}<br><b>Historical Seed Stage DSL rank:</b> ${rank(p.seedRank)}${p.rankingInputs?`<br><b>Separate expanded Seed list:</b> ${rank(p.rankingInputs.suppliedSeedListRank)}`:''}<br><b>Placement:</b> ${esc(p.ranking?.rationale??'')}`;

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
  app.innerHTML=`<nav class="editionnav"><a href="#dsl">← 2026 DSL rankings</a></nav><div class="player-nameplate-field"><h1>${esc(p.name)}</h1><div class="player-nameplate-meta"><span class="eyebrow">2026 DSL PROFILE</span><p>${esc(p.position)} · ${esc(p.organization)} · ${esc(resolved.owner)}</p></div></div><div class="profile"><div><section class="panel"><h2>Scouting context & dynasty outlook</h2><p>${esc(p.performanceSummary)}</p>${p.reportSections.map(s=>`<h3>${esc(s.title)}</h3><p>${esc(s.text)}</p>`).join('')}<p class="muted">${esc(p.projectionContext)}</p><details><summary>Scouting references</summary>${p.scoutingSources.map(s=>`<p>${s.url.includes('baseballamerica.com')?esc(s.label)+ ' · subscription source':`<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer"><u>${esc(s.label)} ↗</u></a>`}<br><small>${s.sourceDate?`Published ${esc(s.sourceDate)} · `:''}Retrieved ${esc(s.retrievedDate)}</small></p>`).join('')}</details>${scoutingConfidence(p,'dsl')}</section>${draftOutcomesHtml(p)}${prospectMetrics(p)}</div><aside class="panel">${grades}<h2>BangaLangin organization</h2><p>${esc(resolved.owner)}</p><p class="muted">Ownership snapshot: October 6, 2026</p><h2>Player information</h2><p>${esc(p.organization)} · ${esc(p.position)}<br>Age ${esc(dslAge(p))} · ${esc(dslNation(p))}<br>Born ${esc(bio.birthDate)}<br>${esc(bio.height)} · ${esc(bio.weight)} lb<br>Bats / throws: ${esc(bio.batSide.code)} / ${esc(bio.pitchHand.code)}</p><h2>Ranking inputs</h2><p>${inputs(p)}</p><p class="muted">All 46 placements use the approved November 20 offensive-ecosystem review. Published ranks remain historical evidence; the current order is a qualitative dynasty evaluation, not a weighted ranking formula.</p>${underlyingDataSection(p)}</aside></div>`;
  return;
 }
 app.innerHTML=`${nav}${sectionBanner('dsl')}<p class="muted">2026 DSL class board · Full Pipeline dynasty reranking · Updated November 20, 2026</p><div class="controls"><input id="dsl-search" aria-label="Search DSL prospects" placeholder="Search players or BangaLangin organizations…"><select id="dsl-org" aria-label="Filter by MLB organization"><option value="">All MLB organizations</option>${[...new Set(board.map(p=>p.organization))].sort().map(o=>`<option>${esc(o)}</option>`).join('')}</select></div><div class="dsl-results-toolbar"><p id="dsl-count" class="muted" aria-live="polite"></p><div class="door-view-toggle" role="group" aria-label="DSL rankings view"><button type="button" id="dsl-view-cards" aria-pressed="true">Cards</button><button type="button" id="dsl-view-list" aria-pressed="false">List</button></div></div><div class="dsl-grid" id="dsl-grid"></div><details class="report dsl-method"><summary>Sources and method</summary><p>All 46 participants use the user-approved November 20, 2026 editorial order. Do not double-penalize Chase% and Whiff%. Evaluate the full offensive ecosystem: carrying traits first, survivability of weaknesses second, profile cleanliness as a separator. Impact, age-to-level, discipline, athleticism, defense and positional value can offset offensive weaknesses. This is editorial judgment, not a fitted score or new scouting measurement. Current Pipeline placements weigh season-relative age, contact, usable power, walks, physical projection and plausible playing-time role. ISO ≥ .250, K ≤ 18% and BB/K ≥ 1.00 are preferred screens, not hard cutoffs. Higher-risk power ceilings can outrank safer low-impact bats. Pitchers are discounted for command, role uncertainty and development distance.</p><p class="muted">Baseball America’s September 4 ranks and the supplied Seed Stage snapshots remain historical evidence. The original 55% BA / 45% Seed composite scores are retained in the data but do not determine this editorial order. Expanded Seed list ranks and organization-only ranks are separate sources, not interchangeable DSL-wide rankings. Age is evaluated during the 2026 season rather than from the current-age card label. Small samples and repeat-level performance receive less confidence. Peña’s DSL evaluation uses his 175-PA DSL split; subsequent stateside performance is supporting evidence. No predictive model or success probabilities were fitted. Sources: attributed scouting reports, supplied Seed Stage material and official player records. Luis Hernández (SF) remains excluded because his 2026 assignment was stateside. Ownership uses the October 6 snapshot.</p></details>`;
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

