import {activateHeaderNavigation} from '/header-navigation.js';
activateHeaderNavigation(document);
import {tradeNarrative} from './trade-narrative.js';
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

const etaEvidence=await fetch('/data/research/eta-evidence.json').then(r=>r.ok?r.json():{}).catch(()=>({}));
// Reformat only the displayed summaries. Every score and conclusion comes from
// the verified analyzer's existing DOM output; no catalog or model is accessed.
const textNode=(tag,className,text)=>{const node=document.createElement(tag);node.className=className;node.textContent=text;return node;};
const conciseVerdict=text=>{
 if(text.startsWith('Uncertain:')){const base=text.match(/Base estimate is (?:a |an )?(gain|loss|even)/)?.[1];return 'Uncertain'+(base?' · base estimate: '+base:'');}
 if(text.startsWith('Modeled gain'))return 'Modeled gain across tested assumptions';
 if(text.startsWith('Modeled loss'))return 'Modeled loss across tested assumptions';
 return text;
};
const originalOutcomes=[...document.querySelectorAll('.outcomes > div')];
const summaryCards=originalOutcomes.map((container,side)=>{
 const readable=textNode('div','readable-summary','');
 const evidence=document.createElement('details');evidence.className='summary-evidence';
 evidence.append(textNode('summary','','Detailed explanation'));
 for(const node of [...container.childNodes])evidence.append(node);
 container.append(readable,evidence);return readable;
});
let lastSummary='';
const renderReadableSummaries=()=>{
 const inputs=[0,1].map(side=>({
  owner:document.getElementById('ownerlabel'+side).textContent,
  net:document.getElementById('net'+side).textContent,
  range:document.getElementById('range'+side).textContent,
  assessment:document.getElementById('assessment'+side).textContent,
  why:document.getElementById('why'+side).textContent,
  sent:[...document.querySelectorAll('#assets'+side+' .name')].map(node=>node.textContent),
  received:[...document.querySelectorAll('#assets'+(1-side)+' .name')].map(node=>node.textContent)
 }));
 const signature=JSON.stringify(inputs);if(signature===lastSummary)return;lastSummary=signature;
 inputs.forEach((value,side)=>{
  const card=summaryCards[side];card.replaceChildren(textNode('p','eyebrow',value.owner));
  const score=value.net.match(/^([+-]?[\d.]+) competitive-fit change$/);
  if(!score){card.append(textNode('h3','summary-empty',value.net));card.parentElement.querySelector('details').hidden=true;return;}
  card.parentElement.querySelector('details').hidden=false;
  const metric=textNode('div','summary-score','');metric.append(textNode('strong','',score[1]),textNode('span','','Strategy fit change'));card.append(metric);
  const packages=textNode('div','summary-packages','');
  for(const [label,names] of [['Receives',value.received],['Sends',value.sent]]){
   const column=textNode('div','summary-package','');column.append(textNode('h4','',label));
   const list=document.createElement('ul');for(const name of names)list.append(textNode('li','',name));column.append(list);packages.append(column);
  }card.append(packages);
  const conclusions=value.assessment.match(/^Neutral asset balance: (.*?) Competitive fit: (.*?) Market acquisition price unestimated;/);
  if(conclusions){
   const rows=textNode('dl','summary-verdicts','');
   for(const [label,result] of [['Neutral value',conclusions[1]]]){const row=document.createElement('div');row.append(textNode('dt','',label),textNode('dd','',conciseVerdict(result)));rows.append(row);}card.append(rows);
  }
  // Read the original selected IDs; never infer identity from a display name.
  if(typeof state!=='undefined'&&typeof DATA!=='undefined'){
   const assets=new Map(DATA.assets.map(a=>[a.id,a]));
   const bounds=value.range.match(/^Scenario envelope (-?[\d.]+) to (-?[\d.]+)/);
   const near=value.why.match(/first-three-year contribution changes (-?[\d.]+)/);
   const narrative=tradeNarrative({owner:document.getElementById('org'+side).selectedOptions[0].textContent,strategy:state.modes[side],incoming:state.sides[1-side].map(id=>assets.get(id)),outgoing:state.sides[side].map(id=>assets.get(id)),fit:Number(score[1]),range:bounds?{low:Number(bounds[1]),high:Number(bounds[2])}:null,assessment:value.assessment,otherFit:Number(inputs[1-side].net.match(/^([+-]?[\d.]+)/)?.[1]),otherStrategy:state.modes[1-side],nearChange:near?Number(near[1]):null,etas:etaEvidence});
   card.append(textNode('p','trade-narrative',narrative));
  }
  const range=value.range.match(/^Scenario envelope (.*?) ·/);if(range)card.append(textNode('p','summary-range','Tested strategy range: '+range[1]));
  const caution=value.why.match(/Evidence caution: (\d+) assets/);if(caution)card.append(textNode('p','summary-caution',caution[1]+' assets depend on development, draft assumptions, or limited MLB history. See player breakdowns.'));
 });
};
for(const id of ['ownerlabel0','ownerlabel1','net0','net1','range0','range1','assessment0','assessment1','why0','why1','assets0','assets1']){
 new MutationObserver(renderReadableSummaries).observe(document.getElementById(id),{childList:true,subtree:true,characterData:true});
}
renderReadableSummaries();
