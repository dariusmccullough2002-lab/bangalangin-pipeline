import {packageReview,renderReview} from './valuation-review.js';
import {seasonOutlook} from './contribution-horizon.js';
import {activateHeaderNavigation} from '/header-navigation.js';
activateHeaderNavigation(document);
import {explainTrade,renderExplanation,renderPlainSummary} from './trade-explanation.js';
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

// Explain the active ledger through its own value function; never rescore assets.
const textNode=(tag,className,text)=>{const node=document.createElement(tag);node.className=className;node.textContent=text;return node;};
// The packed analyzer initializes asynchronously; do not observe missing asset nodes.
await new Promise(resolve=>{if(document.body.dataset.ready==='true'){resolve();return;}const observer=new MutationObserver(()=>{if(document.body.dataset.ready==='true'){observer.disconnect();resolve();}});observer.observe(document.body,{attributes:true,attributeFilter:['data-ready']});});
const outcomes=document.querySelector('.outcomes');
const originalOutcomes=[...outcomes.children];
const analysis=textNode('section','trade-analysis','');analysis.setAttribute('aria-label','Trade analysis');
const heading=textNode('div','trade-analysis-heading','');heading.append(textNode('p','eyebrow','TRADE ANALYSIS'),textNode('h2','','Two strategies. One exchange.'));
const scores=textNode('div','trade-analysis-scores','');
const neutral=document.getElementById('neutralnet').closest('section');neutral.classList.add('trade-analysis-neutral');
const reasoning=textNode('div','trade-reasoning','');reasoning.setAttribute('aria-live','polite');
const technical=document.createElement('details');technical.className='trade-full-details';technical.append(textNode('summary','','For more details'));
const calculations=textNode('div','trade-calculations','');
const original=document.createElement('details');original.className='trade-original-evidence';original.append(textNode('summary','','Additional ledger diagnostics'));for(const node of originalOutcomes)original.append(node);
technical.append(neutral,calculations,original);const priceReview=textNode('div','trade-price-review-container','');analysis.append(heading,priceReview,scores,reasoning,technical);outcomes.replaceWith(analysis);
let lastSummary='';
let latestExplanation=null;
window.PipelineTradeExplanation={export:()=>latestExplanation};
const renderReadableSummaries=()=>{
 if(typeof state==='undefined'||typeof DATA==='undefined')return;
 const inputs=[0,1].map(side=>({owner:document.getElementById('ownerlabel'+side).textContent,net:document.getElementById('net'+side).textContent,range:document.getElementById('range'+side).textContent}));
 const signature=JSON.stringify([inputs,state]);if(signature===lastSummary)return;lastSummary=signature;
 scores.replaceChildren();reasoning.replaceChildren();calculations.replaceChildren();technical.hidden=true;latestExplanation=null;
 const assets=new Map(DATA.assets.map(a=>[a.id,a]));const explanations=[];const coverageReport=window.PipelineValuationReview?packageReview(DATA,state,window.PipelineValuationReview):null;priceReview.replaceChildren();if(coverageReport)priceReview.append(renderReview(document,coverageReport));
 for(let side=0;side<2;side++){
  const owner=document.getElementById('org'+side).selectedOptions[0].textContent;
  const card=textNode('div','trade-strategy-card','');card.append(textNode('p','eyebrow',inputs[side].owner));
  const match=inputs[side].net.match(/^([+-]?[\d.]+) strategy-value change$/);
  if(!match){card.append(textNode('p','summary-empty',inputs[side].net));scores.append(card);if(state.sides.every(ids=>ids.length)&&state.teams[0]!==state.teams[1]){const blocked=explainTrade({incoming:state.sides[1-side].map(id=>assets.get(id)),outgoing:state.sides[side].map(id=>assets.get(id)),mode:state.modes[side],valueFor:(id,mode)=>val(id,mode),strategyFor:(asset,mode)=>window.PipelineStrategyValues.estimate(asset,mode),timingFor:(asset,mode)=>window.PipelineProspectTiming?.timingEstimate(asset,mode)});reasoning.append(renderPlainSummary(document,blocked,owner));calculations.append(renderExplanation(document,blocked,owner));explanations.push({owner,...blocked});}continue;}
  const metric=textNode('div','summary-score','');metric.append(textNode('strong','',match[1]),textNode('span','','Strategy-adjusted value change'));card.append(metric);
  const packages=textNode('div','summary-packages','');
  for(const [label,ids] of [['Receives',state.sides[1-side]],['Sends',state.sides[side]]]){const column=textNode('div','summary-package','');column.append(textNode('h4','',label));const list=document.createElement('ul');for(const id of ids)list.append(textNode('li','',assets.get(id)?.name??id));column.append(list);packages.append(column);}card.append(packages);scores.append(card);
  const bounds=inputs[side].range.match(/^Value assumption range (-?[\d.]+) to (-?[\d.]+)/);
  const explanation=explainTrade({incoming:state.sides[1-side].map(id=>assets.get(id)),outgoing:state.sides[side].map(id=>assets.get(id)),mode:state.modes[side],valueFor:(id,mode)=>val(id,mode),strategyFor:(asset,mode)=>window.PipelineStrategyValues.estimate(asset,mode),timingFor:(asset,mode)=>window.PipelineProspectTiming?.timingEstimate(asset,mode),range:bounds?{low:Number(bounds[1]),high:Number(bounds[2])}:null});
  const bridge=textNode('div','strategy-value-bridge','');bridge.append(textNode('span','','Neutral value change '+(explanation.neutralNet>=0?'+':'')+explanation.neutralNet.toFixed(1)),textNode('span','','Timing adjustment '+(explanation.timingAdjustment>=0?'+':'')+explanation.timingAdjustment.toFixed(1)));card.insertBefore(bridge,packages);card.insertBefore(textNode('p','season-outlook',state.modes[side]==='contender'?'Earlier help · maximum ±10% per asset':state.modes[side]==='rebuild'?'Later help · maximum ±10% per asset':'Neutral prices · no timing adjustment'),metric);
  explanations.push({owner,...explanation});reasoning.append(renderPlainSummary(document,explanation,owner));calculations.append(renderExplanation(document,explanation,owner));
 }
 if(explanations.length){
  const intro=textNode('div','trade-reasoning-intro','');intro.append(textNode('h3','','What this trade means'));
  reasoning.prepend(intro);technical.hidden=false;
  calculations.append(textNode('p','trade-explanation-note','Strategy-adjusted values start from the same neutral asset prices. Timing changes each asset by at most 10%; it does not replace the price with projected production. Raw production, roster costs and space sensitivity remain separate. Prices without a ranking anchor are provisional.'));
  latestExplanation={release:'price-led-explanation-20261025',valuationReview:coverageReport,teams:explanations};
 }
};
for(const id of ['ownerlabel0','ownerlabel1','net0','net1','range0','range1','assessment0','assessment1','why0','why1','assets0','assets1'])new MutationObserver(renderReadableSummaries).observe(document.getElementById(id),{childList:true,subtree:true,characterData:true});
renderReadableSummaries();
