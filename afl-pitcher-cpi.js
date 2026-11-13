const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function pitcherCpiRow(data,p){return p.type==='P'?data?.pitcherCpi?.pitchers?.find(r=>r.mlbamId===p.mlbamId):null;}
export function aflPitcherCpiTile(data,p){
 if(p.type!=='P')return '';
 const r=pitcherCpiRow(data,p);
 return `<div><span>CPI+ · Pitching Index</span><b>${r?.cpi!=null?r.cpi.toFixed(1):'—'}</b><small>${r?(r.missingInputs?'Incomplete inputs':`${r.officialBf} BF${r.smallSample?' · small sample':''}`):'Awaiting pitching inputs'}</small><small><a href="#afl/cpi">CPI+ leaderboard →</a></small></div>`;
}
export const pitcherCpiFootnote='<p class="muted"><small>CPI+ combines pitch quality, K−BB% and ERA, with a bounded adjustment for the hitters faced. 100 is the qualified AFL pitcher average; higher is better. Opponent ratings exclude the pitcher’s own results. Experimental performance index, not a prospect grade.</small></p>';
export function sortPitcherCpi(rows,key='cpi'){
 if(!['cpi','filthPlus','kMinusBB','era','bf','oqi','name'].includes(key))key='cpi';
 return [...rows].sort((a,b)=>{
  if(key==='name')return a.name.localeCompare(b.name);
  const x=a[key],y=b[key];if(x==null)return y==null?a.name.localeCompare(b.name):1;if(y==null)return -1;
  return (key==='era'?x-y:y-x)||b.bf-a.bf||a.mlbamId-b.mlbamId;
 });
}
export function renderPitcherCpi(app,data,players=[]){
 const intro='<a href="#afl">← AFL Tracker</a><h1>CPI+ Pitcher Leaderboard</h1><h2>Contextual Pitching Index</h2>';
 if(!data?.pitcherCpi?.pitchers?.length){app.innerHTML=intro+'<p role="status">CPI+ is currently unavailable.</p>';return;}
 const rows=data.pitcherCpi.pitchers,profiles=new Map(players.map(p=>[p.mlbamId,p]));
 const teams=[...new Set(rows.map(r=>r.team))].sort();
 app.innerHTML=intro+`<p><strong>Pitch quality leads. Results and competition add context.</strong> CPI+ combines PitchIQ Filth+, whiffs, CSW and chase with K−BB% and ERA. Higher is better; 100 is the qualified AFL pitcher average.</p>
 <p class="muted">Regular season + postseason combined · Fall Stars Game excluded · Through ${esc(data.through)} · Updated ${esc(new Date(data.generatedAt).toLocaleString('en-US',{timeZone:'America/New_York'}))} ET</p>
 <p class="muted">PitchIQ input timestamp: ${esc(data.pitchSourceGeneratedAt??'Unavailable')} (provider time zone unspecified).</p>
 <div class="controls"><input id="cpi-search" type="search" placeholder="Search pitchers…" aria-label="Search CPI+ pitchers"><select id="cpi-team" aria-label="Filter CPI+ AFL team"><option value="">All AFL teams</option>${teams.map(t=>`<option>${esc(t)}</option>`).join('')}</select><select id="cpi-sort" aria-label="Sort CPI+ pitchers"><option value="cpi">CPI+</option><option value="filthPlus">Filth+</option><option value="kMinusBB">K−BB%</option><option value="era">ERA (lowest first)</option><option value="bf">Batters faced</option><option value="oqi">Batter quality faced</option><option value="name">Name</option></select><label><input id="cpi-small" type="checkbox"> Include small samples / incomplete inputs</label></div>
 <p id="cpi-count" class="muted" aria-live="polite"></p>
 <div class="tablewrap"><table><thead><tr><th>CPI+ rank</th><th>Pitcher</th><th>AFL / MLB team</th><th>IP</th><th>BF</th><th>ERA</th><th>K−BB%</th><th>Filth+</th><th>Batter quality faced</th><th>CPI+</th></tr></thead><tbody id="cpi-rows"></tbody></table></div>
 ${pitcherCpiFootnote}
 <details class="afl-method"><summary>How CPI+ works</summary>
 <p>The base blend is 65% pitch quality, 25% official K−BB% and 10% inverse ERA. Pitch quality uses standardized Filth+ (60%), whiff rate (20%), CSW (12%) and chase (8%). K−BB% appears once explicitly, in the results block. Related pitch measures share one block; they are not claimed to be statistically independent. The available AFL feed has Filth+, not a separate Stuff+ field; no invented Stuff+ grade is substituted.</p>
 <p>Standardize each input against pitchers with at least 20 BF and 50 tracked pitches; cap each standardized value at ±3. Regress pitch quality by pitches/(pitches+150), K−BB% by BF/(BF+40), and ERA by outs/(outs+45), equivalent to IP/(IP+15). ERA is calculated from earned runs and outs, not decimal baseball innings. Components are multiplied by 15 and blended. The qualified cohort is centered at 100.</p>
 <p>Batter quality remains a supporting adjustment: clamp((opponent quality−100)×0.20, −3, +3)×matched BF/(matched BF+40) points. Stronger opposition helps; weaker opposition reduces the score modestly. Opponent quality excludes ALL results against the evaluated pitcher from every hitter, team and league reference. Neither CPI+, CBS+ nor pitching results feed back into that independent opponent rating. CPI+ itself should improve when a pitcher strikes out more hitters or allows fewer earned runs; only the independent opposition score is required to remain unchanged.</p>
 <p>Every pitcher with matchups is retained. Full scores require complete pitch inputs, official K/BB/BF, earned runs and positive recorded outs; missing inputs show a dash. Default qualification is 20 official BF and 50 tracked pitches. Small samples can be included using the checkbox. These weights, shrinkage constants and context limits are transparent editorial choices, not fitted or externally validated forecasting coefficients.</p>
 <p>Sources: latest available PitchIQ AFL pitcher feed and official MLB AFL results/matchups. Source timestamps can differ: CPI+ may combine final-game results with an earlier pitch-quality snapshot. It is a descriptive performance tool, not a guarantee of MLB success.</p></details>`;
 const q=app.querySelector('#cpi-search'),team=app.querySelector('#cpi-team'),sort=app.querySelector('#cpi-sort'),small=app.querySelector('#cpi-small');
 const norm=v=>String(v).normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();
 const fmt=(v,n=1)=>v==null||!Number.isFinite(Number(v))?'—':Number(v).toFixed(n);
 const render=()=>{
  const filtered=rows.filter(r=>(small.checked||(!r.smallSample&&!r.missingInputs))&&(!team.value||r.team===team.value)&&norm(r.name+' '+(profiles.get(r.mlbamId)?.mlbOrg??'')).includes(norm(q.value)));
  app.querySelector('#cpi-count').textContent=filtered.length+' pitchers shown';
  app.querySelector('#cpi-rows').innerHTML=sortPitcherCpi(filtered,sort.value).map(r=>{
   const p=profiles.get(r.mlbamId),name=p?.route?`<a href="${esc(p.route)}">${esc(r.name)}</a>`:esc(r.name);
   return `<tr><td>${r.cpiRank??'—'}</td><td>${name}${r.missingInputs?'<small>Incomplete inputs</small>':r.smallSample?'<small>Small sample</small>':''}</td><td>${esc(r.team)}<small>${esc(p?.mlbOrg??'—')}</small></td><td>${esc(r.ip??'—')}</td><td>${r.officialBf??r.bf}</td><td>${fmt(r.era,2)}</td><td>${fmt(r.kMinusBB)}${r.kMinusBB!=null?'%':''}</td><td>${fmt(r.filthPlus)}</td><td>${fmt(r.oqi)}</td><td><strong>${fmt(r.cpi)}</strong></td></tr>`;
  }).join('')||'<tr><td colspan="10">No pitchers match these filters.</td></tr>';
 };
 q.oninput=render;team.onchange=render;sort.onchange=render;small.onchange=render;render();
}
