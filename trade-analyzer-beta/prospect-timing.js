import {renderArrival} from './arrival-workload.js';
export function needsTimingCalibration(asset){return asset?.audit?.kind==='prospect';}
export function competitiveValue(asset,mode){return needsTimingCalibration(asset)?null:asset?.competitive_values?.[mode]?.display??null;}
export function renderTiming(doc,data,asset,mode){
 if(!needsTimingCalibration(asset))return null;
 const make=(tag,text)=>{const e=doc.createElement(tag);if(text!==undefined)e.textContent=text;return e;};
 const section=make('section');section.setAttribute('aria-label','Prospect arrival timing audit');
 section.append(make('h3','Prospect arrival timing'),make('p','Competitive fit unavailable: debut timing and regular MLB playing time are not separately calibrated. Dynasty value remains available.'));
 const r=data?.players?.[asset.id];if(!r){section.append(make('p','Published timing evidence could not be loaded. No arrival estimate substituted.'));return section;}
 section.append(make('p','Inherited model ETA '+r.inherited_model_eta+' has been withdrawn from trade conclusions.'));
 for(const e of [r.published_evidence,...(r.additional_evidence||[])].filter(Boolean)){
  section.append(make('p',e.source+' ETA: '+e.value+' · retrieved '+e.retrievedDate+' · an arrival estimate, not regular playing time.'));
  const link=make('a','Open '+e.source+' source');link.href=e.url;link.target='_blank';link.rel='noopener';section.append(link);
 }
 if(!r.published_evidence)section.append(make('p','No traceable published ETA in the saved evidence. Timing scenarios unavailable.'));
 if(r.scenarios.length){
  section.append(make('h4','Conditional timing scenarios'),make('p',data.scenario_definition));
  const table=make('table');for(const row of [['Published ETA anchor','Illustrative delay to regular role','Regular-role start',mode+' production score'],...r.scenarios.map(s=>[s.published_anchor,s.illustrative_regular_role_delay+' years',s.regular_role_start,s.fit[mode].toFixed(1)])]){
   const tr=make('tr');for(const cell of row)tr.append(make('td',String(cell)));table.append(tr);
  }section.append(table,make('p','Scenario scores are excluded from trade totals. No single arrival probability or preferred scenario has been assigned.'));
 }else if(r.published_evidence)section.append(make('p','The source ETA predates the frozen trajectory. Missing earlier production cannot be reconstructed safely; no timing scenario invented.'));
 return section;
}
let data=null,arrivalModel=null;if(typeof window!=='undefined'){try{const response=await fetch('/data/prospect-timing-audit.json');if(!response.ok)throw Error('Timing evidence unavailable');data=await response.json();try{const next=await fetch('/data/arrival-workload-model.json');if(next.ok)arrivalModel=await next.json();}catch(error){console.error('Arrival research unavailable',error);}}catch(error){console.error(error);}}
export function mount(body,asset,mode){const section=renderTiming(body.ownerDocument,data,asset,mode);if(section)body.append(section);const modelSection=renderArrival(body.ownerDocument,arrivalModel,asset);if(modelSection)body.append(modelSection);}
