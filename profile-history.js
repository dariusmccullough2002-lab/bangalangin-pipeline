const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let pending,history,reports;
export async function loadProfileHistory(){
 pending??=Promise.allSettled(['transactions','profile-reports'].map(n=>fetch(`data/${n}.json`).then(r=>{if(!r.ok)throw Error('Unavailable');return r.json()}))).then(([h,r])=>{history=h.status==='fulfilled'?h.value:null;reports=r.status==='fulfilled'?r.value:null});
 await pending;
}
export const refinedReport=p=>reports?.profiles?.[p.playerId];
function identity(p){if(p.fantraxId)return p.fantraxId;if(p.playerId?.startsWith('fantrax-'))return p.playerId.slice(8);const matches=Object.entries(history?.identities??{}).filter(([,name])=>name.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()===p.name.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase());return matches.length===1?matches[0][0]:null;}
export function acquisitionContext(p){
 const id=identity(p),rows=history?.livePlayers?.[id]?.rows??[];
 if(['Eli Willits','Emil Morales'].includes(p.name)&&rows.some(r=>r[2].includes('Ronald Acuna Jr.'))){const r=rows.find(r=>r[2].includes('Ronald Acuna Jr.'));return `<h3>League acquisition context</h3><p>${esc(p.name)} was included in the March 3, 2026 blockbuster that sent seven players to Shea Stadiums for Ronald Acuña Jr.: Jacob Misiorowski, Munetaka Murakami, Eury Pérez, Kyle Bradish, Luis Robert Jr., Emil Morales and Eli Willits. ${p.name==='Eli Willits'?'Fantrax also records his original selection by How Lowe Can You Go? on February 16, 2026, in Round 1, pick 7. ':''}That package explains his path into this farm; his prospect outlook still rests on his own development and scouting evidence.</p>`;}
 const r=rows.find(r=>/^(Drafted|Claimed|Traded)/.test(r[1])&&(!p.organization||r[1].endsWith(p.organization)));
 return r?`<h3>League acquisition context</h3><p>The latest recorded acquisition${p.organization?` by ${esc(p.organization)}`:''} was ${esc(r[1].toLowerCase())} on ${esc(r[0])}.${r[1].startsWith('Drafted')&&r[2]?` Fantrax records ${esc(r[2])}.`:''} The dated history below preserves earlier moves and any recorded trade package.</p>`:'';
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
