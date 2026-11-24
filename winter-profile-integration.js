import {renderWinterProfile,winterPerformanceEvidence,winterProfileContext} from './winter-profiles.js';
import {entryHistoryHtml} from './profile-polish.js';
import {organizeProfileSections} from './profile-polish.js';
const norm=x=>String(x??'').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase().replace(/[^a-z0-9]/g,'');
const routeKey=hash=>hash.split('/').slice(0,2).join('/');
export function winterRouteIndex(catalog,winter,archive){
 const index=new Map(),byId=new Map(catalog.players.map(p=>[p.mlbamId,p]));
 for(const p of catalog.players){index.set(p.profileUrl,p);index.set('#winter-player/'+p.mlbamId,p);}
 for(const l of winter.leagues)for(const group of ['hitters','pitchers'])for(const row of l[group])if(row.profileUrl&&!index.has(row.profileUrl))index.set(row.profileUrl,byId.get(row.mlbamId)??{mlbamId:row.mlbamId,name:row.name});
 for(const a of archive){const matches=catalog.players.filter(p=>norm(p.name)===norm(a.name)&&p.mlbOrg===a.mlbOrg&&(!a.mlbamId||a.mlbamId===p.mlbamId));if(matches.length===1)index.set('#player/'+a.id,matches[0]);}
 return index;
}
export function activateWinterProfileCoverage(app){
 let data,pending=false;
 const render=()=>{
  const route=routeKey(location.hash),p=data?.index.get(route),profile=app.querySelector('.profile');
  if(!p||!profile||profile.dataset.winterCoverage||norm(app.querySelector('h1')?.textContent)!==norm(p.name))return;
  const records=winterProfileContext(p,data.winter);if(!records.length)return;
  profile.dataset.winterCoverage='true';
  if(route.startsWith('#player/')&&p.seasonStats){
   const archiveFacts=profile.querySelector('.facts')?.outerHTML??'',history=app.querySelector('[data-profile-history]')?.outerHTML??'';
   app.innerHTML=renderWinterProfile(p,data.winter)+history;
   const replacement=app.querySelector('.profile');replacement.dataset.winterCoverage='true';
   if(archiveFacts)replacement.firstElementChild.insertAdjacentHTML('beforeend',`<details><summary>August 2026 ranking snapshot</summary>${archiveFacts}</details>`);
  }else if(!route.startsWith('#winter-player/')){
   const section=document.createElement('div');section.innerHTML=winterPerformanceEvidence(records,true,data.winter.seasonLabel);
   section.firstElementChild.dataset.winterEvidence=String(p.mlbamId);
   // The shared section organizer moves this into Performance evidence and keeps the selected tab.
   app.append(section.firstElementChild);
  }
  const sidebar=app.querySelector('.profile aside');
  if(sidebar&&p.proEntry&&!sidebar.querySelector('.player-entry'))sidebar.insertAdjacentHTML('afterbegin',entryHistoryHtml(p.proEntry));
  organizeProfileSections(app);
 };
 const observer=new MutationObserver(()=>{if(pending)return;pending=true;queueMicrotask(()=>{pending=false;render();});});
 observer.observe(app,{childList:true,subtree:true});
 Promise.all(['winter/profiles-2026.json','winter/2026.json','players.json'].map(async path=>{const r=await fetch('data/'+path);if(!r.ok)throw Error('Winter profile coverage unavailable');return r.json();})).then(([catalog,winter,archive])=>{data={winter,index:winterRouteIndex(catalog,winter,archive)};render();}).catch(()=>{});
 return observer;
}
