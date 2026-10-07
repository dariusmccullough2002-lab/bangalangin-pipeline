import {resolveDslProfile} from './dsl-profiles.js';
const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const normalizeSearch=value=>String(value??'').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
export function buildProfileIndex(current,archive,players,draft={players:[]},international={players:[]},dsl={players:[]},professionals={players:[]},afl={players:[]}){
 const rows=[],seen=new Set(),currentArchiveIds=new Set();
 for(const p of current.rankings){
  if(p.mlbamId)seen.add(p.mlbamId);
  if(p.archivePlayerId)currentArchiveIds.add(p.archivePlayerId);
  rows.push({name:p.name,route:`#october-player/${p.playerId}`,context:`October · ${p.rankingPosition} · ${p.mlbOrg} · ${p.organization}`});
 }
 for(const p of draft.players){
  if(p.mlbamId&&seen.has(p.mlbamId))continue;
  if(p.mlbamId)seen.add(p.mlbamId);
  rows.push({name:p.name,route:`#draft-player/${p.id}`,context:`2026 draft · ${p.position} · ${p.draftOrganization}`});
 }
 for(const p of international.players)rows.push({name:p.name,route:`#international-player/${p.id}`,context:`2027 international · ${p.position} · Expected ${p.expectedOrganization}`});
 for(const r of archive.rankings.filter(r=>r.organizationId==='shea-stadiums')){
  if(currentArchiveIds.has(r.playerId))continue;
  const p=players.find(p=>p.id===r.playerId);
  if(p)rows.push({name:p.name,route:`#player/${p.id}`,context:`August archive · ${p.position} · ${p.mlbOrg}`});
 }
 for(const p of dsl.players){
  const resolved=resolveDslProfile(p,current);
  if(p.mlbamId)seen.add(p.mlbamId);
  if(resolved.current||rows.some(r=>r.route===resolved.route))continue;
  rows.push({name:p.name,route:resolved.route,context:`2026 DSL · ${p.position} · ${p.organization} · ${resolved.owner}`});
 }
 for(const p of professionals.players){
  if(p.mlbamId&&seen.has(p.mlbamId))continue;
  rows.push({name:p.name,aliases:p.aliases,route:`#international-pro-player/${p.id}`,context:`International professional · ${p.position} · ${p.club} · ${p.status}`});
 }
 for(const p of afl.players){if(seen.has(p.mlbamId)||rows.some(r=>r.route===p.route))continue;seen.add(p.mlbamId);rows.push({name:p.name,route:p.route,context:`2026 AFL · ${p.position} · ${p.mlbOrg} · ${p.owner}`});}
 return rows.sort((a,b)=>a.name.localeCompare(b.name));
}
export function findProfiles(index,query){
 const terms=normalizeSearch(query).split(' ').filter(Boolean);
 if(!terms.length)return [];
 return index.filter(p=>terms.every(t=>normalizeSearch([p.name,...(p.aliases??[])].join(' ')).includes(t))).sort((a,b)=>{
  const q=normalizeSearch(query),an=normalizeSearch(a.name),bn=normalizeSearch(b.name);
  return Number(bn===q)-Number(an===q)||Number(bn.startsWith(q))-Number(an.startsWith(q))||a.name.localeCompare(b.name);
 });
}
let amateurData;
export function activateHomeSearch(container,current,archive,players){
 const form=container.querySelector('#profile-search-form'),input=form?.querySelector('input'),results=container.querySelector('#profile-search-results'),status=container.querySelector('#profile-search-status');
 if(!form||!input||!results||!status)return;
 let index=buildProfileIndex(current,archive,players),loading=true,failed=false;
 const render=()=>{
  const matches=findProfiles(index,input.value);
  results.innerHTML=matches.slice(0,8).map(p=>`<li><a href="${escapeHtml(p.route)}"><span><b>${escapeHtml(p.name)}</b><small>${escapeHtml(p.context)}</small></span><span aria-hidden="true">↗</span></a></li>`).join('');
  results.hidden=!matches.length;
  status.textContent=!normalizeSearch(input.value)?'Search October prospects, draft players, international amateurs, international professionals, 2026 DSL players, AFL players, and available archived profiles.':matches.length?`${matches.length} profile${matches.length===1?'':'s'} found${matches.length>8?' · Showing the first 8; refine your search':''}.`:loading?'Searching profiles…':failed?'No matches in the available profiles. Draft and international search is temporarily unavailable.':'No profiles found. Try a different name.';
 };
 input.addEventListener('input',render);
 input.addEventListener('keydown',event=>{
  if(event.key==='ArrowDown'&&results.querySelector('a')){event.preventDefault();results.querySelector('a').focus();}
  if(event.key==='Escape'){input.value='';render();}
 });
 results.addEventListener('click',event=>{if(event.target.closest('a')){results.hidden=true;input.value='';}});
 window.addEventListener('hashchange',()=>{results.hidden=true;input.value='';});
 form.addEventListener('submit',event=>{event.preventDefault();const first=results.querySelector('a');if(first)first.click();});
 render();
 amateurData??=Promise.all(['draft/2026.json','international/2027.json','dsl/2026.json','international/professionals-2026.json','afl/full-2026.json'].map(async path=>{const response=await fetch(`data/${path}`);if(!response.ok)throw Error('Search data unavailable');return response.json();}));
 amateurData.then(([draft,international,dsl,professionals,afl])=>{if(!form.isConnected)return;loading=false;index=buildProfileIndex(current,archive,players,draft,international,dsl,professionals,afl);render();}).catch(()=>{amateurData=undefined;if(!form.isConnected)return;loading=false;failed=true;render();});
}
