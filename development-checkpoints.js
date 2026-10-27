const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function checkpointHtml(p){
 if(!p)return '';
 const rows=[
 ['Main question',p.question,'question'],
 ['Starting point',p.baseline??'A verified performance baseline is not yet available.','baseline'],
 ['Positive signal',p.positive,'positive'],
 ['Concern signal',p.concern,'concern'],
 ['Next evaluation',p.window,'window']
 ];
 return `<section class="panel development-checkpoint" aria-label="Development checkpoint"><div class="checkpoint-heading"><span class="eyebrow">WHAT TO WATCH NEXT</span><h2>Development checkpoint</h2><p class="checkpoint-topic">${esc(p.topic)}</p><span class="checkpoint-status">${esc(p.status)}</span></div><div class="checkpoint-table-wrap"><table class="checkpoint-table"><caption class="sr-only">Development monitoring plan for ${esc(p.name??'this prospect')}</caption><tbody>${rows.map(([label,value,tone])=>`<tr class="checkpoint-row-${tone}"><th scope="row"><span class="checkpoint-row-label"><i aria-hidden="true"></i>${label}</span></th><td>${esc(value)}</td></tr>`).join('')}</tbody></table></div><div class="checkpoint-evidence">${p.evidence?`<details><summary>Research basis <span>Reviewed ${esc(p.reviewedAsOf??p.evidenceDate??'date unavailable')}</span></summary><blockquote>${esc(p.evidence)}</blockquote><p class="muted">Published report years, original source dates and statistical samples remain distinct from the review date.</p></details>`:'<p class="muted">The saved profile does not contain enough substantive evidence to assign a specific development weakness.</p>'}<details><summary>Sources & references <span>${p.sources.length} references</span></summary>${p.sources.map(s=>`<p><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.label??'Profile reference')} ↗</a>${s.sourceDate?` · published ${esc(s.sourceDate)}`:''}${s.retrievedDate?` · retrieved ${esc(s.retrievedDate)}`:''}</p>`).join('')||'<p>No direct source link is stored for this checkpoint. Source verification remains pending.</p>'}</details></div><p class="checkpoint-footnote">Individually reviewed October 22, 2026 · Development signals are tests to observe, not progress already achieved or automatic ranking changes. No arbitrary statistical pass marks are assigned. Workout clips alone do not establish progress.</p></section>`;
}
export function activateCheckpoints(app){
 let data;
 const render=()=>{const route=location.hash.slice(1).split('/').slice(0,2).join('/');const p=data?.entries?.[route];const container=app.querySelector('.profile');if(!container||!p||app.querySelector('.development-checkpoint'))return;
 // Only attach once the asynchronous profile renderer has produced the matching name.
 if(app.querySelector('h1')?.textContent.trim()!==p.name)return;
 const target=container.firstElementChild;
 target.insertAdjacentHTML('beforeend',checkpointHtml(p));
 };
 const observer=new MutationObserver(render);observer.observe(app,{childList:true,subtree:true});
 fetch('data/development-checkpoints.json').then(r=>{if(!r.ok)throw Error('Checkpoint data unavailable');return r.json();}).then(d=>{data=d;render();}).catch(()=>{});
 window.addEventListener('hashchange',render);
 return ()=>{observer.disconnect();window.removeEventListener('hashchange',render);};
}
