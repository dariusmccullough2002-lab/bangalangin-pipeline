import {activateHomeSearch} from '/home-search.js';
// Header behavior only; the verified analyzer script and storage stay independent.
const menus=[...document.querySelectorAll('header nav details')];
for(const menu of menus){
 menu.addEventListener('toggle',()=>{if(menu.open)for(const other of menus)if(other!==menu)other.open=false;});
 menu.addEventListener('click',event=>{if(event.target.closest('a'))menu.open=false;});
}
document.addEventListener('click',event=>{for(const menu of menus)if(!menu.contains(event.target))menu.open=false;});
document.addEventListener('keydown',event=>{if(event.key==='Escape')for(const menu of menus)if(menu.open){menu.open=false;menu.querySelector('summary').focus();}});
try{
 const [current,archive,players]=await Promise.all(['/data/editions/october-2026.json','/data/editions/august-2026.json','/data/players.json'].map(async path=>{const response=await fetch(path);if(!response.ok)throw Error('Profile search unavailable');return response.json();}));
 activateHomeSearch(document,current,archive,players,'/');
}catch{
 const form=document.querySelector('#profile-search-form');
 form.addEventListener('submit',event=>{event.preventDefault();location.assign('/#home');});
 document.querySelector('#profile-search-status').textContent='Profile search is temporarily unavailable. Open Home to search the Pipeline.';
}
