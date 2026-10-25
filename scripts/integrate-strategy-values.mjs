import fs from 'node:fs';
// Rewrite executable hooks only. Catalog and embedded historical source documents stay intact.
export function integrateStrategyValues(path){
 let html=fs.readFileSync(path,'utf8');const match=html.match(/script\.textContent\s*=\s*("(?:[^"\\]|\\.)*")/);if(!match)throw Error('Strategy integration script missing');let code=JSON.parse(match[1]);
 const split=code.indexOf('const previewDocuments=');if(split<0)throw Error('Archived documents boundary missing');let live=code.slice(0,split);const archive=code.slice(split);
 const replace=(old,next)=>{if(!live.includes(old))throw Error('Strategy integration hook missing: '+old.slice(0,90));live=live.replaceAll(old,next);};
 const val=live.match(/function val\(id,mode\)\{[^\n]+/)[0];replace(val,"function val(id,mode){return window.PipelineStrategyValues?.value(id,mode)??null}");
 const stats=live.match(/function stats\(ids,mode\)\{[^\n]+/)[0];replace(stats,"function stats(ids,mode){let total=0,lo=0,hi=0,missing=[];for(const id of ids){const a=catalog.get(id),v=val(id,mode),r=window.PipelineStrategyValues?.bounds(id,mode);if(v===null||!r){missing.push(a.name);continue}total+=v;lo+=r.low;hi+=r.high;}return{total,lo,hi,missing}}");
 replace("a.audit.kind==='prospect'?(val(id,state.modes[side])===null?'fit unavailable · published timing missing':fmt(val(id,state.modes[side]))+' conditional '+state.modes[side]+' fit'):fmt(val(id,state.modes[side]))+' '+state.modes[side]+' fit'","fmt(val(id,state.modes[side]))+' '+state.modes[side]+' adjusted value'");
 replace("competitive-fit change","strategy-value change");
 replace("Competitive fit unavailable for complete trade","Strategy value unavailable for complete trade");
 replace("' outgoing competitive fit'","' outgoing adjusted value'");
 replace("Competitive fit · separate from price","Strategy-adjusted asset value");
 replace("mode+' competitive fit'","mode+' adjusted value'");
 replace("Scenario envelope ","Value assumption range ");
 replace("tested assumptions","price and timing assumptions");
 replace("' Competitive fit: '","' Strategy-adjusted value: '");
 const metric=live.match(/m==='neutral'&&a\.ranking_policy\?'Ranking-led value[^\n]+?(?=\)\);metrics\.append)/);
 if(!metric)throw Error('Strategy detail metric hook missing');
 replace(metric[0],"m==='neutral'?'Neutral asset price':window.PipelineStrategyValues.note(a,m)");
 const rangeStart="if(a.audit.kind!=='prospect')body.append(el('p','subtle','Assumption range under '";
 const rangeAt=live.indexOf(rangeStart);if(rangeAt<0)throw Error('Detail range hook missing');const rangeEnd=live.indexOf('\n',rangeAt);
 live=live.slice(0,rangeAt)+"const adjustedRange=window.PipelineStrategyValues.bounds(id,mode);if(adjustedRange)body.append(el('p','subtle','Value assumption range: '+fmt(adjustedRange.low)+' to '+fmt(adjustedRange.high)+'. Saved neutral-price range plus the permitted timing sensitivity; not a confidence interval.'));"+live.slice(rangeEnd);
 const rowAt=live.indexOf("['Competitive fit',");const rowEnd=live.indexOf("],['Roster-specific marginal utility'",rowAt);if(rowAt<0||rowEnd<0)throw Error('Detail strategy row hook missing');live=live.slice(0,rowAt)+"['Strategy-adjusted asset value',fmt(val(id,mode))+' · neutral price plus bounded timing preference'"+live.slice(rowEnd);
 replace("['Future annual time discount',a.competitive_values[mode]?.annual_time_discount??'unavailable']","['Strategy policy','Smooth timing preference; maximum ±10% of each asset price']");
 const why=/const explanation=\$\('why'\+side\);if\(hasBoth&&!sameTeam\)\{[^\n]+?else explanation\.textContent='';/;
 if(!why.test(live))throw Error('Old production narrative hook missing');live=live.replace(why,"const explanation=$('why'+side);explanation.textContent=hasBoth&&!sameTeam?'Neutral asset-price change '+fmt(fundamentalNet)+'; timing adjustment '+fmt(net-fundamentalNet)+'; strategy-adjusted change '+fmt(net)+'. Maximum timing adjustment is ±10% per asset. Production diagnostics and roster costs remain separate.':'';");
 const exportAt=live.indexOf('assets:state.sides.map(ids=>ids.map(id=>{');const exportEnd=live.indexOf(',warnings:DATA.warnings',exportAt);if(exportAt<0||exportEnd<0)throw Error('Asset export hook missing');live=live.slice(0,exportAt)+"assets:state.sides.map(ids=>ids.map(id=>window.PipelineStrategyValues.exportAsset(catalog.get(id))))"+live.slice(exportEnd);
 replace('model:DATA.version,','model:window.PipelineStrategyValues.release,baseModel:DATA.version,strategyPolicy:window.PipelineStrategyValues.policy,');
 replace("V2.3C identity-prior guard candidate · player snapshot ","Neutral-anchored strategy · smooth 10% limit · player snapshot ");
 replace(". No production connection.",". Saved ownership; live roster completeness unverified.");
 return finish();
 function finish(){html=html.replace(match[1],JSON.stringify(live+archive));const init='DATA=JSON.parse(await new Response(stream).text());';if(!html.includes(init))throw Error('Strategy bootstrap hook missing');html=html.replace(init,init+"const strategyValues=await import('/trade-analyzer-beta/strategy-values.js');window.PipelineStrategyValues=strategyValues.installStrategyValues(DATA,(a,m)=>window.PipelineProspectTiming?.timingEstimate(a,m)??null);");const updates=[
 ["V2.3E · BETA","V2.4 · BETA"],
 ["DYNASTY TRADE ANALYZER · V2.3E ranking-led dynasty values","DYNASTY TRADE ANALYZER · V2.4 neutral-anchored strategies"],
 ["Listed prospects retain ranking-led dynasty values after debut. Expected contribution and strategy fit remain separate; other assets retain the existing model scale.","Neutral asset prices set the baseline. Contender and rebuild apply a smooth timing adjustment limited to 10% per asset; balanced preserves neutral prices. Prices without a ranking anchor remain provisional."],
 ["Unavailable future estimates will block a complete verdict rather than count as zero.","Missing timing evidence retains neutral asset value with a warning; missing asset prices block a complete verdict."],
 ["Neutral asset value stays unchanged when strategy changes. Competitive fit is a separate timing score. Market/acquisition prices are unestimated; rankings are evidence, not point bonuses.","Neutral asset value stays unchanged when strategy changes. The displayed strategy-adjusted value adds a bounded timing preference to that price. Raw production is a separate diagnostic. Market prices remain uncalibrated."]
 ];for(const [old,next] of updates){if(!html.includes(old))throw Error('Strategy page copy hook missing: '+old.slice(0,50));html=html.replace(old,next);}fs.writeFileSync(path,html);}
}
