const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function checkpointHtml(p){
 if(!p)return '';
 return `<section class="panel development-checkpoint" aria-label="Development checkpoint"><span class="eyebrow">WHAT TO WATCH NEXT</span><h2>Development checkpoint</h2><p><b>${esc(p.topic)}</b> · ${esc(p.status)}</p><h3>Main question</h3><p>${esc(p.question)}</p>${p.evidence?`<details><summary>Player-specific basis · evidence dated ${esc(p.evidenceDate??'unknown')}</summary><blockquote>${esc(p.evidence)}</blockquote><p class="muted">Excerpt from this player’s saved profile. Source dates and statistical samples retain their original limits.</p></details>`:'<p class="muted">The saved profile does not contain enough substantive evidence to assign a specific development weakness.</p>'}<h3>Positive signal</h3><p>${esc(p.positive)}</p><h3>Concern signal</h3><p>${esc(p.concern)}</p><h3>Next evaluation window</h3><p>${esc(p.window)}</p><p class="muted">Monitoring plan prepared October 22, 2026 from existing profile evidence. These are editorial follow-up questions, not measured improvements, new tool grades or automatic ranking changes. Workout clips alone do not establish progress.</p><details><summary>Evidence references (${p.sources.length})</summary>${p.sources.map(s=>`<p><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.label??'Profile reference')} ↗</a>${s.sourceDate?` · published ${esc(s.sourceDate)}`:''}${s.retrievedDate?` · retrieved ${esc(s.retrievedDate)}`:''}</p>`).join('')||'<p>No direct source link is stored for this checkpoint. Source verification remains pending.</p>'}</details></section>`;
}
export function activateCheckpoints(app){
 let data;
 const render=()=>{const route=location.hash.slice(1);const p=data?.entries?.[route];const container=app.querySelector('.profile');if(!container||!p||app.querySelector('.development-checkpoint'))return;
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
