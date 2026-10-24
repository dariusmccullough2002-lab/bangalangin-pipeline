// Offline structural candidates. No production import or learned player overrides.
const finite=Number.isFinite;
export function rankingAnchoredCandidate(price,balanced,selected,cap=.10){
 if(![price,balanced,selected,cap].every(finite)||price<0||balanced<0||selected<0||cap<0||cap>1)return {status:'blocked',value:null,reason:'Invalid or unavailable valuation input'};
 if(balanced===0)return selected===0?{status:'flat-zero-contribution',value:price,factor:1,reason:'No modeled timing difference; asset price retained, not a production forecast'}:{status:'blocked',value:null,reason:'Nonzero selected fit with zero balanced denominator'};
 const ratio=selected/balanced,factor=Math.min(1+cap,Math.max(1-cap,ratio));
 return {status:'candidate',value:price*factor,factor,uncappedFactor:ratio,capped:Math.abs(ratio-1)>cap,policy:'Ranking-led price multiplied by bounded relative timing preference; unvalidated market/strategy policy, not a trained projection'};
}
export function windowContribution(path,years){
 if(!Number.isInteger(years)||years<1||years>8||!Array.isArray(path)||path.length!==8||!path.every(x=>finite(x)&&x>=0))return null;
 return path.slice(0,years).reduce((a,b)=>a+b,0);
}
