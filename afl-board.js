import {aflPitcherCpiTile,pitcherCpiFootnote,renderPitcherCpi} from './afl-pitcher-cpi.js';
import {aflCpsFootnote, aflCpsTile, featuredCpsHitters, loadAflCps, renderAflCps} from './afl-cps.js';
import {loadAmateurData} from './amateurs.js';
import {scoutingConfidence} from './scouting-confidence.js';
import {aflProfileLink} from './afl-profile-links.js';
import {loadProfileHistory,refinedReport} from './profile-history.js';
import {prospectSavantLink,prospectGrades,reportSources} from './profile-context.js';
import {pitchIqLink} from './pitchiq.js';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link=(url,label)=>`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer"><u>${esc(label)} ↗</u></a>`;
import {AFL_STATS_URL,fetchCombinedAflStats} from './afl-season-stats.js';
export {AFL_STATS_URL};
const pitchUrl='https://pitchiq.prospecttilt.com/#v=afl';
const FAN_GRAPHS_AFL_GRADES={695722:{hideSourceLink:true,source:'FanGraphs',sourceDate:'2026',retrievedDate:'2026-10-06',fv:'40',tools:{Hit:'20/40','Game Power':'40/50','Raw Power':'55/55',Speed:'40/40',Field:'30/45'},scale:'FanGraphs Prospects Report · 20–80 present/future tool scale. Captured from the 2026 updated player report.'}};
const fmt=(v,n=3)=>v==null||!Number.isFinite(Number(v))?'—':Number(v).toFixed(n);
const pct=(n,d)=>d>0?`${(100*(n??0)/d).toFixed(1)}%`:'—';
export function aflAge(birthDate,asOf){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(birthDate??'')||!/^\d{4}-\d{2}-\d{2}$/.test(asOf??''))return '—';
 const born=new Date(birthDate+'T00:00:00Z'),date=new Date(asOf+'T00:00:00Z');
 if(!Number.isFinite(born.getTime())||!Number.isFinite(date.getTime())||born>date)return '—';
 return date.getUTCFullYear()-born.getUTCFullYear()-(asOf.slice(5)<birthDate.slice(5)?1:0);
}
export function sortAflPlayers(players,stats,mode='name'){
 const alpha=(a,b)=>a.name.localeCompare(b.name);
 if(mode==='age')return [...players].sort((a,b)=>String(b.bio?.birthDate??'').localeCompare(String(a.bio?.birthDate??''))||alpha(a,b));
 if(mode!=='performance')return [...players].sort(alpha);
 // Keep unlike statistics in separate role groups; no invented hitter/pitcher composite.
 const metric=p=>{
  const s=stats[p.type].get(p.mlbamId);
  if(!hasAflSample(p,s))return {tier:0,score:-Infinity,sample:0,era:Infinity};
  const sample=p.type==='H'?Number(s.plateAppearances):Number(s.outs??inningsToOuts(s.inningsPitched));
  const score=p.type==='H'?Number(s.ops):Number(s.battersFaced)>0?(Number(s.strikeOuts)-Number(s.baseOnBalls))/Number(s.battersFaced):NaN;
  if(!Number.isFinite(score))return {tier:0,score:-Infinity,sample,era:Infinity};
  return {tier:sample>=(p.type==='H'?20:15)?2:1,score,sample,era:Number(s.era??Infinity)};
 };
 return [...players].sort((a,b)=>{
  const x=metric(a),y=metric(b);
  return y.tier-x.tier||a.type.localeCompare(b.type)||y.score-x.score||(a.type==='P'?x.era-y.era:0)||y.sample-x.sample||alpha(a,b);
 });
}
export function inningsToOuts(ip){if(!/^\d+\.[012]$/.test(String(ip)))return null;const [i,o]=String(ip).split('.').map(Number);return i*3+o;}
export function indexAflStats(data){
 const out={H:new Map(),P:new Map()};
 for(const g of data?.stats??[]){const key=g.group?.displayName==='hitting'?'H':g.group?.displayName==='pitching'?'P':null;if(!key)continue;
  for(const r of g.splits??[]){if(r.season!=='2026'||r.league?.id!==119||!Number.isSafeInteger(r.player?.id))continue;out[key].set(r.player.id,r.stat);}
 }return out;
}
export function validateAflRefresh(previous,incoming){
 const groups=new Set((incoming?.stats??[]).map(g=>g.group?.displayName));
 if(!groups.has('hitting')||!groups.has('pitching'))throw Error('Incomplete AFL feed');
 for(const g of incoming.stats){if(g.totalSplits!=null&&g.splits?.length<g.totalSplits)throw Error('Truncated AFL feed');}
 const before=indexAflStats(previous),after=indexAflStats(incoming);
 for(const type of ['H','P'])for(const id of before[type].keys())if(!after[type].has(id))throw Error('AFL feed omitted previously reported players');
 return incoming;
}
export async function fetchAflUpdates(previous,date,{fetcher=fetch,signal}={}){
 const json=async url=>{const response=await fetcher(url,{signal,cache:'no-store'});if(!response.ok)throw Error('MLB feed unavailable');return response.json();};
 const [stats,schedule]=await Promise.allSettled([fetchCombinedAflStats({fetcher,signal}),json(`https://statsapi.mlb.com/api/v1/schedule?sportId=17&leagueId=119&date=${date}`)]);
 const result={stats:null,schedule:null,statsError:null,scheduleError:null};
 const reason=e=>e?.name==='AbortError'?'request timed out':e?.message||'MLB feed unavailable';
 try{if(stats.status==='rejected')throw stats.reason;result.stats=validateAflRefresh(previous,stats.value);}catch(error){result.statsError=reason(error);}
 try{if(schedule.status==='rejected')throw schedule.reason;if(!Array.isArray(schedule.value?.dates))throw Error('Invalid game schedule');result.schedule=schedule.value;}catch(error){result.scheduleError=reason(error);}
 return result;
}
export function shiftAflDate(date,days){const d=new Date(`${date}T12:00:00Z`);d.setUTCDate(d.getUTCDate()+days);return d.toISOString().slice(0,10);}
export async function fetchAflSchedule(date,{fetcher=fetch,signal}={}){const response=await fetcher(`https://statsapi.mlb.com/api/v1/schedule?sportId=17&leagueId=119&date=${encodeURIComponent(date)}`,{signal,cache:'no-store'});if(!response.ok)throw Error('MLB schedule unavailable');const result=await response.json();if(!Array.isArray(result?.dates))throw Error('Invalid game schedule');return result;}
export function aflGamesHtml(schedule,date,{error=null,loading=false,saved=false}={}){
 const games=(schedule?.dates??[]).filter(d=>d.date===date).flatMap(d=>(d.games??[]).filter(g=>g.teams?.home?.team&&g.teams?.away?.team));
 const note=loading?'<p role="status">Checking the schedule…</p>':error?`<p role="status">Schedule refresh unavailable.${saved?' Showing the last available schedule for this date.':' This date’s games could not be confirmed.'}</p>`:saved?'<p class="muted">Saved schedule for this date · checking for updates.</p>':'';
 return note+(games.map(g=>{const time=g.gameDate?new Intl.DateTimeFormat('en-US',{timeZone:'America/Phoenix',hour:'numeric',minute:'2-digit'}).format(new Date(g.gameDate)):null;return `<article class="afl-card"><span class="eyebrow">${esc(date)} / ${esc(g.status?.detailedState??'Scheduled')}</span><h3>${esc(g.teams.away.team.name)} at ${esc(g.teams.home.team.name)}</h3><p>${g.teams.away.score==null?(time?`${esc(time)} Arizona time`:'Time TBD'):`${esc(g.teams.away.score)} – ${esc(g.teams.home.score??'—')}`}</p>${g.venue?.name?`<p>${esc(g.venue.name)}</p>`:''}${link(`https://www.mlb.com/gameday/${g.gamePk}`,'Official game & box score')}</article>`;}).join('')||(!loading&&!error&&!saved?'<p>No AFL games are listed for this date in the returned feed.</p>':''));
}
export function hasAflSample(p,s){return !!s&&(p.type==='H'?Number(s.plateAppearances)>0:Number(s.outs??inningsToOuts(s.inningsPitched))>0||Number(s.battersFaced)>0);}
const statsCacheKey='pipeline-afl-stats-2026-v1';
function loadStatsCache(fallback){try{const cached=JSON.parse(localStorage.getItem(statsCacheKey));return cached?.data?{...cached,data:validateAflRefresh(fallback,cached.data)}:null;}catch{return null;}}
function saveStatsCache(data,checked){try{localStorage.setItem(statsCacheKey,JSON.stringify({data,checked}));}catch{}}
export function aflSignal(p,s){
 if(!s)return {label:'Awaiting AFL appearance',hot:false};
 if(p.type==='H'){
  const n=Number(s.plateAppearances)||0;if(!n)return {label:'Awaiting AFL appearance',hot:false};
  if(n>=8&&Number(s.ops)>=.900)return {label:n<20?'Early hot start · small sample':'Strong AFL production',hot:true};
  const ops=s.ops==null||s.ops===''?NaN:Number(s.ops);
  if(n>=8&&Number.isFinite(ops)&&ops<.700)return {label:n<20?'Struggling at the plate · small sample':'Struggling at the plate',hot:false};
  return {label:n<20?'Small sample':'Mixed AFL results',hot:false};
 }
 const outs=Number(s.outs??inningsToOuts(s.inningsPitched))||0,bf=Number(s.battersFaced)||0;
 if(!outs&&!bf)return {label:'Awaiting AFL appearance',hot:false};
 const diff=bf>0?100*((s.strikeOuts??0)-(s.baseOnBalls??0))/bf:null;
 if(outs>=6&&diff>=20&&s.era!=null&&s.era!==''&&Number.isFinite(Number(s.era))&&Number(s.era)<=3)return {label:outs<15?'Early bat-missing start · small sample':'Strong AFL pitching',hot:true};
 const era=s.era==null||s.era===''?NaN:Number(s.era);
 if(outs>=6&&((Number.isFinite(era)&&era>5)||(diff!=null&&diff<0)))return {label:outs<15?'Struggling on the mound · small sample':'Struggling on the mound',hot:false};
 return {label:outs<15?'Small sample':'Mixed AFL results',hot:false};
}
export const AFL_CATEGORIES=[
 {id:'all',label:'All players'},
 {id:'strong-hitting',label:'Strong AFL production'},
 {id:'strong-pitching',label:'Strong AFL pitching'},
 {id:'early',label:'Early hot starts'},
 {id:'mixed',label:'Mixed results'},
 {id:'struggling-hitting',label:'Struggling at the plate'},
 {id:'struggling-pitching',label:'Struggling on the mound'},
 {id:'small',label:'Small samples'},
 {id:'awaiting',label:'Awaiting appearance'}
];
export function aflCategory(p,stat){
 const {label}=aflSignal(p,stat);
 if(label==='Strong AFL production')return 'strong-hitting';
 if(label==='Strong AFL pitching')return 'strong-pitching';
 if(label.startsWith('Early '))return 'early';
 if(label.startsWith('Mixed '))return 'mixed';
 if(label.startsWith('Struggling at the plate'))return 'struggling-hitting';
 if(label.startsWith('Struggling on the mound'))return 'struggling-pitching';
 if(label==='Small sample')return 'small';
 return 'awaiting';
}
// Regress hitter OPS toward .700 over 20 PA: reward production with a sample-size cushion.
// Pitchers retain innings priority after clearing the performance screen.
export function featuredAflPlayers(players,stats,limit=3){
 return ['H','P'].flatMap(type=>players.filter(p=>p.type===type&&aflSignal(p,stats[type].get(p.mlbamId)).hot).sort((a,b)=>{
  const sa=stats[type].get(a.mlbamId),sb=stats[type].get(b.mlbamId);
  const sample=s=>type==='H'?Number(s.plateAppearances):Number(s.outs??inningsToOuts(s.inningsPitched));
  const quality=s=>type==='H'?Number(s.ops):(s.strikeOuts-s.baseOnBalls)/s.battersFaced;
  const hitterScore=s=>(Number(s.plateAppearances)*Number(s.ops)+20*.700)/(Number(s.plateAppearances)+20);
  return (type==='H'?hitterScore(sb)-hitterScore(sa):0)||sample(sb)-sample(sa)||quality(sb)-quality(sa)||(type==='P'?Number(sa.era)-Number(sb.era):0)||a.name.localeCompare(b.name)||a.mlbamId-b.mlbamId;
 }).slice(0,limit));
}
export function featuredAflTrackerPlayers(players,stats,cps,limit=3){
 const byId=new Map(players.map(p=>[p.mlbamId,p]));
 const hitters=featuredCpsHitters(cps,limit).map(row=>({
  ...byId.get(row.mlbamId),mlbamId:row.mlbamId,name:row.name,type:'H',cps:row.cps
 }));
 const cpiById=new Map((cps?.pitcherCpi?.pitchers??[]).map(row=>[row.mlbamId,row.cpi]));
 const pitchers=featuredAflPlayers(players.filter(p=>p.type==='P'&&p.status==='Active'),stats,limit).map(p=>({...p,cpi:cpiById.get(p.mlbamId)??null}));
 return [...hitters,...pitchers];
}
export function filterAflPlayers(rows,{query='',team='',type='',played=false,includeInactive=false,category='all'}={},stats){
 const norm=v=>String(v??'').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();const terms=norm(query).split(/\s+/).filter(Boolean);
 return rows.filter(p=>(includeInactive||p.status==='Active')&&(!team||String(p.aflTeamId)===team)&&(!type||p.type===type)&&(!played||hasAflSample(p,stats?.[p.type]?.get(p.mlbamId)))&&(category==='all'||aflCategory(p,stats?.[p.type]?.get(p.mlbamId))===category)&&terms.every(t=>norm([p.name,p.mlbOrg,p.aflTeam,p.owner].join(' ')).includes(t)));
}
const statLine=(p,s)=>!s?'No recorded AFL sample':p.type==='H'?`${s.plateAppearances??0} PA · ${s.avg??'—'}/${s.obp??'—'}/${s.slg??'—'} · ${s.homeRuns??0} HR · ${s.stolenBases??0} SB`:`${s.inningsPitched??'—'} IP · ${s.era??'—'} ERA · ${s.strikeOuts??0} K / ${s.baseOnBalls??0} BB`;
const liveFacts=(p,s,cps)=>{
 if(!s)return '<p>No AFL performance sample is recorded in this feed.</p>';
 const pairs=p.type==='H'?[['PA',s.plateAppearances],['AVG / OBP / SLG',`${s.avg} / ${s.obp} / ${s.slg}`],['HR / SB',`${s.homeRuns} / ${s.stolenBases}`],['K%',pct(s.strikeOuts,s.plateAppearances)],['BB%',pct(s.baseOnBalls,s.plateAppearances)],['OPS',s.ops]]:[['IP',s.inningsPitched],['ERA',s.era],['K / BB',`${s.strikeOuts} / ${s.baseOnBalls}`],['BF',s.battersFaced],['K%',pct(s.strikeOuts,s.battersFaced)],['BB%',pct(s.baseOnBalls,s.battersFaced)]];
 return `<div class="facts metricfacts">${pairs.map(([k,v])=>`<div><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join('')}${aflCpsTile(cps,p)}${aflPitcherCpiTile(cps,p)}</div><p><span class="badge">${esc(aflSignal(p,s).label)}</span></p>${p.type==='P'?pitcherCpiFootnote:aflCpsFootnote}`;
};
export function aflProfileHtml(data,p,draftEntry){
 const review=refinedReport(p);const paragraphs=review?.paragraphs??p.reportParagraphs;const s=p.regularStats;const gradeProfile=FAN_GRAPHS_AFL_GRADES[p.mlbamId]?{...p,scoutingGrades:FAN_GRAPHS_AFL_GRADES[p.mlbamId]}:p;const pairs=!s?[]:p.type==='H'?[['PA',s.plateAppearances],['AVG / OBP / SLG',`${fmt(s.avg)} / ${fmt(s.obp)} / ${fmt(s.slg)}`],['HR / SB',`${s.homeRuns} / ${s.stolenBases}`],['K%',fmt(s.kPercent,1)+'%'],['BB%',fmt(s.bbPercent,1)+'%'],['ISO',fmt(s.iso)]]:[['IP',s.inningsPitched],['ERA',fmt(s.era,2)],['K / BB',`${s.strikeOuts} / ${s.baseOnBalls}`],['BF',s.battersFaced],['K%',fmt(s.kPercent,1)+'%'],['BB%',fmt(s.bbPercent,1)+'%']];
 return `<a href="#afl">← Arizona Fall League</a><div class="player-nameplate-field"><h1>${esc(p.name)}</h1><div class="player-nameplate-meta"><span class="eyebrow">AFL / 2026 PLAYER PROFILE</span><p>${esc(p.position)} · ${esc(p.mlbOrg)} · ${esc(p.aflTeam)}</p></div></div><div class="profile afl-profile"><div><section class="panel"><div class="facts"><div><span>PROFILE STATUS</span><b>${draftEntry?'AFL / FYPD':'AFL ONLY'}</b></div><div><span>MLB ORG</span><b>${esc(p.mlbOrg)}</b></div><div><span>AGE / AFL</span><b>${(()=>{const born=new Date(String(p.bio.birthDate)+'T12:00:00Z'),asOf=new Date(String(data.asOf)+'T12:00:00Z');return Number.isFinite(born.getTime())&&Number.isFinite(asOf.getTime())?((asOf-born)/(365.2425*24*60*60*1000)).toFixed(1):'Unavailable'})()}</b></div><div><span>POSITION</span><b>${esc(p.position)}</b></div><div><span>AFL TEAM</span><b>${esc(p.aflTeam)}</b></div><div><span>FANTASY ORG</span><b>${esc(p.owner)}</b></div></div><h2>Scouting context & dynasty outlook</h2>${paragraphs.map((text,i)=>`${i?`<h3>${esc(review?.sectionTitles?.[i]??(i===1?'Regular-season foundation':text.startsWith('Published tool context')?'Published scouting context':text.startsWith('MLB translation')||text.startsWith('Dynasty outlook')?'Dynasty outlook':text.startsWith('Pipeline performance')?'Process strengths & risks':'Fall evaluation'))}</h3>`:''}<p>${esc(text)}</p>`).join('')}<p class="muted">${esc(review?.context??data.reportContext)} Research cutoff: ${esc(review?.reviewedAsOf??data.asOf)}.</p>${reportSources(review)}${scoutingConfidence(p,'afl')}</section><section class="panel metricssection"><span class="eyebrow">DATED REGULAR SEASON / ${esc(p.regularScope)} 2026</span><h2>Performance evidence</h2><div class="facts metricfacts">${pairs.map(([k,v])=>`<div><span>${k}</span><b>${esc(v)}</b></div>`).join('')}</div>${!s?'<p>No verified regular-season aggregate was returned; missing data is not a zero.</p>':''}<details><summary>Level splits</summary>${p.regularSplits.map(r=>`<p><b>${esc(r.level)}</b> · ${esc(r.team)}<br>${esc(statLine(p,r.stat).replace('AFL','regular-season'))}</p>`).join('')}</details></section><section class="panel metricssection" aria-label="Current AFL performance"><span class="eyebrow">AFL ONLY / OFFICIAL MLB FEED</span><h2>Current AFL performance</h2><p id="afl-live-status" class="muted" role="status"></p><div id="afl-profile-live"></div></section></div><aside class="panel">${prospectGrades(gradeProfile)}<span class="eyebrow">AFL ROSTER / 2026</span><h2>${esc(p.aflTeam)}</h2><p>${esc(p.status)} in the official roster snapshot · ${esc(data.asOf)}</p><h3>BangaLangin organization</h3><p>${esc(p.owner)}</p><p class="muted">Ownership snapshot: October 6. New profiles are outside the November rankings.</p><h3>Player information</h3><p>${esc(p.mlbOrg)} · ${esc(p.position)}<br>Born ${esc(p.bio.birthDate)}<br>${esc(p.bio.height)} · ${esc(p.bio.weight)} lb<br>Bats / throws: ${esc(p.bio.batSide)} / ${esc(p.bio.pitchHand)}</p>${draftEntry?`<p><a href="#draft-player/${esc(draftEntry.id)}"><u>Open FYPD Draft Profile →</u></a></p>`:''}${prospectSavantLink(p)}${pitchIqLink(p)}<section class="afl-card"><h3>Underlying AFL data</h3>${link(pitchUrl,'PitchIQ — AFL board')}<p class="muted">Search ${esc(p.name)} in the AFL view. If PitchIQ opens its home screen, select AFL first.</p>${aflProfileLink(p,data)}</section><details><summary>Profile sources</summary>${p.sources.map(s=>`<p>${link(s.url,s.label)}</p>`).join('')}</details></aside></div>`;
}
let dataPromise,timer,version=0;
if(typeof window!=='undefined')window.addEventListener('hashchange',()=>{clearInterval(timer);version++;});
const nyDate=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'America/Phoenix',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
export async function showAfl(app,page,id){
 clearInterval(timer);const ownVersion=++version,hash=location.hash;app.innerHTML='<p role="status">Loading Arizona Fall League…</p>';
 let data;try{dataPromise??=fetch('data/afl/full-2026.json').then(r=>{if(!r.ok)throw Error('Roster unavailable');return r.json();});data=await dataPromise;}catch{dataPromise=null;if(ownVersion===version)app.innerHTML='<h1>AFL research unavailable</h1><p>Please reload to try again.</p>';return;}
 if(ownVersion!==version||hash!==location.hash)return;
 const cps=await loadAflCps();
 if(ownVersion!==version||hash!==location.hash)return;
 if(page==='afl'&&['cpi','pitcher-oqi'].includes(id)){renderPitcherCpi(app,cps,data.players);return;}
 if(page==='afl'&&(id==='cbs'||id==='cps')){renderAflCps(app,cps,data.players);return;}
 const p=page==='afl-player'?data.players.find(p=>String(p.mlbamId)===id):null;
 if(page==='afl-player'&&!p){app.innerHTML='<h1>AFL player not found</h1><a href="#afl">Return to AFL</a>';return;}
 // An existing prospect identity has one canonical profile.
 if(p?.hasExistingProfile){location.replace(p.route);return;}
 if(p){
  const [,draft]=await Promise.all([loadProfileHistory(),loadAmateurData('draft').catch(()=>null)]);
  if(ownVersion!==version||hash!==location.hash)return;
  const draftEntry=draft?.players.find(entry=>entry.mlbamId===p.mlbamId&&entry.aflProfile);
  if(draftEntry){location.replace('#draft-player/'+encodeURIComponent(draftEntry.id));return;}
  app.innerHTML=aflProfileHtml(data,p);
 }
 else app.innerHTML=`<div class="afl-header-layout"><div class="afl-header-intro"><div class="afl-feature-top"><span class="afl-feature-label">THE FALL FIELD GUIDE</span><span class="afl-feature-season">2026</span></div><span class="eyebrow">RESEARCH TOOLS / FALL BALL</span><h1>Arizona Fall League</h1><p class="afl-feature-deck">Six teams. One proving ground.</p><p class="muted">Regular season + postseason combined · Fall Stars Game excluded.</p><svg class="afl-field-mark" aria-hidden="true" viewBox="0 0 160 125" fill="none"><path d="M80 110 24 54a79 79 0 0 1 112 0Z"/><path d="m80 110-30-30 30-30 30 30Z"/><path d="M80 110V50M24 54l56 56 56-56"/><circle cx="80" cy="84" r="5"/><path d="m80 105-4 4v4h8v-4Z"/></svg><div class="afl-feature-evidence"><p class="muted">2026 · All six teams · ${data.players.filter(p=>p.status==='Active').length} active roster players · ${data.players.length} preserved profiles · Roster checked ${esc(data.asOf)}</p><p id="afl-live-status" class="muted" role="status"></p><button id="afl-refresh" class="afl-refresh-button" type="button">Refresh AFL data</button></div></div><a href="#afl/cbs" class="afl-header-tools" style="display:flex;flex-direction:column;justify-content:center;gap:12px;text-decoration:none;min-height:240px;color:#fff9ed;background:#153831">
<span style="display:flex;align-items:center;justify-content:space-between;gap:12px">
<span class="eyebrow" style="color:#f4dc9f">2026 FALL BALL · HITTING ANALYTICS</span>
<svg aria-hidden="true" viewBox="0 0 40 40" width="36" height="36" style="flex:none" fill="none" stroke="#f4dc9f" stroke-width="1.5"><path d="M20 34 5 19a21 21 0 0 1 30 0ZM20 34 10 24l10-10 10 10Z"/><circle cx="20" cy="24" r="2"/></svg>
</span>
<span style="font-size:clamp(30px,3.5vw,49px);font-weight:800;line-height:1.05">CBS+ Leaderboard</span>
<span style="display:block;background:#20483f;border-left:3px solid #f4dc9f;border-radius:0 7px 7px 0;padding:10px 13px;font-size:1rem;line-height:1.55;color:#fff9ed"><strong>Contextual Batting Score</strong> compares AFL hitters using their production, playing time, team offense, and the pitchers they faced. Two hitters with the same OPS can rank differently if one faced tougher pitching.</span>
<strong style="align-self:flex-start;background:#f4dc9f;color:#153831;padding:9px 13px;border-radius:7px">Explore the leaderboard →</strong></a></div><div class="afl-producing-heading"><h2>Who is producing?</h2><a class="button" href="#afl/cpi">CPI+ Pitchers →</a></div><div id="afl-hot" class="afl-resource-grid"></div><details class="afl-method afl-player-list"><summary>AFL Player Statelines <span id="afl-player-toggle" aria-hidden="true">+</span></summary><div class="controls afl-controls"><input id="afl-search" aria-label="Search AFL players" placeholder="Search players…"><select id="afl-team" aria-label="Filter AFL team"><option value="">All AFL teams</option>${[...new Map(data.players.map(p=>[p.aflTeamId,p.aflTeam])).entries()].map(([i,n])=>`<option value="${i}">${esc(n)}</option>`).join('')}</select><select id="afl-type" aria-label="Filter AFL position"><option value="">Hitters & pitchers</option><option value="H">Hitters</option><option value="P">Pitchers</option></select><select id="afl-category" aria-label="Filter AFL performance category">${AFL_CATEGORIES.map(c=>`<option value="${c.id}">${c.label}</option>`).join('')}</select><select id="afl-sort" aria-label="Sort AFL players"><option value="name">Rank Alphabetically</option><option value="age">Rank By Age</option><option value="performance">Rank By Performance</option></select></div><p id="afl-count" class="muted" aria-live="polite"></p><div id="afl-results-panel" class="tablewrap" role="region" aria-label="Filtered AFL players"><table><thead><tr><th>PLAYER</th><th>AGE</th><th>AFL / MLB TEAM</th><th>BANGALANGIN</th><th>AFL PERFORMANCE</th><th>INDICATOR</th></tr></thead><tbody id="afl-rows"></tbody></table></div></details><p class="muted"><small><strong>CBS+ caveat.</strong> Contextual Batting Score measures current AFL hitting after accounting for team offense, sample size and the actual pitchers faced. It is experimental and does not project MLB performance or grade prospects.</small></p><aside class="afl-header-tools" style="width:100%;box-sizing:border-box;height:auto;max-height:none;margin-top:24px" aria-label="AFL resources and game tracker"><div class="afl-tools-heading"><span class="eyebrow">AFL RESOURCES</span><span class="afl-season-tag">2026 FALL BALL</span></div><div class="afl-tool-links">${link(pitchUrl,'PitchIQ')}${link('https://www.prospect-portfolio.com/afl','ProspectRank')}${link('https://www.mlb.com/arizona-fall-league','MLB AFL')}</div><div class="afl-games-heading"><h2>Game tracker</h2><span class="muted">Arizona game times</span></div><div class="afl-schedule-controls"><button type="button" id="afl-day-prev" aria-label="Previous day">←</button><label for="afl-game-date" class="sr-only">AFL schedule date</label><input type="date" id="afl-game-date" aria-label="AFL schedule date"><button type="button" id="afl-day-next" aria-label="Next day">→</button><button type="button" id="afl-day-today">Today</button><button type="button" id="afl-day-tomorrow">Tomorrow</button></div><p id="afl-schedule-label" class="muted"></p><section id="afl-games" style="max-height:none;overflow:visible" class="afl-resource-grid" aria-label="AFL games for selected date" aria-live="polite"></section></aside><section class="afl-bottom-resources"><div class="notice"><b>Fall performance complements the Pipeline evaluation.</b> Current MLB season counts refresh while you browse. Early games produce tiny samples; these indicators are descriptive, not talent rankings or guarantees.</div><details class="afl-method"><summary>Indicator rules & sample sizes</summary><p>Rank By Performance groups hitters and pitchers separately: hitters by OPS, pitchers by K−BB% (then lower ERA). Samples of at least 20 PA or 5 IP appear before smaller samples; players without recorded performance appear last. Rank By Age sorts youngest first using birth dates.</p><p>Hitters: at least 8 PA and OPS of .900 or higher. Below 20 PA, explicitly labeled an early hot start. Pitchers: at least 2 IP, ERA at or below 3.00 and K−BB% at least 20%. Below 5 IP, explicitly labeled an early bat-missing start. These fixed screening rules are not park-adjusted, age-adjusted, or scouting grades. They compare neither AFL results to regular-season results nor hitters to pitchers. Missing counts produce no positive indicator. Featured hitters are ranked by CBS+ after clearing 35 PA and .850 OPS. Featured pitchers prioritize innings after clearing the pitching performance screen, with K−BB% and ERA breaking ties.</p><p>Roster membership comes from the official full-roster snapshot, not from having statistics. Stats and game status come from the public MLB Stats API. Fetch times indicate when this page checked the feed; the provider may cache or delay updates. The page refreshes every five minutes while open. Sources or connections can fail; saved results then carry a visible snapshot label.</p></details></section>`;
 const cached=loadStatsCache(data.statsSnapshot);
 const playerList=app.querySelector('.afl-player-list');
 if(playerList)playerList.addEventListener('toggle',()=>{
  playerList.querySelector('#afl-player-toggle').textContent=playerList.open?'−':'+';
 });
 let rawStats=cached?.data??data.statsSnapshot,stats=indexAflStats(rawStats),pending=false,live=false,checked=cached?.checked??data.statsRetrievedAt??data.retrievedAt,statsError=null;
 let selectedCategory='all';
 let selectedDate=nyDate(),scheduleError=null,scheduleLoading=true,scheduleRequest=0;
 const schedules=new Map((data.scheduleSnapshot?.dates??[]).map(d=>[d.date,{dates:[d]}]));
 const confirmedDates=new Set();
 const renderGames=()=>{if(p)return;app.querySelector('#afl-game-date').value=selectedDate;app.querySelector('#afl-schedule-label').textContent=new Intl.DateTimeFormat('en-US',{timeZone:'UTC',weekday:'long',month:'long',day:'numeric',year:'numeric'}).format(new Date(`${selectedDate}T12:00:00Z`));app.querySelector('#afl-games').innerHTML=aflGamesHtml(schedules.get(selectedDate),selectedDate,{error:scheduleError,loading:scheduleLoading,saved:schedules.has(selectedDate)&&!confirmedDates.has(selectedDate)});};
 const changeDate=async date=>{
  if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||!Number.isFinite(Date.parse(`${date}T12:00:00Z`)))return;
  selectedDate=date;scheduleError=null;scheduleLoading=true;const request=++scheduleRequest;renderGames();
  const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),15000);
  try{const next=await fetchAflSchedule(date,{signal:controller.signal});if(request!==scheduleRequest||ownVersion!==version||hash!==location.hash)return;schedules.set(date,next);confirmedDates.add(date);}
  catch{if(request===scheduleRequest)scheduleError='MLB schedule unavailable';}
  finally{clearTimeout(timeout);if(request===scheduleRequest&&ownVersion===version&&hash===location.hash){scheduleLoading=false;renderGames();}}
 };
 const render=()=>{
  const label=live?`MLB feed · checked ${new Date(checked).toLocaleString()} · refreshes every 5 minutes`:`Last available data · ${new Date(checked).toLocaleString()} · ${statsError?`live stats refresh unavailable: ${statsError}`:"checking the MLB feed"}`;
  app.querySelector('#afl-live-status').textContent=label;
  if(p){app.querySelector('#afl-profile-live').innerHTML=liveFacts(p,stats[p.type].get(p.mlbamId),cps);return;}
  const search=app.querySelector('#afl-search'),team=app.querySelector('#afl-team'),type=app.querySelector('#afl-type');
  const baseRows=filterAflPlayers(data.players,{query:search.value,team:team.value,type:type.value,includeInactive:false},stats);
  const rows=sortAflPlayers(baseRows.filter(p=>selectedCategory==='all'||aflCategory(p,stats[p.type].get(p.mlbamId))===selectedCategory),stats,app.querySelector('#afl-sort').value);
  const counts=new Map(AFL_CATEGORIES.map(c=>[c.id,0]));counts.set('all',baseRows.length);for(const row of baseRows){const id=aflCategory(row,stats[row.type].get(row.mlbamId));counts.set(id,counts.get(id)+1);}
  const categorySelect=app.querySelector('#afl-category');
  for(const option of categorySelect.options){option.textContent=`${AFL_CATEGORIES.find(c=>c.id===option.value).label} (${counts.get(option.value)})`;}
  categorySelect.value=selectedCategory;
  app.querySelector('#afl-count').textContent=`${rows.length} profiles shown · ${data.players.filter(p=>p.status==='Active').length} active · ${data.players.length} total preserved`;
  app.querySelector('#afl-rows').innerHTML=rows.map(p=>{const s=stats[p.type].get(p.mlbamId),signal=aflSignal(p,s);return `<tr><td><a href="${esc(p.route)}">${esc(p.name)}</a><small>${esc(p.position)}${p.status==='Active'?'':' · '+esc(p.status)}</small></td><td title="Age as of ${esc(data.asOf)}">${aflAge(p.bio?.birthDate,data.asOf)}</td><td>${esc(p.aflTeam)}<small>${esc(p.mlbOrg)}</small></td><td>${esc(p.owner)}</td><td>${esc(statLine(p,s))}</td><td><span class="badge ${signal.hot?'afl-positive':''}">${esc(signal.label)}</span></td></tr>`;}).join('')||'<tr><td colspan="6">No players match these filters.</td></tr>';
  const tops=featuredAflTrackerPlayers(data.players,stats,cps);
  app.querySelector('#afl-hot').innerHTML=(!cps?'<p class="muted">CBS+ unavailable. Featured hitter rankings are temporarily unavailable.</p>':!tops.some(p=>p.type==='H')?'<p class="muted">No hitters meet the CBS+ feature thresholds.</p>':'')+tops.map(p=>`<article class="panel"><span class="eyebrow">${p.type==='H'?'HITTER':'PITCHER'} / AFL</span><h3>${p.route?`<a href="${esc(p.route)}">${esc(p.name)}</a>`:esc(p.name)}</h3><p>${esc(statLine(p,stats[p.type].get(p.mlbamId)))}</p><span class="badge afl-positive">${p.type==='H'?'CBS+ '+p.cps.toFixed(1):'CPI+ '+(Number.isFinite(p.cpi)?p.cpi.toFixed(1):'—')}</span></article>`).join('')||'<p>No players currently meet the published sample and performance rules.</p>';
  renderGames();
 };
 const refresh=async()=>{
  if(pending)return;pending=true;const btn=app.querySelector('#afl-refresh');if(btn){btn.disabled=true;btn.textContent='Checking MLB feed…';}
  const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),15000);
  const requestDate=selectedDate,request=++scheduleRequest;
  try{const update=await fetchAflUpdates(rawStats,requestDate,{signal:controller.signal});if(ownVersion!==version||hash!==location.hash)return;statsError=update.statsError;live=!!update.stats;if(update.stats){rawStats=update.stats;stats=indexAflStats(rawStats);checked=new Date().toISOString();saveStatsCache(rawStats,checked);}if(request===scheduleRequest&&selectedDate===requestDate){scheduleError=update.scheduleError;scheduleLoading=false;if(update.schedule){schedules.set(requestDate,update.schedule);confirmedDates.add(requestDate);}}}
  catch{if(ownVersion!==version||hash!==location.hash)return;live=false;statsError="MLB feed unavailable";}
  finally{clearTimeout(timeout);pending=false;if(ownVersion===version&&hash===location.hash){if(btn){btn.disabled=false;btn.textContent='Refresh AFL data';}render();}}
 };
 const refreshButton=app.querySelector('#afl-refresh');if(refreshButton)refreshButton.onclick=refresh;
 if(!p){
  app.querySelector('#afl-category').onchange=e=>{selectedCategory=e.target.value;render();};
  app.querySelector('#afl-game-date').onchange=e=>changeDate(e.target.value);app.querySelector('#afl-day-prev').onclick=()=>changeDate(shiftAflDate(selectedDate,-1));app.querySelector('#afl-day-next').onclick=()=>changeDate(shiftAflDate(selectedDate,1));app.querySelector('#afl-day-today').onclick=()=>changeDate(nyDate());app.querySelector('#afl-day-tomorrow').onclick=()=>changeDate(shiftAflDate(nyDate(),1));for(const sel of ['#afl-search','#afl-team','#afl-type','#afl-sort'])app.querySelector(sel).addEventListener(sel==='#afl-search'?'input':'change',render);}
 render();refresh();timer=setInterval(()=>{if(document.visibilityState==='visible'&&ownVersion===version&&hash===location.hash)refresh();},300000);
}
