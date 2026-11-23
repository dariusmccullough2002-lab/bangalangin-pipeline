// Pipeline model scores, not publication grades. No organizational rank sums.
export const farmWeights=Object.freeze({elite:.25,topTen:.20,depth:.15,ceiling:.10,proximity:.10,hitting:.05,pitching:.05,certainty:.10});
const clamp=x=>Math.max(0,Math.min(100,x));
const mean=a=>a.length?a.reduce((s,x)=>s+x,0)/a.length:0;
const sum=a=>a.reduce((s,x)=>s+x,0);
const value=p=>100/(1+(p.leagueRank/45)**1.25);
const stat=(p,type)=>p.seasonStats?.groups.find(g=>g.group===type);
const future=g=>Number.parseFloat(String(g).split('/').at(-1));
function certainty(p){
  const g=stat(p,p.type==='P'?'pitching':'hitting');
  const stage={AAA:15,AA:10,'A+':4,A:0,CPX:-10,DSL:-15}[p.level]??-20;
  let score=55+stage;
  if(!g)return clamp(score-15);
  if(g.group==='hitting')score-=Math.max(0,g.kPercent-20)*1.1;
  else score-=Math.max(0,g.bbPercent-8)*2;
  const sample=g.group==='hitting'?g.pa:g.outs/3;
  const full=g.group==='hitting'?400:100;
  score+=10*Math.min(sample/full,1);
  if(sample<full/3)score-=10;
  return clamp(score);
}
function ceiling(p){
  const tools=p.scoutingGrades?.tools??{};
  const impact=Object.entries(tools).filter(([k])=>!['Command','Control'].includes(k)).map(([,g])=>future(g)).filter(Number.isFinite);
  // Unknown grades fall back to ranking value, never an invented 20–80 grade.
  const signal=impact.length?clamp((Math.max(...impact)-30)*2):value(p);
  return signal*(.6+.4*certainty(p)/100);
}
export function scoreFarms(players,organizations){
  const raw=organizations.map(org=>{
    const pool=players.filter(p=>p.organizationId===org.id).sort((a,b)=>a.leagueRank-b.leagueRank);
    const top=pool.slice(0,10),five=pool.slice(0,5),vals=pool.map(value);
    const hitters=pool.filter(p=>p.type!=='P'),pitchers=pool.filter(p=>p.type==='P'||p.type==='B');
    const proximity=top.length?sum(top.map(p=>value(p)*({AAA:1,AA:.7,'A+':.35,A:.2,CPX:.08,DSL:.05}[p.level]??0)))/sum(top.map(value))*100:0;
    return {organizationId:org.id,name:org.currentName??org.name,eligibleCount:pool.length,top100Count:pool.filter(p=>p.leagueRank<=100).length,hitters:hitters.length,pitchers:pitchers.length,bestProspect:pool[0]?.playerId,components:{
      elite:.6*(vals[0]??0)+.4*sum(five.map(value))/5,
      topTen:sum(top.map(value))/10,
      depth:50*Math.min(pool.length/30,1)+50*Math.min(vals.filter(v=>v>=20).length/20,1),
      ceiling:sum(five.map(ceiling))/5,
      proximity,
      hitting:sum(hitters.slice(0,10).map(value))/10,
      pitching:sum(pitchers.slice(0,5).map(value))/5,
      certainty:mean(top.map(certainty))
    }};
  });
  // Relative component scores make units comparable; each league leader is 100.
  const maxima=Object.fromEntries(Object.keys(farmWeights).map(k=>[k,Math.max(...raw.map(f=>f.components[k]))]));
  for(const f of raw){
    f.rawComponents={...f.components};
    f.components=Object.fromEntries(Object.entries(f.components).map(([k,v])=>[k,maxima[k]?v/maxima[k]*100:0]));
    f.composite=sum(Object.entries(farmWeights).map(([k,w])=>f.components[k]*w));
  }
  raw.sort((a,b)=>b.composite-a.composite||a.organizationId.localeCompare(b.organizationId));
  const leader=raw[0]?.composite??0;
  return raw.map((f,i)=>{
    const index=leader?f.composite/leader*100:0;
    const tier=index>=90?'Elite':index>=80?'Strong':index>=65?'Above average':index>=45?'Middle':'Thin';
    const strengths=Object.entries(f.components).sort((a,b)=>b[1]-a[1]).slice(0,2).map(([k])=>({elite:'elite talent',topTen:'top-ten quality',depth:'depth',ceiling:'ceiling',proximity:'MLB proximity',hitting:'hitting',pitching:'pitching',certainty:'lower development risk'}[k]));
    const best=players.find(p=>p.playerId===f.bestProspect);
    const explanation=`${best?.name??'No eligible prospect'} leads a farm with ${f.top100Count} league Top 100 prospects and ${f.eligibleCount} eligible players. ${strengths.join(' and ')} are its strongest relative components. The pool includes ${f.hitters} hitters and ${f.pitchers} pitchers${players.some(p=>p.organizationId===f.organizationId&&p.type==='B')?' (two-way players count in both groups)':''}. This ordering evaluates only non-debuted prospects; players already in MLB contribute no farm value.`;
    return {...f,rank:i+1,index:Number(index.toFixed(1)),gap:Number((100-index).toFixed(1)),tier,explanation};
  });
}
