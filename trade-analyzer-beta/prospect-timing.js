import {renderArrival} from './arrival-workload.js';
export function needsTimingCalibration(asset){return asset?.audit?.kind==='prospect';}
export function timingEstimate(asset,mode,evidence=data){
 if(!needsTimingCalibration(asset))return null;
 const r=evidence?.players?.[asset.id];if(!r)return null;
 const scenarios=(r.scenarios??[]).filter(s=>Number.isFinite(s.fit?.[mode]));
 const sources=[r.published_evidence,...(r.additional_evidence??[])].filter(e=>e&&/^20\d{2}$/.test(String(e.value))).sort((a,b)=>String(b.retrievedDate??b.date??'').localeCompare(String(a.retrievedDate??a.date??''))||String(a.source).localeCompare(String(b.source)));
 for(const source of sources){const chosen=scenarios.find(s=>s.published_anchor===Number(source.value)&&s.illustrative_regular_role_delay===0);if(!chosen)continue;
 return {display:chosen.fit[mode],low:Math.min(...scenarios.map(s=>s.fit[mode])),high:Math.max(...scenarios.map(s=>s.fit[mode])),source,annualUtility:[...(chosen.annual_utility??[])],regularRoleStart:chosen.regular_role_start,delay:0,scenarioCount:scenarios.length,policy:'Conditional point assumes regular-role contribution begins in the latest retrieved supported published ETA year; alternatives include other saved anchors and 0/1/2-year delays. No probabilities assigned; not a calibrated expectation.'};}
 return null;
}
export function competitiveValue(asset,mode,evidence=data){return needsTimingCalibration(asset)?timingEstimate(asset,mode,evidence)?.display??null:asset?.competitive_values?.[mode]?.display??null;}
export function competitiveBounds(asset,mode,evidence=data){const r=timingEstimate(asset,mode,evidence);return r?{low:r.low,high:r.high}:null;}
export function renderTiming(doc,data,asset,mode){
 if(!needsTimingCalibration(asset))return null;
 const make=(tag,text)=>{const e=doc.createElement(tag);if(text!==undefined)e.textContent=text;return e;};
 const section=make('section');section.setAttribute('aria-label','Prospect arrival timing audit');
 const estimate=timingEstimate(asset,mode,data);section.append(make('h3','Prospect arrival timing'),make('p',estimate?'Raw conditional production score: '+estimate.display.toFixed(1)+'. Uses '+estimate.source.source+' ETA '+estimate.source.value+' with no additional delay to regular-role contribution. This is an explicit assumption, not a calibrated playing-time forecast.':'Raw production timing unavailable: no supported published-ETA scenario. The strategy-adjusted asset price retains neutral value.'));
 const r=data?.players?.[asset.id];if(!r){section.append(make('p','Published timing evidence could not be loaded. No arrival estimate substituted.'));return section;}
 section.append(make('p','Inherited model ETA '+r.inherited_model_eta+' has been withdrawn from trade conclusions.'));
 for(const e of [r.published_evidence,...(r.additional_evidence||[])].filter(Boolean)){
  section.append(make('p',e.source+' ETA: '+e.value+' · retrieved '+e.retrievedDate+' · an arrival estimate, not regular playing time.'));
  if(e.url){const link=make('a','Open '+e.source+' source');link.href=e.url;link.target='_blank';link.rel='noopener';section.append(link);}else section.append(make('p','User-supplied source snapshot; publication date not independently established.')); 
 }
 if(!r.published_evidence)section.append(make('p','No traceable published ETA in the saved evidence. Timing scenarios unavailable.'));
 if(r.scenarios?.length){
  section.append(make('h4','Conditional timing scenarios'),make('p',data.scenario_definition));
  const table=make('table');for(const row of [['Published ETA anchor','Illustrative delay to regular role','Regular-role start',mode+' production score'],...r.scenarios.map(s=>[s.published_anchor,s.illustrative_regular_role_delay+' years',s.regular_role_start,s.fit[mode].toFixed(1)])]){
   const tr=make('tr');for(const cell of row)tr.append(make('td',String(cell)));table.append(tr);
  }section.append(table,make('p','The selected raw production score is diagnostic only; it does not enter the asset-price totals. The price uses the supported annual path for a bounded timing adjustment. No probabilities are assigned, and the envelope is not a confidence interval. Neutral dynasty prices stay unchanged.'));
 }else if(r.published_evidence)section.append(make('p','The source ETA predates the frozen trajectory. Missing earlier production cannot be reconstructed safely; no timing scenario invented.'));
 return section;
}
let data=null,arrivalModel=null;if(typeof window!=='undefined'){try{const response=await fetch('/data/prospect-timing-audit.json');if(!response.ok)throw Error('Timing evidence unavailable');data=await response.json();try{const next=await fetch('/data/arrival-workload-model.json');if(next.ok)arrivalModel=await next.json();}catch(error){console.error('Arrival research unavailable',error);}}catch(error){console.error(error);}}
export function mount(body,asset,mode){const section=renderTiming(body.ownerDocument,data,asset,mode);if(section)body.append(section);const modelSection=renderArrival(body.ownerDocument,arrivalModel,asset);if(modelSection)body.append(modelSection);}
