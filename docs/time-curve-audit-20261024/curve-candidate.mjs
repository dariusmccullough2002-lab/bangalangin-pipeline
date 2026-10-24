import {rankingAnchoredCandidate} from '../strategy-setting-audit-20261024/policy-candidates.mjs';
const sum=a=>a.reduce((x,y)=>x+y,0);
export function normalize(a){const total=sum(a);if(!Number.isFinite(total)||total<=0)throw Error('Invalid curve mass');return a.map(x=>x/total);}
// Integrate each season rather than sampling only at its midpoint. Units: years from forecast start.
export function gaussianWeights(center,width){
 if(!Number.isFinite(center)||!Number.isFinite(width)||width<=0)throw Error('Invalid Gaussian');
 return normalize(Array.from({length:8},(_,year)=>{let s=0;const n=200;for(let i=0;i<=n;i++){const x=year+i/n;s+=(i===0||i===n?1:i%2?4:2)*Math.exp(-.5*((x-center)/width)**2);}return s/(3*n);}));
}
export const baseline=normalize(Array.from({length:8},(_,t)=>.88**t));
export const profiles={
 'existing':{contender:normalize(Array.from({length:8},(_,t)=>.75**t)),rebuild:normalize(Array.from({length:8},(_,t)=>.94**t))},
 'front-loaded':{contender:gaussianWeights(.5,1.5),rebuild:gaussianWeights(3.5,4)},
 'gentler':{contender:gaussianWeights(.5,2),rebuild:gaussianWeights(3.5,4)}
};
export function curveValue(price,path,weights,cap){
 if(!Array.isArray(path)||path.length!==8||!path.every(x=>Number.isFinite(x)&&x>=0))return {value:null,status:'blocked',reason:'Missing or invalid annual contribution path'};
 const dot=w=>sum(path.map((x,i)=>x*w[i]));return rankingAnchoredCandidate(price,dot(baseline),dot(weights),cap);
}
export function allocateNeutral(price,path){
 if(!Number.isFinite(price)||price<0||!Array.isArray(path)||path.length!==8||!path.every(x=>Number.isFinite(x)&&x>=0)||sum(path)===0)return null;
 return normalize(path.map((x,i)=>x*baseline[i])).map(x=>price*x);
}

// Smooth policy alternative: log-ratio response approaches the cap without hard clipping.
// scale=.5 is a fixed sensitivity assumption, not fitted to trades.
export function smoothCurveValue(price,path,weights,cap,scale=.5){
 const raw=curveValue(price,path,weights,cap);if(raw.value===null||raw.status==='flat-zero-contribution')return raw;
 const r=raw.uncappedFactor;const response=r===0?-1:Math.tanh(Math.log(r)/scale);
 const factor=1+cap*response;return {...raw,value:price*factor,factor,capped:false,response,policy:'Ranking-anchored smooth bounded timing response; unvalidated policy'};
}
