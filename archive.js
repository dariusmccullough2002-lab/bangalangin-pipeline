export const archiveTabs=[{id:'august',label:'August Archive',legacy:'organizations'},{id:'approach',label:'Our Approach',legacy:'methodology'},{id:'rosters',label:'Current Rosters',legacy:'rosters'},{id:'farms',label:'Farm Systems',legacy:'october-farms'}];
export function archiveTabForRoute(page,id){return page==='archive'?(archiveTabs.find(t=>t.id===id)?.id??'august'):archiveTabs.find(t=>t.legacy===page)?.id??null;}
export function archiveShell(){return `<section class="archive-page" aria-labelledby="archive-title"><div class="archive-heading"><span class="eyebrow">THE PIPELINE REFERENCE DESK</span><h1 id="archive-title">Archive</h1><p>Explore historical rankings, roster information, farm system evaluations, and the methodology behind BangaLangin Pipeline.</p></div><nav class="archive-tabs" role="tablist" aria-label="Archive sections">${archiveTabs.map(t=>`<a href="#archive/${t.id}" id="archive-tab-${t.id}" role="tab" aria-controls="archive-panel-${t.id}" aria-selected="false" tabindex="-1">${t.label}</a>`).join('')}</nav>${archiveTabs.map(t=>`<section id="archive-panel-${t.id}" class="archive-content" role="tabpanel" aria-labelledby="archive-tab-${t.id}" tabindex="0" hidden></section>`).join('')}</section>`;}
const instances=new WeakMap();
export function showArchive(app,selected,renderers){
 let state=instances.get(app);
 if(!state||!app.contains(state.shell)){
  app.innerHTML=archiveShell();state={shell:app.querySelector('.archive-page'),loaded:new Set(),loading:new Set()};instances.set(app,state);
  const links=[...state.shell.querySelectorAll('[role="tab"]')];
  links.forEach((link,i)=>link.addEventListener('keydown',event=>{let next;if(event.key==='ArrowRight')next=(i+1)%links.length;else if(event.key==='ArrowLeft')next=(i+links.length-1)%links.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=links.length-1;else return;event.preventDefault();links[next].focus();links[next].click();links[next].scrollIntoView?.({block:'nearest',inline:'nearest'});}));
 }
 selected=archiveTabs.some(t=>t.id===selected)?selected:'august';
 for(const t of archiveTabs){const active=t.id===selected,tab=state.shell.querySelector('#archive-tab-'+t.id),panel=state.shell.querySelector('#archive-panel-'+t.id);tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;panel.hidden=!active;}
 if(state.loaded.has(selected)||state.loading.has(selected))return;
 const panel=state.shell.querySelector('#archive-panel-'+selected);state.loading.add(selected);panel.setAttribute('aria-busy','true');panel.innerHTML='<p role="status">Loading this Archive section…</p>';
 const isCurrent=()=>app.contains(state.shell)&&state.shell.contains(panel);
 const finish=()=>{if(!isCurrent())return;for(const heading of panel.querySelectorAll('h1')){const h=document.createElement('h2');for(const attribute of heading.attributes)h.setAttribute(attribute.name,attribute.value);h.classList.add('archive-section-title');h.replaceChildren(...heading.childNodes);heading.replaceWith(h);}state.loaded.add(selected);};
 Promise.resolve().then(()=>{if(isCurrent())return renderers[selected](panel,{isCurrent});}).then(finish).catch(()=>{if(isCurrent()){panel.innerHTML='<p role="alert">This section could not be loaded. Reload to retry.</p>';}}).finally(()=>{state.loading.delete(selected);panel.removeAttribute('aria-busy');});
}
