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
 return `<section class="afl-card" aria-label="2026 Arizona Fall League"><span class="eyebrow">ARIZONA FALL LEAGUE / 2026</span><h3>${esc(row.aflTeam)}</h3><p class="muted">${esc(row.status)} on the official roster · Checked ${esc(data.asOf)}<br>Dated snapshot; roster status can change.</p><ul><li>${external(urls.pitchiq,'View in PitchIQ')}<small>Underlying AFL data · Search ${esc(row.name)}. If the home screen opens, select AFL.</small></li><li>${external(row.prospectRankUrl??urls.stats,row.prospectRankUrl?'2026 AFL stats — ProspectRank':'AFL tracker — ProspectRank')}<small>${row.prospectRankUrl?'Player page with separate AFL statistics.':'Hitter tracker; no verified pitcher-specific AFL page.'}</small></li><li>${external(urls.mlb,'Official AFL / MLB')} · ${external(urls.rosters,'Rosters')}</li></ul><p class="muted">External AFL results supplement the Pipeline evaluation.</p></section>`;
}
export function aflResources(){
 return `<section class="afl-resources" aria-labelledby="afl-resources-title"><span class="eyebrow">RESEARCH TOOLS / FALL BALL</span><h2 id="afl-resources-title">2026 Arizona Fall League</h2><p><a href="#afl">Explore AFL profiles & live performance →</a></p><div class="afl-resource-grid"><div>${external(urls.pitchiq,'PitchIQ')}<p>Underlying Hawk-Eye data: contact, chase, exit velocity, pitch shapes and whiffs. AFL view link; select AFL if the home screen opens, then search a player.</p></div><div>${external(urls.stats,'ProspectRank')}<p>Nightly-updated AFL hitter statistics and daily performance tracking.</p></div><div>${external(urls.mlb,'MLB AFL')}<p>Official rosters, schedule, box scores, news and video.</p></div></div><p class="afl-scouting">Scouting context: ${external('https://www.prospectslive.com/2026-arizona-fall-league-preview/','Prospects Live')} · ${external('https://blogs.fangraphs.com/welcome-to-the-2026-arizona-fall-league-scouting-prep-and-preview/','FanGraphs')}</p></section>`;
}
