// Keep editorial caveats available without interrupting the scouting report.
const keepInPlace='details, table, .facts, .card, .dsl-card, .pro-card, .farmreports, .player-nameplate-field, .development-checkpoint, .player-nameplate-meta, .profile-tabs, [role="status"], [aria-live]';
export function polishPage(app){
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
 return `<section class="player-entry" aria-label="Entry into pro baseball"><span class="eyebrow">ORIGIN STORY</span><h3>Entry into pro baseball</h3><p>${escapeHtml(row.summary)}</p>${row.detail?`<p class="entry-detail">${escapeHtml(row.detail)}</p>`:''}${row.sources?.length?`<details><summary>Entry record & sources</summary>${row.sources.map(s=>`<p><a href="${escapeHtml(s.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(s.label)} ↗</a></p>`).join('')}</details>`:''}</section>`;
}
export function activateEntryHistory(app){
 let data,pending=false;
 const render=()=>{
  const row=data?.entries?.[location.hash.slice(1)];
  const sidebar=app.querySelector('.profile aside');
  if(!row||!sidebar||sidebar.querySelector('.player-entry')||app.querySelector('h1')?.textContent.trim()!==row.name)return;
  sidebar.insertAdjacentHTML('afterbegin',entryHistoryHtml(row));
 };
 const observer=new MutationObserver(()=>{if(pending)return;pending=true;queueMicrotask(()=>{pending=false;render();});});
 observer.observe(app,{childList:true,subtree:true});
 fetch('data/player-entry-history.json').then(r=>{if(!r.ok)throw Error('Entry history unavailable');return r.json();}).then(d=>{data=d;render();}).catch(()=>{});
 return observer;
}
