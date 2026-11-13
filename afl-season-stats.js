// MLB's stats endpoint does not aggregate comma-separated gameType values.
// Fetch each competition separately, then add counting stats and rebuild rates.
export const AFL_GAME_TYPES=['R','D','L','W'];
export const AFL_STATS_URL='https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting,pitching&season=2026&leagueIds=119&sportIds=17&playerPool=ALL&limit=1000&gameType=R';
const rate=(n,d,digits=3)=>d>0?(n/d).toFixed(digits):(0).toFixed(digits);
const ipOuts=ip=>{const [whole,part='0']=String(ip??'0.0').split('.');if(!/^\d+$/.test(whole)||!/[012]/.test(part)||part.length!==1)throw Error('Invalid innings');return Number(whole)*3+Number(part);};
export function combineAflStats(payloads,{teamStats=false}={}){
 const groups=new Map();
 for(const payload of payloads) {
  if(!Array.isArray(payload?.stats))throw Error('Invalid AFL stats response');
  for(const group of payload.stats){
   if(group.totalSplits!=null&&(group.splits?.length??0)<group.totalSplits)throw Error('Truncated AFL feed');
   const kind=group.group?.displayName;if(!['hitting','pitching'].includes(kind))continue;
   if(!groups.has(kind))groups.set(kind,{...group,splits:new Map()});
   const rows=groups.get(kind).splits;
   for(const row of group.splits??[]){
    const id=teamStats?row.team?.id:row.player?.id;if(!Number.isSafeInteger(id))throw Error('AFL stat row lacks identity');
    if(!rows.has(id))rows.set(id,{...row,stat:{},_outs:0});
    const dest=rows.get(id);
    for(const [key,value] of Object.entries(row.stat??{})){
     if(typeof value==='number'&&key!=='age')dest.stat[key]=(dest.stat[key]??0)+value;
     else if(key==='age')dest.stat.age=value;
    }
    if(kind==='pitching')dest._outs+=Number.isFinite(row.stat.outs)?row.stat.outs:ipOuts(row.stat.inningsPitched);
   }
  }
 }
 const stats=[...groups.values()].map(group=>{
  const splits=[...group.splits.values()].map(({_outs,...row})=>{
   const s=row.stat,n=k=>s[k]??0;
   s.avg=rate(n('hits'),n('atBats'));
   const onBase=n('hits')+n('baseOnBalls')+n('hitByPitch'),obpDen=n('atBats')+n('baseOnBalls')+n('hitByPitch')+n('sacFlies');
   s.obp=rate(onBase,obpDen);s.slg=rate(n('totalBases'),n('atBats'));
   s.ops=((obpDen?onBase/obpDen:0)+(n('atBats')?n('totalBases')/n('atBats'):0)).toFixed(3);
   s.babip=rate(n('hits')-n('homeRuns'),n('atBats')-n('strikeOuts')-n('homeRuns')+n('sacFlies'));
   s.stolenBasePercentage=rate(n('stolenBases'),n('stolenBases')+n('caughtStealing'));
   if(group.group.displayName==='pitching'){
    s.outs=_outs;s.inningsPitched=Math.floor(_outs/3)+'.'+_outs%3;
    s.era=_outs?rate(n('earnedRuns')*27,_outs,2):'-.--';s.whip=_outs?rate((n('hits')+n('baseOnBalls'))*3,_outs,2):'-.--';
    s.strikeoutWalkRatio=rate(n('strikeOuts'),n('baseOnBalls'),2);
    for(const [key,count] of [['strikeoutsPer9Inn','strikeOuts'],['walksPer9Inn','baseOnBalls'],['hitsPer9Inn','hits'],['homeRunsPer9','homeRuns']])s[key]=rate(n(count)*27,_outs,2);
   }
   return row;
  });return {...group,totalSplits:splits.length,splits};
 });
 return {stats,scope:'regular-season-and-postseason',gameTypes:[...AFL_GAME_TYPES]};
}
export async function fetchCombinedAflStats({fetcher=fetch,signal}={}){
 const payloads=await Promise.all(AFL_GAME_TYPES.map(async type=>{
  const response=await fetcher(AFL_STATS_URL.replace('gameType=R','gameType='+type),{signal,cache:'no-store'});
  if(!response.ok)throw Error('MLB '+type+' stats unavailable');return response.json();
 }));
 return combineAflStats(payloads);
}
