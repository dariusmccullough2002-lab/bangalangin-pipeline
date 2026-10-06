const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let pending,history,reports;
export async function loadProfileHistory(){
 pending??=Promise.allSettled(['transactions','profile-reports'].map(n=>fetch(`data/${n}.json`).then(r=>{if(!r.ok)throw Error('Unavailable');return r.json()}))).then(([h,r])=>{history=h.status==='fulfilled'?h.value:null;reports=r.status==='fulfilled'?r.value:null});
 await pending;
}
export const refinedReport=p=>reports?.profiles?.[p.playerId];
function identity(p){if(p.fantraxId)return p.fantraxId;if(p.playerId?.startsWith('fantrax-'))return p.playerId.slice(8);const matches=Object.entries(history?.identities??{}).filter(([,name])=>name.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()===p.name.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase());return matches.length===1?matches[0][0]:null;}
const humanDate=d=>new Date(d+'T12:00:00Z').toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric',timeZone:'UTC'});
const list=items=>items.length<2?items.join(''):items.slice(0,-1).join(', ')+' and '+items.at(-1);
function tradeSentence(name,date,assets){
 const sides=[...new Set(assets.map(a=>a.from))];
 return `${name} was traded on ${date}. ${sides.map(team=>`${team} sent ${list(assets.filter(a=>a.from===team).map(a=>a.name))} to ${assets.find(a=>a.from===team)?.to}`).join('; ')}.`;
}
export function acquisitionContext(p){
 const id=identity(p),live=history?.livePlayers?.[id],events=history?.players?.[id]??[];
 const sentences=[];
 if(p.name==='Leo De Vries'&&events.filter(e=>e.type==='trade'&&e.date==='2026-07-27').length===2){sentences.push('Leo De Vries was flipped twice on July 27, 2026: the supplied export timestamps place his move from Yoho and a Bottle of Rum to How Lowe Can You Go? at 3:04 PM EDT, followed by his move to Shea Stadiums at 3:12 PM EDT—just eight minutes later.');}
 if(live){
  for(const r of [...live.rows].reverse()){
   const [date,action,details]=r;
   if(action.startsWith('Traded')){
    const lines=details.split('\n').map(x=>x.trim()).filter(Boolean),sides=[];let side;
    for(const line of lines){if(line.endsWith(' trades away')){side={team:line.slice(0,-12),assets:[]};sides.push(side);}else if(side)side.assets.push(line);}
    if(sides.length===2){sentences.push(`${p.name} was traded to ${action.slice(10)} on ${date}. ${sides.map(a=>`${a.team} sent ${list(a.assets)} to ${sides.find(b=>b!==a).team}`).join('; ')}.`);}else sentences.push(`${p.name} was ${action.toLowerCase()} on ${date}.`);
   }else if(action.startsWith('Drafted'))sentences.push(`${p.name} was drafted by ${action.slice(11)} on ${date}${details?`, ${details.charAt(0).toLowerCase()+details.slice(1)}`:''}.`);
   else if(action.startsWith('Claimed')){const type=action.includes('(WW)')?'off waivers':'as a free agent';const team=action.split(' by ').slice(1).join(' by ');sentences.push(`${p.name} was claimed by ${team} on ${date} ${type}.${details?` The transaction also records: ${details}.`:''}`);}
   else if(action.startsWith('Dropped'))sentences.push(`${p.name} was dropped by ${action.slice(11)} on ${date}.${details?` The corresponding move was: ${details}.`:''}`);
  }
  const keepers=live.rows.filter(r=>r[1].startsWith('Kept'));
  if(keepers.length)sentences.push(`Recorded keeper decisions: ${keepers.slice().reverse().map(r=>`${r[1].slice(8)} on ${r[0]}`).join('; ')}.`);
 }else{
  for(const e of [...events].sort((a,b)=>a.date.localeCompare(b.date)||(history.trades.find(t=>t.id===a.tradeId)?.occurredAt??'').localeCompare(history.trades.find(t=>t.id===b.tradeId)?.occurredAt??''))){
   const trade=history.trades.find(t=>t.id===e.tradeId);
   if(trade)sentences.push(tradeSentence(p.name,humanDate(e.date),trade.assets));
   else if(e.type.startsWith('claim'))sentences.push(`${p.name} was claimed by ${e.team} on ${humanDate(e.date)}${e.type==='claim-waivers'?' off waivers':' as a free agent'}.`);
   else if(e.type==='drop')sentences.push(`${p.name} was dropped by ${e.team} on ${humanDate(e.date)}.`);
  }
 }
 if(!sentences.length)sentences.push(`${p.name}'s verified fantasy acquisition history is not available in the captured records. No draft position, claim date or trade is asserted until it can be sourced.`);
 if(!live&&events.length)sentences.push('This supplied history is partial; an original draft selection or earlier claims may be missing.');
 return `<h3>League transaction story</h3>${sentences.map(t=>`<p>${esc(t)}</p>`).join('')}`;
}
export function transactionHistory(p){
 const id=identity(p),live=history?.livePlayers?.[id],events=history?.players?.[id]??[];
 const table=rows=>`<div class="tablewrap"><table><thead><tr><th>DATE</th><th>ACTION</th><th>DETAILS</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(r[0])}</td><td>${esc(r[1])}</td><td>${esc(r[2]).replaceAll('\n','<br>')}</td></tr>`).join('')}</tbody></table></div>`;
 const fallback=events.map(e=>{const trade=history.trades.find(t=>t.id===e.tradeId);return [e.date,e.type==='trade'?`Traded from ${e.from} to ${e.to}`:e.action??`${e.type} · ${e.team??e.to??''}`,trade?trade.assets.map(a=>`${a.name}: ${a.from} → ${a.to}`).join('\n'):e.details??''];});
 return `<section class="panel" data-profile-history><h2>Fantasy transaction history</h2><details open><summary>Full recorded history</summary><p class="muted">${!history?'History is temporarily unavailable.':live?'Fantrax Trans (Fntsy) tab captured October 6, 2026. All rows returned by the tab are shown, newest first; earlier unrecorded activity cannot be established.':events.length?'Partial history from the supplied trade export and screenshot. Drafts, claims and other moves may be missing.':'A complete Fantrax history has not yet been captured for this player. This does not mean the player has never been drafted, claimed or traded.'}</p>${live?table(live.rows):fallback.length?table(fallback):''}<p class="muted">Historical team names are preserved. Current ownership comes from the latest roster export. Same-day records follow Fantrax’s displayed order; exact times are not supplied.</p></details></section>`;
}
export function activateProfileTabs(app){
 const historyPane=app.querySelector('[data-profile-history]'),overview=app.querySelector('.profile');if(!historyPane||!overview)return;
 const nav=document.createElement('nav');nav.className='editionnav';nav.setAttribute('aria-label','Player profile sections');nav.setAttribute('role','tablist');
 const panels=[overview,...app.querySelectorAll('.metricssection,.amateur-sources')];
 for(const [label,isHistory] of [['Scouting & overview',false],['Transaction history',true]]){const button=document.createElement('button');button.type='button';button.className='button';button.textContent=label;button.setAttribute('role','tab');button.setAttribute('aria-selected',String(!isHistory));button.onclick=()=>{historyPane.hidden=!isHistory;for(const pane of panels){pane.hidden=isHistory;pane.style.display=isHistory?'none':'';}for(const b of nav.children)b.setAttribute('aria-selected',String(b===button));};nav.append(button);}
 overview.before(nav);historyPane.hidden=true;
}
