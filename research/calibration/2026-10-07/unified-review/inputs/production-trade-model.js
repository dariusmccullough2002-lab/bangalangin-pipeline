export const MODES={contender:{label:'Contender',years:[.65,.25,.10],future:.85,risk:.20},balanced:{label:'Balanced',years:[.40,.30,.30],future:1,risk:.12},rebuild:{label:'Rebuild',years:[.15,.25,.60],future:1.15,risk:.06}};
export const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
export function innings(ip){const s=String(ip).split('.');return Number(s[0])+(Number(s[1]||0)/3);}
export function kbb(k,bb){return bb>0?k/bb:k*1.01;}
export function qa3(ip,er){return (ip>=5&&er<=2)||(ip>=6&&er<=3);}
export function ratios(b={},p={}){return {AVG:b.AB?b.H/b.AB:0,OPS:(b.AB+b.BB+b.HBP+b.SF?((b.H||0)+(b.BB||0)+(b.HBP||0))/(b.AB+b.BB+b.HBP+b.SF):0)+(b.AB?(b.TB||0)/b.AB:0),WHIP:p.IP?((p.H||0)+(p.BB||0))/p.IP:0,'K/BB':kbb(p.K||0,p.BB||0)};}
const sum=(a,k)=>a.reduce((v,p)=>v+(p[k]||0),0);
export function aggregate(projected){const b={},p={};for(const k of ['AB','H','BB','HBP','SF','TB','HR','R','RBI','SB'])b[k]=sum(projected.map(v=>v.bat),k);for(const k of ['IP','H','BB','K','ER','SVH7','QA3'])p[k]=sum(projected.map(v=>v.pit),k);return {...b,...Object.fromEntries(['IP','K','ER','SVH7','QA3'].map(k=>[k,p[k]])),...ratios(b,p)};}
// Transparent statistical scenarios, not licensed projection data. No invented prospect MLB lines.
export function project(player,year,context={}){const n=year-2026,age=(player.age||28)+n;const young=age<27?1.015:age>30?Math.max(.85,1-.025*(age-30)):1;const rate=Math.pow(young,n)*(context.skills??1),work=clamp(Math.pow(age>32?.96:1,n)*(context.role??1),0,1.5);const bat={},pit={};for(const [k,v]of Object.entries(player.bat||{}))bat[k]=v*work;for(const [k,v]of Object.entries(player.pit||{}))pit[k]=v*work;pit.IP=innings(player.pit?.IP||0)*work;
 for(const k of ['H','TB','HR','R','RBI','SB'])bat[k]=(bat[k]||0)*rate;
 bat.H=Math.min(bat.H||0,bat.AB||0);bat.TB=Math.max(bat.H,bat.TB||0);
 pit.K=(pit.K||0)*rate;for(const k of ['H','BB','ER'])pit[k]=(pit[k]||0)/Math.max(.5,rate);
 pit.QA3=(pit.QA3||0)*rate;return {bat,pit};}
export function categoryUnits(v){const b=v.bat,p=v.pit,r=ratios(b,p);return [(b.HR||0)/8,(b.R||0)/25,(b.RBI||0)/25,(b.SB||0)/8,((b.H||0)-.250*(b.AB||0))/15,((r.OPS||0)-.720)*(b.AB||0)/40,(p.K||0)/45,-(p.ER||0)/15,(p.SVH7||0)/30,(p.QA3||0)/5,((p.K||0)-3*(p.BB||0))/40,(1.25*(p.IP||0)-(p.H||0)-(p.BB||0))/15];}
export function productionValue(p,year,c={}){const projection=project(p,year,c),units=categoryUnits(projection);const raw=units.reduce((a,b)=>a+b,0);const volume=(projection.bat.AB||0)+(projection.pit.IP||0)*3;return volume>0?clamp(12+raw*4,0,100):0;}
export function value(p,mode='balanced',context={}){const m=MODES[mode]||MODES.balanced;if(p.kind==='pick'){const base=[0,48,29,18,11,7][p.round],discount=Math.pow(.85,p.year-2027);return base*discount*m.future*(context.slot==='early'?1.2:context.slot==='late'?.8:1);}
 const base=m.years.reduce((v,w,i)=>v+w*productionValue(p,2027+i,context),0);
 const rank=p.prospect?.rank;let future=0;if(rank){const eta=Number(String(p.prospect.eta||'').match(/20\d\d/)?.[0]||2030);const access=m.years.reduce((s,w,i)=>s+w*(2027+i>=eta?1:.35),0);future=(65*Math.exp(-(rank-1)/90)+5)*access*m.future;}
 const risk=context.risk??(rank?.35:.15);return Math.max(base,future)*(1-m.risk*risk);}
export function tradeResult(give,receive,mode,contexts={}){const total=a=>a.reduce((s,p)=>s+value(p,mode,contexts[p.id]||{}),0);const received=total(receive),sent=total(give);return {received,sent,delta:received-sent};}

