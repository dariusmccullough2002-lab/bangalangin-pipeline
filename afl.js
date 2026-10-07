import {AFL_STATS_URL,indexAflStats,aflSignal} from './afl-board.js';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const urls={pitchiq:'https://pitchiq.prospecttilt.com/#v=afl',stats:'https://www.prospect-portfolio.com/afl',mlb:'https://www.mlb.com/arizona-fall-league',rosters:'https://www.mlb.com/news/2026-arizona-fall-league-rosters'};
const external=(url,label)=>`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${label} <span aria-hidden="true">↗</span></a>`;
let snapshot,loading;
// Optional research context must never prevent an existing profile from loading.
export async function loadAfl(){
 loading??=fetch('data/afl/2026.json').then(r=>{if(!r.ok)throw Error('AFL snapshot unavailable');return r.json()}).then(data=>{snapshot=data;}).catch(()=>{loading=null;});
 await loading;
}
export function aflParticipant(p,data=snapshot){
 const id=p?.mlbamId;
 if(!Number.isSafeInteger(id)||id<=0||data?.season!==2026)return null;
 const row=data.players.find(r=>r.mlbamId===id);
 // Fail closed if a profile identity changes after the roster snapshot was reviewed.
 return row&&row.name===p.name&&row.mlbOrg===(p.mlbOrg??p.draftOrganization)&&row.type===p.type?row:null;
}
export function aflCard(p,data=snapshot){
 const row=aflParticipant(p,data);if(!row)return '';
 return `<section class="afl-card" aria-label="2026 Arizona Fall League"><span class="eyebrow">ARIZONA FALL LEAGUE / 2026</span><h3>${esc(row.aflTeam)}</h3><p class="muted">${esc(row.status)} on the official roster · Checked ${esc(data.asOf)}<br>Dated snapshot; roster status can change.</p><div class="afl-inline-live" data-afl-id="${row.mlbamId}" data-afl-type="${row.type}" aria-label="Live AFL stats"><h4>Current AFL performance</h4><p class="afl-inline-status" role="status">Checking the official MLB feed…</p><div class="afl-inline-stats"></div><button type="button" class="afl-inline-refresh">Refresh AFL stats</button><small>AFL only · Refreshes every five minutes while open. Counts can lag games.</small></div><ul><li>${external(urls.pitchiq,'View in PitchIQ')}<small>Underlying AFL data · Search ${esc(row.name)}. If the home screen opens, select AFL.</small></li><li>${external(row.prospectRankUrl??urls.stats,row.prospectRankUrl?'2026 AFL stats — ProspectRank':'AFL tracker — ProspectRank')}<small>${row.prospectRankUrl?'Player page with separate AFL statistics.':'Hitter tracker; no verified pitcher-specific AFL page.'}</small></li><li>${external(urls.mlb,'Official AFL / MLB')} · ${external(urls.rosters,'Rosters')}</li></ul><p class="muted">External AFL results supplement the Pipeline evaluation.</p></section>`;
}
export function aflResources(){
 return `<section class="afl-resources" aria-labelledby="afl-resources-title"><span class="eyebrow">RESEARCH TOOLS / FALL BALL</span><h2 id="afl-resources-title">2026 Arizona Fall League</h2><p><a href="#afl">Explore AFL profiles & live performance →</a></p><div class="afl-resource-grid"><div>${external(urls.pitchiq,'PitchIQ')}<p>Underlying Hawk-Eye data: contact, chase, exit velocity, pitch shapes and whiffs. AFL view link; select AFL if the home screen opens, then search a player.</p></div><div>${external(urls.stats,'ProspectRank')}<p>Nightly-updated AFL hitter statistics and daily performance tracking.</p></div><div>${external(urls.mlb,'MLB AFL')}<p>Official rosters, schedule, box scores, news and video.</p></div></div><p class="afl-scouting">Scouting context: ${external('https://www.prospectslive.com/2026-arizona-fall-league-preview/','Prospects Live')} · ${external('https://blogs.fangraphs.com/welcome-to-the-2026-arizona-fall-league-scouting-prep-and-preview/','FanGraphs')}</p></section>`;
}

export function aflInlineStats(p,s){
 if(!s)return '<p>No recorded AFL sample in the returned feed.</p>';
 const percent=(n,d)=>Number(d)>0?`${(100*Number(n??0)/Number(d)).toFixed(1)}%`:'—';
 const line=p.type==='H'?`${s.plateAppearances??0} PA · ${s.avg??'—'}/${s.obp??'—'}/${s.slg??'—'} · ${s.homeRuns??0} HR · ${s.stolenBases??0} SB`:`${s.inningsPitched??'—'} IP · ${s.era??'—'} ERA · ${s.strikeOuts??0} K / ${s.baseOnBalls??0} BB`;
 const denominator=p.type==='H'?s.plateAppearances:s.battersFaced;
 return `<p><b>${esc(line)}</b><br>K: ${esc(percent(s.strikeOuts,denominator))} · BB: ${esc(percent(s.baseOnBalls,denominator))}${p.type==='H'?` · OPS: ${esc(s.ops??'—')}`:''}</p><span class="badge">${esc(aflSignal(p,s).label)}</span>`;
}
let inlineTimer,inlineController,inlineVersion=0,fullSnapshot;
function stopInline(){clearInterval(inlineTimer);inlineController?.abort();inlineVersion++;}
if(typeof window!=='undefined')window.addEventListener('hashchange',stopInline);
export function activateAflLive(app){
 stopInline();const cards=[...app.querySelectorAll('.afl-inline-live')];if(!cards.length)return;
 const ownVersion=inlineVersion;let pending=false,lastData=null,lastChecked=null;
 const active=()=>ownVersion===inlineVersion&&cards.every(c=>c.isConnected);
 const render=(data,label)=>{const stats=indexAflStats(data);for(const card of cards){const p={type:card.dataset.aflType};card.querySelector('.afl-inline-status').textContent=label;card.querySelector('.afl-inline-stats').innerHTML=aflInlineStats(p,stats[p.type].get(Number(card.dataset.aflId)));}};
 const refresh=async()=>{
  if(pending||!active())return;pending=true;inlineController=new AbortController();const controller=inlineController,timeout=setTimeout(()=>controller.abort(),15000);
  for(const card of cards)card.querySelector('button').disabled=true;
  try{const response=await fetch(AFL_STATS_URL,{signal:controller.signal});if(!response.ok)throw Error('AFL stats unavailable');const data=await response.json();if(!Array.isArray(data.stats))throw Error('Invalid AFL stats');if(!active())return;lastData=data;lastChecked=new Date().toLocaleString();render(data,`MLB feed · checked ${lastChecked}`);}
  catch{if(!active())return;if(lastData)render(lastData,`Last successful check ${lastChecked} · live refresh unavailable`);else{
   try{fullSnapshot??=fetch('data/afl/full-2026.json').then(r=>{if(!r.ok)throw Error('Snapshot unavailable');return r.json();}).catch(e=>{fullSnapshot=null;throw e;});const saved=await fullSnapshot;if(active())render(saved.statsSnapshot,`Saved snapshot · ${saved.asOf} · live refresh unavailable`);}
   catch{if(active())for(const card of cards)card.querySelector('.afl-inline-status').textContent='AFL feed unavailable. Use the external tracker or retry.';}
  }}finally{clearTimeout(timeout);pending=false;if(active())for(const card of cards)card.querySelector('button').disabled=false;}
 };
 for(const card of cards)card.querySelector('button').onclick=refresh;
 refresh();inlineTimer=setInterval(()=>{if(document.visibilityState==='visible')refresh();},300000);
}
