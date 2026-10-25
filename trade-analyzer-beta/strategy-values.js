// Neutral asset prices remain authoritative. Timing changes the price by at most 10%, never replaces it.
export const RELEASE='neutral-anchored-strategy-20261025';
export const CAP=.10;
const finite=Number.isFinite,sum=xs=>xs.reduce((a,b)=>a+b,0),normalize=xs=>{const z=sum(xs);return xs.map(x=>x/z);};
export const BASELINE=normalize(Array.from({length:8},(_,t)=>.88**t));
function gaussian(center,width){return normalize(Array.from({length:8},(_,year)=>{let s=0;for(let i=0;i<=200;i++){const x=year+i/200;s+=(i===0||i===200?1:i%2?4:2)*Math.exp(-.5*((x-center)/width)**2);}return s/600;}));}
export const WEIGHTS={balanced:BASELINE,contender:gaussian(.5,1.5),rebuild:gaussian(3.5,4)};
export const POLICY={release:RELEASE,cap:CAP,responseScale:.5,forecastYear:2027,years:8,firstTwoYears:{contender:sum(WEIGHTS.contender.slice(0,2)),rebuild:sum(WEIGHTS.rebuild.slice(0,2))},meaning:'Neutral asset price plus a smooth bounded timing preference. Ranked players retain ranking-led prices; production-only prices remain provisional. Not calibrated market prices or expected category wins.'};
const validPath=p=>Array.isArray(p)&&p.length===8&&p.every(x=>finite(x)&&x>=0);
export function strategyEstimate(asset,mode,timingFor=()=>null){
 const price=asset?.values?.neutral?.display;
 if(!finite(price)||price<0)return {status:'unavailable',value:null,neutral:price??null,adjustment:null,factor:null,reason:'Neutral asset price unavailable.'};
 if(!['neutral','balanced','contender','rebuild'].includes(mode))return {status:'unavailable',value:null,neutral:price,adjustment:null,factor:null,reason:'Unknown strategy.'};
 const base={release:RELEASE,neutral:price,value:price,factor:1,adjustment:0,cap:CAP,mode,priceSource:asset.ranking_policy?.source_scope??(asset.audit?.kind==='pick'?'pick-selection policy':'production-only provisional')};
 if(mode==='neutral'||mode==='balanced')return {...base,status:'neutral',reason:'Balanced strategy preserves the neutral asset price exactly.'};
 let path,timing=null,kind=asset.audit?.kind;
 if(kind==='prospect'){timing=timingFor(asset,'balanced');path=timing?.annualUtility;}else path=asset.annual_expected_utility;
 if(!validPath(path))return {...base,status:'neutral-retained',reason:'Timing evidence unavailable; neutral price retained without inventing an arrival or a strategy bonus.'};
 if(kind==='pick'&&(!Number.isInteger(asset.audit.year)||path.some((x,i)=>2027+i<asset.audit.year&&x>0)))return {...base,status:'neutral-retained',reason:'Pick conversion timing is unsupported; neutral pick price retained.'};
 const dot=w=>sum(path.map((u,t)=>u*w[t])),balanced=dot(BASELINE),selected=dot(WEIGHTS[mode]);
 if(balanced===0)return {...base,status:'neutral-retained',reason:'No modeled timing difference; zero production surplus does not establish zero dynasty value.'};
 const ratio=selected/balanced,response=ratio===0?-1:Math.tanh(Math.log(ratio)/.5),factor=1+CAP*response,value=price*factor;
 return {...base,status:kind==='prospect'||kind==='pick'?'conditional':'timing-adjusted',factor,value,adjustment:value-price,timingRatio:ratio,annual:[...path],timingSource:timing?.source??null,regularRoleStart:timing?.regularRoleStart??null,pickConversionProxy:kind==='pick'&&asset.audit.year>2027,reason:kind==='pick'?'Conditional future selected-player contribution path; no immediate player slot or direct lineup production credited. Later draft classes use the saved uncertain proxy.':kind==='prospect'?'Supported published-ETA path; regular-role timing remains conditional.':'Saved annual contribution timing; total production magnitude does not replace the neutral price.'};
}
export function strategyBounds(asset,mode,timingFor=()=>null){
 const e=strategyEstimate(asset,mode,timingFor);if(e.value===null)return null;
 const l=asset.range?.low?.neutral,h=asset.range?.high?.neutral,valid=finite(l)&&finite(h)&&l>=0&&h>=0;
 const low=valid?Math.min(l,h,e.neutral):e.neutral,high=valid?Math.max(l,h,e.neutral):e.neutral;
 const active=mode==='contender'||mode==='rebuild';
 return {low:low*(active?1-CAP:1),high:high*(active?1+CAP:1),meaning:'Saved neutral-price envelope combined with the full permitted timing-adjustment range. Policy sensitivity, not a confidence interval.',neutralRangeAvailable:valid};
}
export function installStrategyValues(data,timingFor=()=>null){
 const byId=new Map(data.assets.map(a=>[a.id,a]));
 const api={release:RELEASE,policy:POLICY,estimate:(a,m)=>strategyEstimate(a,m,timingFor),value:(id,m)=>strategyEstimate(byId.get(id),m,timingFor).value,bounds:(id,m)=>strategyBounds(byId.get(id),m,timingFor),note:(a,m)=>{const e=strategyEstimate(a,m,timingFor);return e.value===null?e.reason:e.status==='neutral-retained'?e.reason:`Neutral ${e.neutral.toFixed(1)} ${e.adjustment>=0?'+':'−'} ${Math.abs(e.adjustment).toFixed(1)} timing adjustment; maximum ±10% per asset.`;},exportAsset(a){
  const modes=['neutral','balanced','contender','rebuild'],strategy_values=Object.fromEntries(modes.map(m=>[m,{...strategyEstimate(a,m,timingFor),range:strategyBounds(a,m,timingFor)}]));
  const safe={...a,strategy_values,production_values:a.competitive_values??null,production_range:a.competitive_range??null};delete safe.competitive_values;delete safe.competitive_range;
  if(a.audit.kind==='prospect'){safe.annual_expected_utility=null;safe.distribution_summary=null;safe.production_values=null;safe.production_range=null;safe.audit={...a.audit,eta:null,inherited_eta_withdrawn:a.audit.eta};safe.prospect_evidence={...a.prospect_evidence,snapshot:{...a.prospect_evidence?.snapshot,eta:null}};safe.conditional_timing_fit=Object.fromEntries(modes.filter(m=>m!=='neutral').map(m=>[m,timingFor(a,m)??null]));}
  return safe;
 }};return api;
}
