const keys=['pa','ab','h','tb','bb','hbp','sf','sh'];
const empty=()=>Object.fromEntries(keys.map(k=>[k,0]));
const add=(a,b)=>{for(const k of keys)a[k]+=b[k];return a;};
const minus=(a,b)=>Object.fromEntries(keys.map(k=>{const n=a[k]-(b?.[k]??0);if(n<0)throw Error('Negative leave-pitcher-out count');return [k,n];}));
export function eventOffense(event){
 const v=empty();v.pa=1;
 const bases={single:1,double:2,triple:3,home_run:4};
 if(bases[event]){v.h=1;v.tb=bases[event];}
 if(['walk','intent_walk'].includes(event))v.bb=1;
 if(event==='hit_by_pitch')v.hbp=1;
 if(['sac_fly','sac_fly_double_play'].includes(event))v.sf=1;
 if(['sac_bunt','sac_bunt_double_play'].includes(event))v.sh=1;
 v.ab=!(v.bb||v.hbp||v.sf||v.sh||['catcher_interf','defensive_shift_violation'].includes(event))?1:0;
 return v;
}
const ops=s=>{
 const den=s.ab+s.bb+s.hbp+s.sf;
 return s.pa>0&&den>0&&s.ab>0?(s.h+s.bb+s.hbp)/den+s.tb/s.ab:null;
};
const bucket=(map,key)=>{if(!map.has(key))map.set(key,empty());return map.get(key);};

// No CBS+, PQI, ERA, K rate, cross-pitcher z score or fitted season-wide
// calibration enters this calculation. Every reference removes the target arm.
export function calculatePitcherOqi(games,hitting,pitching=[]){
 const hitters=new Map(),teams=new Map(),arms=new Map(),league=empty();
 for(const game of games){
  if(!Array.isArray(game.plateAppearances))throw Error('Pitcher OQI needs outcome-level PA data');
  for(const [batter,pitcher,team,event] of game.plateAppearances){
   if(![batter,pitcher,team].every(Number.isSafeInteger))throw Error('PA lacks stable player/team identity');
   const v=eventOffense(event);add(league,v);add(bucket(hitters,batter),v);add(bucket(teams,team),v);
   if(!arms.has(pitcher))arms.set(pitcher,{total:empty(),hitters:new Map(),teams:new Map(),opponents:new Map()});
   const arm=arms.get(pitcher);add(arm.total,v);add(bucket(arm.hitters,batter),v);add(bucket(arm.teams,team),v);
   const key=batter+':'+team;arm.opponents.set(key,{batter,team,bf:(arm.opponents.get(key)?.bf??0)+1});
  }
 }
 // Outcome extraction must agree with official offensive counting stats before
 // any opponent ratings are published. Rate fields are never reverse engineered.
 const fields={pa:'plateAppearances',ab:'atBats',h:'hits',tb:'totalBases',bb:'baseOnBalls',hbp:'hitByPitch',sf:'sacFlies',sh:'sacBunts'};
 const official=new Map();
 for(const row of hitting){
  if(!official.has(row.player.id))official.set(row.player.id,{player:row.player,stat:{}});
  const dest=official.get(row.player.id).stat;
  for(const key of Object.values(fields))dest[key]=(dest[key]??0)+Number(row.stat[key]??0);
 }
 for(const row of official.values()){
  const actual=hitters.get(row.player.id)??empty();
  for(const [key,official] of Object.entries(fields)){
   if(actual[key]!==Number(row.stat[official]??0))throw Error(`OQI counting-stat mismatch: ${row.player.fullName} ${official} ${actual[key]} vs ${row.stat[official]}`);
  }
 }
 const identities=new Map(pitching.map(r=>[r.player.id,r]));
 const rows=[...arms].map(([mlbamId,arm])=>{
  const leagueOps=ops(minus(league,arm.total));let weighted=0,independentBf=0,neutralBf=0;
  for(const {batter,team,bf} of arm.opponents.values()){
   const outside=minus(hitters.get(batter),arm.hitters.get(batter));
   const hitterOps=ops(outside),teamOps=ops(minus(teams.get(team),arm.teams.get(team)));
   let quality=1;
   if(hitterOps!=null&&leagueOps>0){
    const reliability=outside.pa/(outside.pa+40);
    const reference=teamOps>0?teamOps:leagueOps;
    quality+=reliability*(.65*(hitterOps/leagueOps-1)+.35*(hitterOps/reference-1));
    independentBf+=bf;
   }else neutralBf+=bf;
   weighted+=bf*quality;
  }
  const info=identities.get(mlbamId);
  return {mlbamId,name:info?.player.fullName??String(mlbamId),team:info?.team?.name??'AFL',
   bf:arm.total.pa,independentBf,neutralBf,uniqueHitters:arm.hitters.size,
   oqi:Number((100*weighted/arm.total.pa).toFixed(3)),smallSample:arm.total.pa<20,
   ip:info?.stat.inningsPitched??null,era:info?.stat.era??null,
   strikeOuts:info?.stat.strikeOuts??null,baseOnBalls:info?.stat.baseOnBalls??null};
 }).sort((a,b)=>b.oqi-a.oqi||b.bf-a.bf||a.mlbamId-b.mlbamId);
 let rank=0;for(const row of rows)row.rank=row.smallSample?null:++rank;
 return {version:'P_OQI_v1',shrinkagePa:40,qualificationBf:20,totalPa:league.pa,
  method:'Leave-one-pitcher-out OPS relative to league (65%) and team (35%); independent PA/(PA+40) shrinkage; BF weighted; 100 is neutral. All pitcher outcomes are excluded from hitter AND reference baselines. No cross-pitcher normalization.',pitchers:rows};
}
