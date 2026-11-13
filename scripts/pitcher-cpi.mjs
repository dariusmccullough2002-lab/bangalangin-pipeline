const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const round=v=>Number(v.toFixed(3));
const shape=[['filth_plus',.60],['whiff_pct',.20],['csw_pct',.12],['chase_pct',.08]];
const weights={pitchQuality:.65,kMinusBB:.25,era:.10};
const zFunction=values=>{
 const mean=values.reduce((a,b)=>a+b,0)/values.length;
 const sd=Math.sqrt(values.reduce((sum,v)=>sum+(v-mean)**2,0)/values.length);
 return v=>sd>0?clamp((v-mean)/sd,-3,3):0;
};
export function calculateCpi(pitch,officialRows,opponentData){
 const sources=new Map(pitch.map(p=>[p.pitcher_id,p]));
 const official=new Map(officialRows.map(r=>[r.player.id,r.stat]));
 const rows=opponentData.pitchers.map(opponent=>{
  const source=sources.get(opponent.mlbamId),stat=official.get(opponent.mlbamId);
  const bf=Number(stat?.battersFaced),outs=Number(stat?.outs),er=Number(stat?.earnedRuns);
  const usable=source&&shape.every(([k])=>Number.isFinite(source[k]))&&Number.isFinite(source.pitches)&&source.pitches>0&&bf>0&&outs>0&&Number.isFinite(er)&&Number.isFinite(stat.strikeOuts)&&Number.isFinite(stat.baseOnBalls);
  if(!usable)return {...opponent,cpi:null,cpiRank:null,qualityIndex:null,missingInputs:true,reason:'Complete pitch-quality and official results inputs required'};
  return {...opponent,source,officialBf:bf,outs,earnedRuns:er,era:27*er/outs,kMinusBB:(stat.strikeOuts-stat.baseOnBalls)/bf,
   pitches:source.pitches,filthPlus:source.filth_plus,smallSample:bf<20||source.pitches<50,missingInputs:false};
 });
 const eligible=rows.filter(r=>!r.missingInputs),reference=eligible.filter(r=>!r.smallSample);
 if(reference.length<2)throw Error('CPI+ needs at least two qualified pitchers');
 const shapeZ=shape.map(([key,weight])=>({key,weight,z:zFunction(reference.map(r=>r.source[key]))}));
 const kbbZ=zFunction(reference.map(r=>r.kMinusBB)),eraZ=zFunction(reference.map(r=>-r.era));
 for(const row of eligible){
  const quality=shapeZ.reduce((sum,c)=>sum+c.weight*c.z(row.source[c.key]),0)*row.pitches/(row.pitches+150);
  const kbb=kbbZ(row.kMinusBB)*row.officialBf/(row.officialBf+40);
  const era=eraZ(-row.era)*row.outs/(row.outs+45);
  const opposition=clamp((row.oqi-100)*.20,-3,3)*row.bf/(row.bf+40);
  row.components={pitchQuality:15*weights.pitchQuality*quality,kMinusBB:15*weights.kMinusBB*kbb,era:15*weights.era*era,opposition};
  row.qualityIndex=round(100+15*quality);
  row.rawCpi=100+Object.values(row.components).reduce((a,b)=>a+b,0);
 }
 // A display centering constant only: it never enters leave-pitcher-out OQI.
 const offset=reference.reduce((sum,r)=>sum+r.rawCpi,0)/reference.length-100;
 for(const row of rows){
  if(!row.missingInputs){row.cpi=round(row.rawCpi-offset);row.era=round(row.era);row.kMinusBB=round(100*row.kMinusBB);row.components=Object.fromEntries(Object.entries(row.components).map(([k,v])=>[k,round(v)]));delete row.rawCpi;}
  delete row.source;
 }
 rows.sort((a,b)=>(b.cpi??-Infinity)-(a.cpi??-Infinity)||b.bf-a.bf||a.mlbamId-b.mlbamId);
 let rank=0;for(const row of rows)row.cpiRank=row.smallSample||row.missingInputs?null:++rank;
 return {version:'CPI_v1',name:'Contextual Pitching Index',weights,shapeWeights:Object.fromEntries(shape),centeringOffset:round(offset),
  sampleRegression:{pitches:150,battersFaced:40,outs:45},qualification:{battersFaced:20,pitches:50},
  method:'65% pitch quality + 25% K−BB% + 10% inverse ERA, sample-regressed and standardized; bounded leave-pitcher-out batter-quality adjustment. Qualified cohort centered at 100. Filth+ is not renamed Stuff+.',
  pitchers:rows};
}
