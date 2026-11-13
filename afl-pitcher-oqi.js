const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function pitcherOqiRow(data,p){return p.type==='P'?data?.pitcherOqi?.pitchers?.find(r=>r.mlbamId===p.mlbamId):null;}
export function aflPitcherOqiTile(data,p){
 if(p.type!=='P')return '';
 const r=pitcherOqiRow(data,p);
 return `<div><span>Hitting difficulty (OQI)</span><b>${r?r.oqi.toFixed(1):'—'}</b><small>${r?`${r.bf} matched BF${r.smallSample?' · small sample':''}`:'Awaiting matchup data'}</small><small><a href="#afl/pitcher-oqi">Pitcher OQI →</a></small></div>`;
}
export const pitcherOqiFootnote='<p class="muted"><small>Pitcher OQI measures the hitters faced: 100 is neutral; higher means tougher opposition. Each hitter’s results against this pitcher are excluded, including from the team and league references. Small independent samples are pulled toward 100. This is opposition context, not a pitching grade.</small></p>';
export function sortPitcherOqi(rows,key='oqi'){
 if(!['oqi','bf','name'].includes(key))key='oqi';
 return [...rows].sort((a,b)=>key==='name'?a.name.localeCompare(b.name):(b[key]-a[key]||b.bf-a.bf||a.mlbamId-b.mlbamId));
}
export function renderPitcherOqi(app,data,players=[]){
 const intro='<a href="#afl">← AFL Tracker</a><h1>Pitcher Opponent Quality</h1>';
 if(!data?.pitcherOqi?.pitchers?.length){app.innerHTML=intro+'<p role="status">Pitcher OQI is currently unavailable.</p>';return;}
 const rows=data.pitcherOqi.pitchers,profiles=new Map(players.map(p=>[p.mlbamId,p]));
 const teams=[...new Set(rows.map(r=>r.team))].sort();
 app.innerHTML=intro+`<p>How strong were the hitters each pitcher faced? <strong>100 is neutral; higher means tougher opposition.</strong> Regular season and postseason combined; Fall Stars Game excluded.</p>
 <p class="muted">Through ${esc(data.through)} · ${rows.length} pitchers with matchups · Updated ${esc(new Date(data.generatedAt).toLocaleString('en-US',{timeZone:'America/New_York'}))} ET</p>
 <div class="controls"><input id="poq-search" type="search" placeholder="Search pitchers…" aria-label="Search pitcher OQI"><select id="poq-team" aria-label="Filter pitcher AFL team"><option value="">All AFL teams</option>${teams.map(t=>`<option>${esc(t)}</option>`).join('')}</select><select id="poq-sort" aria-label="Sort pitcher OQI"><option value="oqi">Opponent quality</option><option value="bf">Batters faced</option><option value="name">Name</option></select><label><input id="poq-small" type="checkbox"> Include samples below 20 BF</label></div>
 <p id="poq-count" class="muted" aria-live="polite"></p>
 <div class="tablewrap"><table><thead><tr><th>OQI rank</th><th>Pitcher</th><th>AFL / MLB team</th><th>Matched BF</th><th>Independent-data BF</th><th>Hitting difficulty (OQI)</th></tr></thead><tbody id="poq-rows"></tbody></table></div>
 ${pitcherOqiFootnote}
 <details class="afl-method"><summary>Method and circularity safeguards</summary>
 <p>For pitcher A, remove every result against A from each opposing hitter’s offensive counts and from the league and team reference counts. Recompute OPS from those independent counts. No CBS+, PQI, pitcher ERA, strikeout rate or cross-pitcher ranking normalization enters this score.</p>
 <p>Hitter quality = 1 + [independent PA ÷ (independent PA + 40)] × [0.65 × (hitter OPS ÷ league OPS − 1) + 0.35 × (hitter OPS ÷ team OPS − 1)]. Every OPS in that expression excludes A. If the independent team baseline is unavailable or zero, use the independent league baseline. A hitter without an independent offensive sample receives neutral quality of 1.</p>
 <p>OQI is 100 times the average hitter quality, weighted by completed matchup PA against A. Thus 110 means modeled opponent offensive quality 10% above neutral after shrinkage, not a 10% claim about talent. This ratio scale differs from hitter OQI’s z-score scale; values across the two metrics are not directly interchangeable.</p>
 <p>Every pitcher with a completed matchup receives a score; the default leaderboard shows at least 20 BF. Smaller samples remain available on profiles and through the checkbox. Independent-data BF counts matchups with a usable outside sample, not the size of that sample. Unmatched independent samples remain neutral rather than disappearing. Official charged-PA rules are retained for two-strike pinch hitters. Pitcher identity is the completing matchup pitcher, consistent with the existing CBS+ matchup convention.</p></details>`;
 const q=app.querySelector('#poq-search'),team=app.querySelector('#poq-team'),sort=app.querySelector('#poq-sort'),small=app.querySelector('#poq-small');
 const norm=v=>String(v).normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();
 const render=()=>{
  const filtered=rows.filter(r=>(small.checked||!r.smallSample)&&(!team.value||r.team===team.value)&&norm(r.name+' '+(profiles.get(r.mlbamId)?.mlbOrg??'')).includes(norm(q.value)));
  app.querySelector('#poq-count').textContent=filtered.length+' pitchers shown';
  app.querySelector('#poq-rows').innerHTML=sortPitcherOqi(filtered,sort.value).map(r=>{
   const p=profiles.get(r.mlbamId),name=p?.route?`<a href="${esc(p.route)}">${esc(r.name)}</a>`:esc(r.name);
   return `<tr><td>${r.rank??'—'}</td><td>${name}${r.smallSample?'<small>Small sample</small>':''}</td><td>${esc(r.team)}<small>${esc(p?.mlbOrg??'—')}</small></td><td>${r.bf}</td><td>${r.independentBf}${r.neutralBf?`<small>${r.neutralBf} neutral BF</small>`:''}</td><td><strong>${r.oqi.toFixed(1)}</strong></td></tr>`;
  }).join('')||'<tr><td colspan="6">No pitchers match these filters.</td></tr>';
 };
 q.oninput=render;team.onchange=render;sort.onchange=render;small.onchange=render;render();
}
