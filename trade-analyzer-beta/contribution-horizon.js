// Separate calendar production from an eight-year time preference. No new prices.
export const FORECAST_YEAR=2027;
export const HORIZON_RELEASE='calendar-contribution-20261024';
const finite=Number.isFinite;
function pathFor(asset,timingFor){
 const kind=asset?.audit?.kind;
 if(kind==='pick')return {path:Array(8).fill(0),status:'no-direct-production',reason:'A draft pick is an acquisition opportunity; no direct MLB production is credited before a player is selected. Its dynasty and multi-year values remain separate.'};
 if(kind==='prospect'){
  const timing=timingFor(asset,'balanced');
  if(!timing?.annualUtility?.length)return {path:null,status:'unavailable',reason:'A supported calendar-aligned prospect path is unavailable; no zero or inherited ETA substituted.'};
  return {path:timing.annualUtility,status:'conditional',regularRoleStart:timing.regularRoleStart,reason:`Published-ETA scenario: regular-role contribution begins in ${timing.regularRoleStart}. Earlier years have no credited production in this scenario, not a guarantee of no MLB debut.`};
 }
 const projection=asset?.audit?.MLB?.projection??asset?.audit?.projection;
 if(!projection||!((projection.PA??0)>0||(projection.IP??0)>0))return {path:null,status:'unavailable',reason:'Supported MLB production forecast unavailable.'};
 const path=asset.annual_expected_utility;
 if(!Array.isArray(path)||path.length!==8||!path.every(x=>finite(x)&&x>=0))return {path:null,status:'unavailable',reason:'Complete saved annual contribution path unavailable.'};
 return {path,status:'projected',reason:'Saved annual expected contribution, including the existing aging and availability assumptions.'};
}
export function compareHorizons(incoming,outgoing,timingFor=()=>null){
 const rows=[...incoming.map(asset=>({asset,direction:1})),...outgoing.map(asset=>({asset,direction:-1}))].map(({asset,direction})=>{
  const p=pathFor(asset,timingFor),valid=p.path?.length===8&&p.path.every(x=>finite(x)&&x>=0);
  return {id:asset.id,name:asset.name,direction,status:valid?p.status:'unavailable',reason:p.reason,regularRoleStart:p.regularRoleStart??null,annual:valid?[...p.path]:null};
 });
 const complete=incoming.length>0&&outgoing.length>0&&rows.every(r=>r.annual);
 const total=(direction,start,end)=>complete?rows.filter(r=>r.direction===direction).reduce((n,r)=>n+r.annual.slice(start,end).reduce((a,b)=>a+b,0),0):null;
 const periods=[[FORECAST_YEAR,0,1],['firstThreeYears',0,3],['laterYears',3,8]].map(([period,start,end])=>{const received=total(1,start,end),sent=total(-1,start,end);return {period,received,sent,net:complete?received-sent:null};});
 return {release:HORIZON_RELEASE,forecastYear:FORECAST_YEAR,complete,conditional:rows.some(r=>r.status==='conditional'),nextSeason:periods[0],firstThreeYears:periods[1],laterYears:periods[2],rows,units:'Saved annual contribution utility; not asset-price points or category wins',limits:'Package production before lineup displacement. No daily schedule, waiver additions, position fit or weekly category simulation. Future picks receive no direct production credit; their asset value is retained separately.'};
}
export function seasonOutlook(horizon){
 if(!horizon.complete)return 'Next season: comparison unavailable';
 const net=horizon.nextSeason.net;
 return `${horizon.forecastYear} outlook: ${Math.abs(net)<.000001?'similar projected production':net>0?'more projected production':'less projected production'}${horizon.conditional?' · conditional':''}`;
}
