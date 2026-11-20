// Research-only helpers. No Pipeline rank/grade imports or writes.
export const risk=(p,m)=>((p.chase-m.means[0])/m.scales[0]+(p.whiff-m.means[1])/m.scales[1])/2;
export function probability(p,m){if(!p.qualified||!p.supported)return null;const z=m.intercept+m.features.reduce((s,k,i)=>s+p[k]*m.coefficients[i],0);return 1/(1+Math.exp(-z));}
export const distance=(a,b,m)=>Math.sqrt(m.features.reduce((s,k,i)=>s+((a[k]-b[k])/m.scales[i])**2,0));
export function nearest(p,rows,m,endpoint,n=4){return rows.filter(x=>x.qualified&&x.playerId!==p.playerId&&x.endpoint===endpoint).map(x=>({...x,distance:distance(p,x,m)})).sort((a,b)=>a.distance-b.distance||a.id.localeCompare(b.id)).slice(0,n);}
export const endpoint=p=>p.iso>=.200&&p.woba>=.330;
// Display sampling only: deterministic coverage of four regions and both outcomes.
// Model fitting, neighbors, filters and tables always use the full dataset.
export function benchmarkSample(rows,selected,m,limit=25){
 const pool=[...rows].sort((a,b)=>a.id.localeCompare(b.id)),out=[];
 const add=p=>{if(p&&!out.some(x=>x.id===p.id)&&out.length<limit)out.push(p);};
 add(pool.find(p=>p.id===selected?.id));
 const median=m.means[2];
 const groups=Array.from({length:8},(_,i)=>pool.filter(p=>(risk(p,m)>=0?4:0)+(p.hard_hit>=median?2:0)+(p.endpoint?1:0)===i));
 // Reference names and observed extremes anchor the reading; remaining slots
 // maximize standardized component coverage within region/outcome strata.
 for(const id of [621566,660271,646240,691718,592450,656941,695578,571970,608336])add(pool.filter(p=>p.playerId===id).sort((a,b)=>b.year-a.year)[0]);
 for(const f of [p=>risk(p,m),p=>p.hard_hit]){add([...pool].sort((a,b)=>f(a)-f(b))[0]);add([...pool].sort((a,b)=>f(b)-f(a))[0]);}
 for(let step=0;out.length<limit&&step<pool.length;step++){
  const before=out.length;
  for(const g of groups){const remaining=g.filter(p=>!out.some(x=>x.id===p.id));remaining.sort((a,b)=>Math.min(...out.map(p=>distance(b,p,m)))-Math.min(...out.map(p=>distance(a,p,m)))||a.id.localeCompare(b.id));add(remaining[0]);}
  if(out.length===before)break;
 }
 return out;
}
export function sortRows(rows,key,ascending=false){return [...rows].sort((a,b)=>(ascending?1:-1)*((a[key]??-Infinity)-(b[key]??-Infinity))||a.id.localeCompare(b.id));}
export function archetype(p){
 if(!['chase','whiff','hard_hit','barrel'].every(k=>Number.isFinite(p[k])))return 'Insufficient data';
 if(p.hard_hit>=45&&p.barrel<8)return 'Hard contact / fewer barrels';
 if(p.hard_hit>=45&&p.barrel>=10){if(p.chase>=35&&p.whiff>=30)return 'High risk / high impact';if(p.whiff>=30)return 'High impact / more whiff';if(p.chase>=35)return 'High impact / more chase';return 'High impact / lower risk';}
 if(p.whiff<25&&p.hard_hit<40)return 'More contact / less impact';return 'Mixed components';
}
