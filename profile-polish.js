// Keep editorial caveats available without interrupting the scouting report.
const keepInPlace='details, table, .facts, .card, .dsl-card, .pro-card, .farmreports, .player-nameplate-field, .development-checkpoint, .player-nameplate-meta, .profile-tabs, [data-door-profile], [role="status"], [aria-live]';
export function polishPage(app){
 organizeProfileSections(app);
 formatSlashLines(app);
 const isProfile=!!app.querySelector('.profile');
 app.classList.toggle('polished-profile',isProfile);
 let notes=app.querySelector(':scope > .page-notes');
 const candidates=[...app.querySelectorAll('p.muted, .checkpoint-footnote, .empty-grade-note')].filter(node=>{
  if(node.closest('.page-notes')||node.id||node.matches('[role], [aria-live]'))return false;
  if(node.matches('.empty-grade-note'))return true;
  if(node.matches('.checkpoint-footnote'))return true;
  if(node.closest('.afl-card')&&!node.closest('.profile aside'))return false;
  return !node.closest(keepInPlace)&&node.textContent.trim();
 });
 if(!candidates.length)return;
 if(!notes){
  notes=document.createElement('section');notes.className='page-notes';notes.setAttribute('aria-label','Page notes and data context');
  notes.innerHTML='<div class="page-notes-heading"><span class="eyebrow">THE DETAILS BEHIND THE DATA</span><h2>Notes & context</h2></div><div class="page-notes-list"></div>';
  app.append(notes);
 }
 const list=notes.querySelector('.page-notes-list');
 for(const node of candidates){
  const parent=node.parentElement;
  const heading=parent.querySelector('h2,h3');
  const item=document.createElement('div');item.className='page-note';
  const label=document.createElement('span');label.className='page-note-label';
  label.textContent=node.matches('.empty-grade-note')?'Scouting grades':node.matches('.checkpoint-footnote')?'Development checkpoints':parent.matches('.external-data')?(parent.querySelector('a')?.textContent.replace('↗','').trim()??'External data'):heading?.textContent??'Publication context';
  item.append(label,node);list.append(item);
 }
 // Async stats and checkpoint renders must never push the notes above the content.
 if(app.lastElementChild!==notes)app.append(notes);
}
export function activateProfilePolish(app){
 let pending=false;
 const observer=new MutationObserver(()=>{if(pending)return;pending=true;queueMicrotask(()=>{pending=false;observer.disconnect();polishPage(app);const notes=app.querySelector(':scope > .page-notes');if(notes&&app.lastElementChild!==notes)app.append(notes);observer.observe(app,{childList:true,subtree:true});});});
 observer.observe(app,{childList:true,subtree:true});polishPage(app);
 return observer;
}

const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function entryHistoryHtml(row){
 if(!row)return '';
 const date=value=>value?new Date(value+'T12:00:00Z').toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric',timeZone:'UTC'}):'';
 const facts=[['Organization',row.team],['Draft year',row.year],['Selection',row.kind==='draft'?(row.round&&row.overallPick?`Round ${row.round} · No. ${row.overallPick} overall`:row.detail):null],['Signed',row.signingDateDisplay??date(row.signingDate)],['School',row.school],['Country',row.country],['Previous league',row.previousLeague],...(['draft','signing','independent'].includes(row.kind)?[[row.bonusStatus?.startsWith('Reported')?'Reported bonus':'Signing bonus',Number.isFinite(row.signingBonusUsd)?new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(row.signingBonusUsd):'Not verified']]:[])].filter(([,value])=>value);
 return `<section class="player-entry" aria-label="Entry into pro baseball"><h3>Entry into pro baseball</h3><span class="entry-method">${escapeHtml(row.method??row.kind)}</span>${facts.length?`<dl class="entry-facts">${facts.map(([label,value])=>`<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join('')}</dl>`:`<p>${escapeHtml(row.summary)}</p>`}${row.detail&&row.kind!=='draft'?`<p class="entry-detail">${escapeHtml(row.detail)}</p>`:''}${row.sources?.length?`<details><summary>Entry record & sources</summary>${[...row.sources,...(row.bonusSource?[row.bonusSource]:[])].map(s=>`<p><a href="${escapeHtml(s.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(s.label)} ↗</a></p>`).join('')}</details>`:''}</section>`;
}
export function formatSlashLines(app){
 const slash=/^(?:0?\.\d{3})\s*\/\s*(?:0?\.\d{3})\s*\/\s*(?:0?\.\d{3})$/;
 for(const node of app.querySelectorAll('.facts b, .draft-stat-grid dd, td')){
  if(!slash.test(node.textContent.trim()))continue;
  node.classList.add('batting-slash-line');
  if(node.parentElement?.parentElement?.classList.contains('facts'))node.parentElement.classList.add('stat-slash-card');
 }
}
export function activateEntryHistory(app){
 let data,pending=false;
 const render=()=>{
  const row=data?.entries?.[location.hash.slice(1).split('/').slice(0,2).join('/')];
  const sidebar=app.querySelector('.profile aside');
  if(!row||!sidebar||sidebar.querySelector('.player-entry')||app.querySelector('h1')?.textContent.trim()!==row.name)return;
  sidebar.insertAdjacentHTML('afterbegin',entryHistoryHtml(row));
 };
 const observer=new MutationObserver(()=>{if(pending)return;pending=true;queueMicrotask(()=>{pending=false;render();});});
 observer.observe(app,{childList:true,subtree:true});
 fetch('data/player-entry-history.json').then(r=>{if(!r.ok)throw Error('Entry history unavailable');return r.json();}).then(d=>{data=d;render();}).catch(()=>{});
 return observer;
}

// Subviews retain the profile identity and sidebar while showing one content page.
export function organizeProfileSections(app){
 const profile=app.querySelector('.profile');if(!profile)return;
 let primary=profile.querySelector(':scope > .profile-primary');
 if(!primary){
  const original=profile.firstElementChild;if(!original)return;
  primary=document.createElement('div');primary.className='profile-primary';original.before(primary);primary.append(original);
 }
 let nav=app.querySelector('.profile-section-nav');
 if(!nav){nav=document.createElement('nav');nav.className='profile-section-nav';nav.setAttribute('aria-label','Player profile sections');nav.setAttribute('role','tablist');nav.dataset.selected='scouting';profile.before(nav);}
 const ensure=(key,label)=>{
  let pane=primary.querySelector(':scope > [data-profile-view="'+key+'"]');
  if(!pane){pane=document.createElement('section');pane.className='profile-view';pane.dataset.profileView=key;pane.id='profile-view-'+key;pane.setAttribute('role','tabpanel');pane.setAttribute('aria-labelledby','profile-tab-'+key);primary.append(pane);}
  if(!nav.querySelector('[data-view="'+key+'"]')){
   const button=document.createElement('button');button.type='button';button.dataset.view=key;button.id='profile-tab-'+key;button.textContent=label;button.setAttribute('role','tab');button.setAttribute('aria-controls',pane.id);
   button.onclick=()=>select(key,true);
   button.onkeydown=event=>{const buttons=[...nav.querySelectorAll('button')];const at=buttons.indexOf(button);let next;if(event.key==='ArrowRight')next=(at+1)%buttons.length;else if(event.key==='ArrowLeft')next=(at+buttons.length-1)%buttons.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=buttons.length-1;else return;event.preventDefault();buttons[next].click();buttons[next].focus();};
   nav.append(button);
  }
  return pane;
 };
 const select=(key,updateUrl=false)=>{
  nav.dataset.selected=key;
  if(updateUrl&&location.hash.startsWith('#october-player/')){const base='#'+location.hash.slice(1).split('/').slice(0,2).join('/');const next=base+(key==='scouting'?'':'/'+key);if(location.hash!==next)window.history.pushState(null,'',next);}
  for(const button of nav.querySelectorAll('button')){const active=button.dataset.view===key;button.setAttribute('aria-selected',String(active));button.tabIndex=active?0:-1;}
  for(const pane of primary.querySelectorAll(':scope > [data-profile-view]'))pane.hidden=pane.dataset.profileView!==key;
 };
 const scouting=ensure('scouting','Scouting & overview');
 const development=ensure('development','Development checkpoint');
 const performance=ensure('performance','Performance evidence');
 const isDraft=location.hash.startsWith('#draft-player/');
 const outcomes=isDraft?ensure('outcomes','Developmental outcomes'):null;
 const history=app.querySelector('[data-profile-history]');
 const historyView=history?ensure('history','Transaction history'):null;
 const door=app.querySelector('[data-door-profile]');
 const doorView=door?ensure('knocking-on-door','Knocking on the Door'):null;
 if(door&&door.parentElement!==doorView)doorView.append(door);
 // Move the specific sections before wrapping the remaining scouting content.
 for(const node of [...app.querySelectorAll('.development-checkpoint')])if(node.parentElement!==development)development.append(node);
 for(const node of [...app.querySelectorAll('.metricssection')])if(!node.closest('aside')&&node.parentElement!==performance)performance.append(node);
 if(outcomes)for(const node of [...app.querySelectorAll('.draft-outcomes')])if(node.parentElement!==outcomes)outcomes.append(node);
 if(history&&history.parentElement!==historyView)historyView.append(history);
 for(const node of [...primary.children])if(!node.matches('[data-profile-view]'))scouting.append(node);
 for(const node of [...app.querySelectorAll(':scope > .amateur-sources')])scouting.append(node);
 for(const [pane,message] of [[development,'A development checkpoint is not yet available for this profile.'],[performance,'Verified performance evidence is not yet available for this profile.']]){
  if(pane.querySelector(':scope > :not(.profile-view-empty)'))pane.querySelector('.profile-view-empty')?.remove();
  else if(!pane.firstElementChild){const empty=document.createElement('p');empty.className='panel profile-view-empty';empty.textContent=message;pane.append(empty);}
 }
 if(!nav.dataset.routeInitialized){
  const requested=location.hash.slice(1).split('/')[2];
  const available=[...nav.querySelectorAll('button')].some(b=>b.dataset.view===requested);
  nav.dataset.selected=available?requested:'scouting';nav.dataset.routeInitialized='true';
  if(requested&&!available)window.history.replaceState(null,'','#'+location.hash.slice(1).split('/').slice(0,2).join('/'));
 }
 select(nav.dataset.selected??'scouting');
}
