import {prospectSavantLink,prospectGrades} from './profile-context.js';
import {pitchIqLink} from './pitchiq.js';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link=(url,label)=>`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer"><u>${esc(label)} ↗</u></a>`;
export const AFL_STATS_URL='https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting,pitching&season=2026&leagueIds=119&sportIds=17&limit=1000';
const pitchUrl='https://pitchiq.prospecttilt.com/#v=afl';
const FAN_GRAPHS_AFL_GRADES={695722:{hideSourceLink:true,source:'FanGraphs',sourceDate:'2026',retrievedDate:'2026-10-06',fv:'40',tools:{Hit:'20/40','Game Power':'40/50','Raw Power':'55/55',Speed:'40/40',Field:'30/45'},scale:'FanGraphs Prospects Report · 20–80 present/future tool scale. Captured from the 2026 updated player report.'}};
const fmt=(v,n=3)=>v==null||!Number.isFinite(Number(v))?'—':Number(v).toFixed(n);
const pct=(n,d)=>d>0?`${(100*(n??0)/d).toFixed(1)}%`:'—';
export function inningsToOuts(ip){if(!/^\d+\.[012]$/.test(String(ip)))return null;const [i,o]=String(ip).split('.').map(Number);return i*3+o;}
export function indexAflStats(data){
 const out={H:new Map(),P:new Map()};
 for(const g of data?.stats??[]){const key=g.group?.displayName==='hitting'?'H':g.group?.displayName==='pitching'?'P':null;if(!key)continue;
  for(const r of g.splits??[]){if(r.season!=='2026'||r.league?.id!==119||!Number.isSafeInteger(r.player?.id))continue;out[key].set(r.player.id,r.stat);}
 }return out;
}
export function aflSignal(p,s){
 if(!s)return {label:'Awaiting AFL appearance',hot:false};
 if(p.type==='H'){
  const n=Number(s.plateAppearances)||0;if(!n)return {label:'Awaiting AFL appearance',hot:false};
  if(n>=8&&Number(s.ops)>=.900)return {label:n<20?'Early hot start · small sample':'Strong AFL production',hot:true};
  return {label:n<20?'Small sample':'Building AFL sample',hot:false};
 }
 const outs=Number(s.outs??inningsToOuts(s.inningsPitched))||0,bf=Number(s.battersFaced)||0;
 if(!outs&&!bf)return {label:'Awaiting AFL appearance',hot:false};
 const diff=bf>0?100*((s.strikeOuts??0)-(s.baseOnBalls??0))/bf:null;
 if(outs>=6&&diff>=20&&s.era!=null&&s.era!==''&&Number.isFinite(Number(s.era))&&Number(s.era)<=3)return {label:outs<15?'Early bat-missing start · small sample':'Strong AFL pitching',hot:true};
 return {label:outs<15?'Small sample':'Building AFL sample',hot:false};
}
export function filterAflPlayers(rows,{query='',team='',type='',played=false}={},stats){
 const norm=v=>String(v??'').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();const terms=norm(query).split(/\s+/).filter(Boolean);
 return rows.filter(p=>(!team||String(p.aflTeamId)===team)&&(!type||p.type===type)&&(!played||stats?.[p.type]?.has(p.mlbamId))&&terms.every(t=>norm([p.name,p.mlbOrg,p.aflTeam,p.owner].join(' ')).includes(t)));
}
const statLine=(p,s)=>!s?'No recorded AFL sample':p.type==='H'?`${s.plateAppearances??0} PA · ${s.avg??'—'}/${s.obp??'—'}/${s.slg??'—'} · ${s.homeRuns??0} HR · ${s.stolenBases??0} SB`:`${s.inningsPitched??'—'} IP · ${s.era??'—'} ERA · ${s.strikeOuts??0} K / ${s.baseOnBalls??0} BB`;
const liveFacts=(p,s)=>{
 if(!s)return '<p>No AFL performance sample is recorded in this feed.</p>';
 const pairs=p.type==='H'?[['PA',s.plateAppearances],['AVG / OBP / SLG',`${s.avg} / ${s.obp} / ${s.slg}`],['HR / SB',`${s.homeRuns} / ${s.stolenBases}`],['K%',pct(s.strikeOuts,s.plateAppearances)],['BB%',pct(s.baseOnBalls,s.plateAppearances)],['OPS',s.ops]]:[['IP',s.inningsPitched],['ERA',s.era],['K / BB',`${s.strikeOuts} / ${s.baseOnBalls}`],['BF',s.battersFaced],['K%',pct(s.strikeOuts,s.battersFaced)],['BB%',pct(s.baseOnBalls,s.battersFaced)]];
 return `<div class="facts metricfacts">${pairs.map(([k,v])=>`<div><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join('')}</div><p><span class="badge">${esc(aflSignal(p,s).label)}</span></p>`;
};
export function aflProfileHtml(data,p){
 const s=p.regularStats;const gradeProfile=FAN_GRAPHS_AFL_GRADES[p.mlbamId]?{...p,scoutingGrades:FAN_GRAPHS_AFL_GRADES[p.mlbamId]}:p;const pairs=!s?[]:p.type==='H'?[['PA',s.plateAppearances],['AVG / OBP / SLG',`${fmt(s.avg)} / ${fmt(s.obp)} / ${fmt(s.slg)}`],['HR / SB',`${s.homeRuns} / ${s.stolenBases}`],['K%',fmt(s.kPercent,1)+'%'],['BB%',fmt(s.bbPercent,1)+'%'],['ISO',fmt(s.iso)]]:[['IP',s.inningsPitched],['ERA',fmt(s.era,2)],['K / BB',`${s.strikeOuts} / ${s.baseOnBalls}`],['BF',s.battersFaced],['K%',fmt(s.kPercent,1)+'%'],['BB%',fmt(s.bbPercent,1)+'%']];
 return `<a href="#afl">← Arizona Fall League</a><div class="player-nameplate-field"><h1>${esc(p.name)}</h1><div class="player-nameplate-meta"><span class="eyebrow">AFL / 2026 PLAYER PROFILE</span><p>${esc(p.position)} · ${esc(p.mlbOrg)} · ${esc(p.aflTeam)}</p></div></div><div class="profile afl-profile"><div><section class="panel"><h2>Scouting context & dynasty outlook</h2>${p.reportParagraphs.map((text,i)=>`${i?`<h3>${esc(i===1?'Regular-season foundation':text.startsWith('Published tool context')?'Published scouting context':text.startsWith('MLB translation')||text.startsWith('Dynasty outlook')?'Dynasty outlook':text.startsWith('Pipeline performance')?'Process strengths & risks':'Fall evaluation')}</h3>`:''}<p>${esc(text)}</p>`).join('')}<p class="muted">${esc(data.reportContext)} Research cutoff: ${esc(data.asOf)}.</p></section><section class="panel metricssection"><span class="eyebrow">DATED REGULAR SEASON / ${esc(p.regularScope)} 2026</span><h2>Performance evidence</h2><div class="facts metricfacts">${pairs.map(([k,v])=>`<div><span>${k}</span><b>${esc(v)}</b></div>`).join('')}</div>${!s?'<p>No verified regular-season aggregate was returned; missing data is not a zero.</p>':''}<details><summary>Level splits</summary>${p.regularSplits.map(r=>`<p><b>${esc(r.level)}</b> · ${esc(r.team)}<br>${esc(statLine(p,r.stat).replace('AFL','regular-season'))}</p>`).join('')}</details></section><section class="panel metricssection" aria-label="Current AFL performance"><span class="eyebrow">AFL ONLY / OFFICIAL MLB FEED</span><h2>Current AFL performance</h2><p id="afl-live-status" class="muted" role="status"></p><button id="afl-refresh" type="button">Refresh AFL data</button><div id="afl-profile-live"></div><p class="muted">Checked on load and every five minutes while this page stays open. Published season counts can lag games; not pitch-by-pitch data.</p></section></div><aside class="panel">${prospectGrades(gradeProfile)}<span class="eyebrow">AFL ROSTER / 2026</span><h2>${esc(p.aflTeam)}</h2><p>${esc(p.status)} in the official roster snapshot · ${esc(data.asOf)}</p><h3>BangaLangin organization</h3><p>${esc(p.owner)}</p><p class="muted">Ownership snapshot: October 6. New profiles are outside the October rankings.</p><h3>Player information</h3><p>${esc(p.mlbOrg)} · ${esc(p.position)}<br>Born ${esc(p.bio.birthDate)}<br>${esc(p.bio.height)} · ${esc(p.bio.weight)} lb<br>Bats / throws: ${esc(p.bio.batSide)} / ${esc(p.bio.pitchHand)}</p>${prospectSavantLink(p)}${pitchIqLink(p)}<section class="afl-card"><h3>Underlying AFL data</h3>${link(pitchUrl,'PitchIQ — AFL board')}<p class="muted">Search ${esc(p.name)} in the AFL view. If PitchIQ opens its home screen, select AFL first.</p>${link('https://www.prospect-portfolio.com/afl','ProspectRank AFL tracker')}</section><details><summary>Profile sources</summary>${p.sources.map(s=>`<p>${link(s.url,s.label)}</p>`).join('')}</details></aside></div>`;
}
let dataPromise,timer,version=0;
if(typeof window!=='undefined')window.addEventListener('hashchange',()=>{clearInterval(timer);version++;});
const nyDate=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
export async function showAfl(app,page,id){
 clearInterval(timer);const ownVersion=++version,hash=location.hash;app.innerHTML='<p role="status">Loading Arizona Fall League…</p>';
 let data;try{dataPromise??=fetch('data/afl/full-2026.json').then(r=>{if(!r.ok)throw Error('Roster unavailable');return r.json();});data=await dataPromise;}catch{dataPromise=null;if(ownVersion===version)app.innerHTML='<h1>AFL research unavailable</h1><p>Please reload to try again.</p>';return;}
 if(ownVersion!==version||hash!==location.hash)return;
 const p=page==='afl-player'?data.players.find(p=>String(p.mlbamId)===id):null;
 if(page==='afl-player'&&!p){app.innerHTML='<h1>AFL player not found</h1><a href="#afl">Return to AFL</a>';return;}
 // An existing prospect identity has one canonical profile.
 if(p?.hasExistingProfile){location.hash=p.route;return;}
 if(p)app.innerHTML=aflProfileHtml(data,p);
 else app.innerHTML=`<span class="eyebrow">RESEARCH TOOLS / FALL BALL</span><h1>Arizona Fall League</h1><p class="muted">2026 · All six teams · ${data.players.length} official roster profiles · Roster checked ${esc(data.asOf)}</p><p id="afl-live-status" class="muted" role="status"></p><button id="afl-refresh" type="button">Refresh AFL data</button><h2>Who is producing?</h2><div id="afl-hot" class="afl-resource-grid"></div><div class="controls afl-controls"><input id="afl-search" aria-label="Search AFL players" placeholder="Search players, organizations or owners…"><select id="afl-team" aria-label="Filter AFL team"><option value="">All AFL teams</option>${[...new Map(data.players.map(p=>[p.aflTeamId,p.aflTeam])).entries()].map(([i,n])=>`<option value="${i}">${esc(n)}</option>`).join('')}</select><select id="afl-type" aria-label="Filter AFL position"><option value="">Hitters & pitchers</option><option value="H">Hitters</option><option value="P">Pitchers</option></select><label><input id="afl-played" type="checkbox"> Recorded AFL sample</label></div><p id="afl-count" class="muted" aria-live="polite"></p><div class="tablewrap"><table><thead><tr><th>PLAYER</th><th>AFL / MLB TEAM</th><th>BANGALANGIN</th><th>AFL PERFORMANCE</th><th>INDICATOR</th></tr></thead><tbody id="afl-rows"></tbody></table></div><section class="afl-bottom-resources"><h2>AFL resources & game tracker</h2><p>${link(pitchUrl,'PitchIQ — AFL underlying data')} · ${link('https://www.prospect-portfolio.com/afl','ProspectRank AFL tracker')} · ${link('https://www.mlb.com/arizona-fall-league','Official MLB AFL')}</p><section id="afl-games" class="afl-resource-grid" aria-label="Today's AFL games"></section><div class="notice"><b>Fall performance complements the Pipeline evaluation.</b> Current MLB season counts refresh while you browse. Early games produce tiny samples; these indicators are descriptive, not talent rankings or guarantees.</div><details class="afl-method"><summary>Indicator rules & sample sizes</summary><p>Hitters: at least 8 PA and OPS of .900 or higher. Below 20 PA, explicitly labeled an early hot start. Pitchers: at least 2 IP, ERA at or below 3.00 and K−BB% at least 20%. Below 5 IP, explicitly labeled an early bat-missing start. These fixed screening rules are not park-adjusted, age-adjusted, or scouting grades. They compare neither AFL results to regular-season results nor hitters to pitchers. Missing counts produce no positive indicator.</p><p>Roster membership comes from the official full-roster snapshot, not from having statistics. Stats and game status come from the public MLB Stats API. Fetch times indicate when this page checked the feed; the provider may cache or delay updates. The page refreshes every five minutes while open. Sources or connections can fail; saved results then carry a visible snapshot label.</p></details></section>`;
 let stats=indexAflStats(data.statsSnapshot),schedule=data.scheduleSnapshot,pending=false,live=false,checked=data.retrievedAt;
 const render=()=>{
  const label=live?`MLB feed · checked ${new Date(checked).toLocaleString()} · refreshes every 5 minutes`:`Last available data · ${new Date(checked).toLocaleString()} · live refresh unavailable or still loading`;
  app.querySelector('#afl-live-status').textContent=label;
  if(p){app.querySelector('#afl-profile-live').innerHTML=liveFacts(p,stats[p.type].get(p.mlbamId));return;}
  const search=app.querySelector('#afl-search'),team=app.querySelector('#afl-team'),type=app.querySelector('#afl-type'),played=app.querySelector('#afl-played');
  const rows=filterAflPlayers(data.players,{query:search.value,team:team.value,type:type.value,played:played.checked},stats).sort((a,b)=>a.name.localeCompare(b.name));
  app.querySelector('#afl-count').textContent=`${rows.length} of ${data.players.length} rostered players shown`;
  app.querySelector('#afl-rows').innerHTML=rows.map(p=>{const s=stats[p.type].get(p.mlbamId),signal=aflSignal(p,s);return `<tr><td><a href="${esc(p.route)}">${esc(p.name)}</a><small>${esc(p.position)}</small></td><td>${esc(p.aflTeam)}<small>${esc(p.mlbOrg)}</small></td><td>${esc(p.owner)}</td><td>${esc(statLine(p,s))}</td><td><span class="badge ${signal.hot?'afl-positive':''}">${esc(signal.label)}</span></td></tr>`;}).join('')||'<tr><td colspan="5">No players match these filters.</td></tr>';
  const hot=data.players.filter(p=>aflSignal(p,stats[p.type].get(p.mlbamId)).hot);const tops=['H','P'].flatMap(t=>hot.filter(p=>p.type===t).sort((a,b)=>{const sa=stats[t].get(a.mlbamId),sb=stats[t].get(b.mlbamId);return t==='H'?Number(sb.ops)-Number(sa.ops):(sb.strikeOuts-sb.baseOnBalls)/sb.battersFaced-(sa.strikeOuts-sa.baseOnBalls)/sa.battersFaced;}).slice(0,3));
  app.querySelector('#afl-hot').innerHTML=tops.map(p=>`<article class="panel"><span class="eyebrow">${p.type==='H'?'HITTER':'PITCHER'} / AFL</span><h3><a href="${esc(p.route)}">${esc(p.name)}</a></h3><p>${esc(statLine(p,stats[p.type].get(p.mlbamId)))}</p><span class="badge afl-positive">${esc(aflSignal(p,stats[p.type].get(p.mlbamId)).label)}</span></article>`).join('')||'<p>No players currently meet the published sample and performance rules.</p>';
  const games=(schedule?.dates??[]).flatMap(d=>d.games.map(g=>({...g,date:d.date}))).filter(g=>g.teams?.home?.team&&g.teams?.away?.team);
  app.querySelector('#afl-games').innerHTML=games.map(g=>`<article class="afl-card"><span class="eyebrow">${esc(g.date)} / ${esc(g.status.detailedState)}</span><h3>${esc(g.teams.away.team.name)} at ${esc(g.teams.home.team.name)}</h3><p>${g.teams.away.score==null?'Scheduled':`${g.teams.away.score} – ${g.teams.home.score??0}`}</p>${link(`https://www.mlb.com/gameday/${g.gamePk}`,'Official game & box score')}</article>`).join('')||'<p>No AFL games are listed for today in the returned feed.</p>';
 };
 const refresh=async()=>{
  if(pending)return;pending=true;const btn=app.querySelector('#afl-refresh');btn.disabled=true;btn.textContent='Checking MLB feed…';
  const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),15000);
  try{const [s,g]=await Promise.all([fetch(AFL_STATS_URL,{signal:controller.signal}).then(r=>{if(!r.ok)throw Error('Stats unavailable');return r.json();}),fetch(`https://statsapi.mlb.com/api/v1/schedule?sportId=17&leagueId=119&date=${nyDate()}`,{signal:controller.signal}).then(r=>{if(!r.ok)throw Error('Games unavailable');return r.json();})]);if(!Array.isArray(s.stats)||!Array.isArray(g.dates))throw Error('Invalid MLB feed');if(ownVersion!==version||hash!==location.hash)return;stats=indexAflStats(s);schedule=g;live=true;checked=new Date().toISOString();}
  catch{if(ownVersion!==version||hash!==location.hash)return;live=false;}
  finally{clearTimeout(timeout);pending=false;if(ownVersion===version&&hash===location.hash){btn.disabled=false;btn.textContent='Refresh AFL data';render();}}
 };
 app.querySelector('#afl-refresh').onclick=refresh;
 if(!p){for(const sel of ['#afl-search','#afl-team','#afl-type','#afl-played'])app.querySelector(sel).addEventListener(sel==='#afl-search'?'input':'change',render);}
 render();refresh();timer=setInterval(()=>{if(document.visibilityState==='visible'&&ownVersion===version&&hash===location.hash)refresh();},300000);
}
