// Display selection only. Never feeds player rankings, forecasts or trade values.
const total=(rows,key)=>rows.reduce((n,s)=>n+(Number(s[key])||0),0);
function aflHitter(id,data){
 return (data?.statsSnapshot?.stats??[]).filter(g=>g.group?.displayName==='hitting').flatMap(g=>g.splits??[]).find(s=>String(s.player?.id)===String(id)&&String(s.season)==='2026'&&s.league?.id===119)?.stat;
}
export function doorHitterTileSample(p,samples={},afl=null){
 if(p.type!=='H')return null;
 const saved=samples.players?.[String(p.mlbamId)];
 const highest=saved?.highest??{season:2026,level:p.level,pa:total(p.levelSplits,'pa')};
 let line=saved?.display,asOf=samples.retrievedAt?.slice(0,10),isAfl=false;
 // Any recorded AFL appearance takes precedence over the regular-season sample.
 const fall=aflHitter(p.mlbamId,afl);
 if(Number(fall?.plateAppearances)>0){
  line={season:2026,level:'AFL',pa:Number(fall.plateAppearances),ab:fall.atBats,avg:fall.avg,obp:fall.obp,slg:fall.slg,hr:fall.homeRuns,sb:fall.stolenBases};
  asOf=(afl.statsRetrievedAt??afl.retrievedAt??afl.asOf)?.slice(0,10);isAfl=true;
 }
 if(!line){
  const levels=['AAA','AA','A+','A','CPX','DSL'];
  const groups=levels.map(level=>({level,rows:(p.allLevelSplits??p.levelSplits).filter(s=>s.group==='hitting'&&s.level===level)}));
  const selected=groups.find(g=>total(g.rows,'pa')>=40)??{level:p.level,rows:p.levelSplits};
  const r=selected.rows;
  // Missing raw denominators must not be replaced by averages of split rates.
  line={season:2026,level:selected.level,pa:total(r,'pa'),hr:total(r,'hr'),sb:total(r,'sb'),avg:r.length===1?r[0].avg:null,obp:r.length===1?r[0].obp:null,slg:r.length===1?r[0].slg:null};
  asOf=p.statsDate;
 }
 const rate=v=>v==null||v===''||v==='—'?'—':Number.isFinite(Number(v))?Number(v).toFixed(3).replace(/^0\./,'.'):'—';
 let note='';
 if(highest.pa<40&&(isAfl||line.season!==highest.season||line.level!==highest.level)){
  note=`${highest.season!==line.season?highest.season+' ':''}${highest.level} sample: only ${highest.pa} PA${highest.ab!=null?` (${highest.ab} AB)`:''}.`;
 }else if(line.pa<40){note=isAfl?`Small AFL sample: ${line.pa} PA.`:`Only ${line.pa} PA; no larger level sample is available.`;}
 return {line,isAfl,highest,metrics:[['AVG',rate(line.avg)],['OBP',rate(line.obp)],['SLG',rate(line.slg)]],extras:`${line.pa} PA · ${line.hr??'—'} HR · ${line.sb??'—'} SB`,caption:`${line.season} ${line.level} only · ${asOf?'stats '+asOf:'date unavailable'}`,note};
}

export function doorPitcherAflSample(p,afl){
 if(p.type!=='P')return null;
 const stat=(afl?.statsSnapshot?.stats??[]).filter(g=>g.group?.displayName==='pitching').flatMap(g=>g.splits??[]).find(s=>String(s.player?.id)===String(p.mlbamId)&&String(s.season)==='2026'&&s.league?.id===119)?.stat;
 if(!stat||!(Number(stat.battersFaced)>0||Number(stat.inningsPitched)>0))return null;
 const bf=Number(stat.battersFaced),pct=n=>bf>0?(100*n/bf).toFixed(1)+'%':'—';
 return {metrics:[['IP',stat.inningsPitched??'—'],['K − BB%',pct(Number(stat.strikeOuts??0)-Number(stat.baseOnBalls??0))],['BB%',pct(Number(stat.baseOnBalls??0))]],caption:`2026 AFL only · stats ${(afl.statsRetrievedAt??afl.retrievedAt??afl.asOf??'date unavailable').slice(0,10)}`};
}
