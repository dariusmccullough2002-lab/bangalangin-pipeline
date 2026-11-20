// Research-only helpers. No Pipeline rank/grade imports or writes.
export const risk=(p,m)=>((p.chase-m.means[0])/m.scales[0]+(p.whiff-m.means[1])/m.scales[1])/2;
export function probability(p,m){if(!p.qualified||!p.supported)return null;const z=m.intercept+m.features.reduce((s,k,i)=>s+p[k]*m.coefficients[i],0);return 1/(1+Math.exp(-z));}
export const distance=(a,b,m)=>Math.sqrt(m.features.reduce((s,k,i)=>s+((a[k]-b[k])/m.scales[i])**2,0));
export function nearest(p,rows,m,endpoint,n=4){return rows.filter(x=>x.qualified&&x.playerId!==p.playerId&&x.endpoint===endpoint).map(x=>({...x,distance:distance(p,x,m)})).sort((a,b)=>a.distance-b.distance||a.id.localeCompare(b.id)).slice(0,n);}
export const endpoint=p=>p.iso>=.200&&p.woba>=.330;
export function sortRows(rows,key,ascending=false){return [...rows].sort((a,b)=>(ascending?1:-1)*((a[key]??-Infinity)-(b[key]??-Infinity))||a.id.localeCompare(b.id));}
export function archetype(p){
 if(!['chase','whiff','hard_hit','barrel'].every(k=>Number.isFinite(p[k])))return 'Insufficient data';
 if(p.hard_hit>=45&&p.barrel<8)return 'Hard contact / fewer barrels';
 if(p.hard_hit>=45&&p.barrel>=10){if(p.chase>=35&&p.whiff>=30)return 'High risk / high impact';if(p.whiff>=30)return 'High impact / more whiff';if(p.chase>=35)return 'High impact / more chase';return 'High impact / lower risk';}
 if(p.whiff<25&&p.hard_hit<40)return 'More contact / less impact';return 'Mixed components';
}
