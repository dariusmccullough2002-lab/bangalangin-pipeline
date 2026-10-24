import {compareHorizons} from './contribution-horizon.js';
// Explain the active ledger; never estimate a second score or infer a roster need.
export const RELEASE='trade-explanation-20261024';
const finite=Number.isFinite;
const f=n=>finite(n)?n.toFixed(1):'Unavailable';
const signed=n=>finite(n)?(n>=0?'+':'')+n.toFixed(1):'Unavailable';
const sum=values=>values.every(finite)?values.reduce((a,b)=>a+b,0):null;
const change=(a,b)=>finite(a)&&finite(b)?a-b:null;
export function explainTrade({incoming,outgoing,mode,valueFor,timingFor=()=>null,range=null}){
 const row=(asset,direction)=>{
  const fit=valueFor(asset.id,mode),balanced=valueFor(asset.id,'balanced'),neutral=valueFor(asset.id,'neutral');
  const q=asset.forecast_research,timing=asset.audit?.kind==='prospect'?timingFor(asset,mode):null;
  const notes=[];const rank=asset.ranking_policy;
  if(rank&&finite(rank.source_rank))notes.push(`${rank.source_scope??'Saved source'} rank ${rank.source_rank}; neutral dynasty value ${f(neutral)}. Rankings anchor price; strategy fit uses projected contribution.`);
  if(timing)notes.push(`${timing.source.source} ETA ${timing.source.value}; the ${f(fit)} fit assumes regular-role contribution starts in ${timing.regularRoleStart??timing.source.value}. Arrival and regular playing time can differ.`);
  else if(asset.audit?.kind==='prospect')notes.push('No supported published-ETA scenario: strategy fit is unavailable. The inherited prospect production path is not used to fill this gap.');
  else if(asset.audit?.kind==='pick')notes.push('A future selection opportunity, not immediate player production. It uses no immediate roster slot; class and selection uncertainty remain.');
  else {
   if(['SP','RP'].includes(asset.audit?.role))notes.push(`The saved production forecast treats this pitcher as ${asset.audit.role==='SP'?'a starter':'a reliever'}; saved position eligibility is ${asset.position??'unavailable'}. Eligibility labels alone do not set the projected pitching role.`);
   const p=asset.audit?.projection;
   if(p&&p.AB>0&&['H','H+SP'].includes(asset.audit?.role)){
    const denom=p.AB+p.BB+p.HBP+p.SF;
    if([p.PA,p.H,p.TB,p.BB,p.HBP,p.SF,p.HR,p.SB].every(finite)&&denom>0)notes.push(`Saved first-year forecast: ${f(p.PA)} PA, ${(p.H/p.AB).toFixed(3)} AVG / ${((p.H+p.BB+p.HBP)/denom+p.TB/p.AB).toFixed(3)} OPS, ${f(p.HR)} HR and ${f(p.SB)} SB. These are projected totals before lineup displacement.`);
   }else if(p&&p.IP>0&&[p.ER,p.K,p.BB,p.H].every(finite))notes.push(`Saved first-year forecast: ${f(p.IP)} IP, ${(9*p.ER/p.IP).toFixed(2)} ERA, ${((p.H+p.BB)/p.IP).toFixed(2)} WHIP and ${f(p.K)} K. ERA is context; the league scores raw ER.`);
   if(asset.active_forecast_inputs)notes.push('The talent baseline blends multiple seasons with regression; the latest season is not assumed to repeat. Workload and the saved aging/availability path also enter contribution.');
  }
  if(q&&finite(q.contributionFactor)){
   const before=q.beforeCompetitiveValues?.[mode]?.display;
   notes.push(`Expected-quality evidence dated ${q.evidenceDate}: ${signed((q.contributionFactor-1)*100)}% contribution adjustment, shared across all strategies${finite(before)&&finite(fit)?`; ${f(before)} → ${f(fit)} ${mode} fit (${signed(fit-before)})`:''}. This bounded sensitivity is not a calibrated rebound or breakout probability.`);
  }
  return {id:asset.id,name:asset.name,direction,fit,balanced,neutral,signedFit:finite(fit)?direction*fit:null,notes};
 };
 const rows=[...incoming.map(a=>row(a,1)),...outgoing.map(a=>row(a,-1))];
 const received=sum(rows.filter(r=>r.direction===1).map(r=>r.fit)),sent=sum(rows.filter(r=>r.direction===-1).map(r=>r.fit)),net=change(received,sent);
 const balancedReceived=sum(rows.filter(r=>r.direction===1).map(r=>r.balanced)),balancedSent=sum(rows.filter(r=>r.direction===-1).map(r=>r.balanced)),balancedNet=change(balancedReceived,balancedSent);
 const neutralReceived=sum(rows.filter(r=>r.direction===1).map(r=>r.neutral)),neutralSent=sum(rows.filter(r=>r.direction===-1).map(r=>r.neutral)),neutralNet=change(neutralReceived,neutralSent);
 const complete=incoming.length>0&&outgoing.length>0&&finite(net);
 const paragraphs=[];
 if(!complete)paragraphs.push('A complete strategy score needs supported values for every selected asset. Missing evidence is not counted as zero.');
 else {
  paragraphs.push(`Under the ${mode} strategy, incoming assets total ${f(received)} fit and outgoing assets total ${f(sent)}: ${f(received)} − ${f(sent)} = ${signed(net)}. Both packages use this team's strategy. ${Math.abs(net)<.05?'The displayed base estimate is even.':net>0?'The model projects a contribution benefit for this side.':'The model projects less strategy-weighted contribution for this side.'}`);
  if(finite(balancedNet))paragraphs.push(`The same exchange scores ${signed(balancedNet)} under balanced timing. Choosing ${mode} changes that balance by ${signed(net-balancedNet)} fit. ${mode==='contender'?'Earlier modeled contribution receives more weight.':mode==='rebuild'?'Later modeled contribution receives more weight; youth or a prospect label alone earns no bonus.':'Contribution is spread across the saved forecast horizon.'}`);
  if(finite(neutralNet))paragraphs.push(`Neutral dynasty value changes by ${signed(neutralNet)} (${f(neutralReceived)} received − ${f(neutralSent)} sent). ${neutralNet*net<0?'The price and strategy signals disagree because ranking-led dynasty value and timed contribution measure different things.':'Dynasty value is a separate ledger; it is not added to the strategy score.'}`);
  const allAssets=[...incoming,...outgoing];
  if(allAssets.every(a=>a.audit?.kind==='MLB'&&a.audit.role==='H'&&a.audit.projection?.AB>0)){
   const keys=['PA','AB','H','BB','HBP','SF','TB','HR','R','RBI','SB'];
   const packageStats=assets=>Object.fromEntries(keys.map(k=>[k,sum(assets.map(a=>a.audit.projection[k]))]));
   const i=packageStats(incoming),o=packageStats(outgoing);
   if(keys.every(k=>finite(i[k])&&finite(o[k]))){
    const avg=p=>p.H/p.AB,ops=p=>(p.H+p.BB+p.HBP)/(p.AB+p.BB+p.HBP+p.SF)+p.TB/p.AB;
    paragraphs.push(`The saved first-year batting forecasts compare ${f(i.PA)} incoming PA with ${f(o.PA)} outgoing PA. Incoming minus outgoing: ${signed(i.HR-o.HR)} HR, ${signed(i.R-o.R)} R, ${signed(i.RBI-o.RBI)} RBI and ${signed(i.SB-o.SB)} SB; combined AVG ${avg(i).toFixed(3)} versus ${avg(o).toFixed(3)}, OPS ${ops(i).toFixed(3)} versus ${ops(o).toFixed(3)}. These components help explain the contribution forecast, but package totals do not establish usable lineup production or category wins.`);
   }
  }
  if(allAssets.every(a=>a.audit?.kind!=='prospect'&&a.annual_expected_utility?.length===8&&a.annual_expected_utility.every(finite))){
   const path=assets=>Array.from({length:8},(_,year)=>assets.reduce((total,a)=>total+a.annual_expected_utility[year],0));
   const i=path(incoming),o=path(outgoing),near=values=>values.slice(0,3).reduce((a,b)=>a+b,0),later=values=>values.slice(3).reduce((a,b)=>a+b,0);
   paragraphs.push(`Before applying this strategy's timing weights, saved contribution in years 1–3 totals ${f(near(i))} incoming versus ${f(near(o))} outgoing; years 4–8 total ${f(later(i))} versus ${f(later(o))}. These are underlying utility units, not dynasty points. This separates the forecast trajectory from the timing preference.`);
  }
  const positive=rows.filter(r=>finite(r.signedFit)&&r.signedFit>0).sort((a,b)=>b.signedFit-a.signedFit).slice(0,2);
  const negative=rows.filter(r=>finite(r.signedFit)&&r.signedFit<0).sort((a,b)=>a.signedFit-b.signedFit).slice(0,2);
  paragraphs.push(`Largest additions: ${positive.map(r=>`${r.name} (${signed(r.signedFit)})`).join(', ')||'none with positive supported fit'}. Largest costs: ${negative.map(r=>`${r.name} (${signed(r.signedFit)})`).join(', ')||'none with positive outgoing fit'}. The full ledger below includes every asset.`);
  if(range&&[range.low,range.high].every(finite))paragraphs.push(`Tested strategy range: ${signed(range.low)} to ${signed(range.high)}. ${range.low<0&&range.high>0?'The result can reverse under tested assumptions, so the base score is not a firm verdict.':'The tested range stays on one side of zero; it does not cover every possible outcome.'} This is a scenario envelope, not a confidence interval.`);
 }
 const horizon=compareHorizons(incoming,outgoing,timingFor);
 const summary=[];
 if(!complete)summary.push("There isn't enough information to judge this trade yet. Some of the selected players or picks are missing a supported forecast.");
 else {
  const plan=mode==='contender'?'prioritizing earlier production across the next eight years':mode==='rebuild'?'building for the future':'balancing this season with the future';
  const names=assets=>assets.length===1?assets[0].name:assets.length===2?assets.map(a=>a.name).join(' and '):'the package led by '+[...assets].sort((a,b)=>(valueFor(b.id,mode)??0)-(valueFor(a.id,mode)??0))[0].name;
  const inc=names(incoming),out=names(outgoing);
  if(mode==='contender'){
   if(!horizon.complete)summary.push('The calculator cannot compare next-season production for every asset in this trade. The longer-term score does not fill that gap.');
   else if(Math.abs(horizon.nextSeason.net)<.000001)summary.push('The saved projections show similar production next season from what you receive and what you give up.');
   else summary.push(horizon.nextSeason.net>0?`For next season, the saved projections favor receiving ${inc} over keeping ${out}.`:`For next season, the saved projections favor keeping ${out} over receiving ${inc}.`);
   if(horizon.complete&&Math.abs(net)>.05&&net*horizon.nextSeason.net<0)summary.push(`The longer-term score leans the other way: it favors ${net>0?inc:out} when later seasons are included. That is a future-value tradeoff, not evidence of more help next season.`);
   else summary.push('The separate strategy score includes eight years of production. It is not a prediction of next season’s standings or your actual lineup improvement.');
  }else {
  summary.push(Math.abs(net)<.05?`For a team focused on ${plan}, the calculator sees little difference between what you receive and what you give up.`:net>0?`For a team focused on ${plan}, the calculator leans toward taking ${inc}. It expects that return to help your plan more than keeping ${out}.`:`For a team focused on ${plan}, the calculator leans toward keeping ${out}. It expects more help from what you're giving up than from ${inc}.`);
   summary.push('This preference includes production over the next eight years. The next-season outlook above shows the shorter-term tradeoff.');
  }
  // A direct hitter comparison gives concrete reasons without a second scoring model.
  const i=incoming[0],o=outgoing[0],ip=i?.audit?.projection,op=o?.audit?.projection;
  if(incoming.length===1&&outgoing.length===1&&[i,o].every(a=>a.audit?.kind==='MLB'&&a.audit.role==='H')&&ip?.AB>0&&op?.AB>0){
   const measures=[['home runs',ip.HR,op.HR],['runs scored',ip.R,op.R],['runs batted in',ip.RBI,op.RBI],['stolen bases',ip.SB,op.SB],['batting average',ip.H/ip.AB,op.H/op.AB]];
   const better=measures.filter(([,a,b])=>finite(a)&&finite(b)&&a>b).map(([label])=>label),worse=measures.filter(([,a,b])=>finite(a)&&finite(b)&&a<b).map(([label])=>label);
   const join=items=>items.length<2?items[0]:items.slice(0,-1).join(', ')+' and '+items.at(-1);
   if(better.length&&worse.length)summary.push(`The forecast gives ${i.name} the edge in ${join(better)}, while ${o.name} leads in ${join(worse)}. Those are expectations for next season, not a ranking of who played better last year.`);
  }
  if(finite(neutralNet)&&Math.abs(neutralNet)>.05)summary.push(neutralNet>0?"On the separate dynasty rankings, you would receive more overall asset value than you give up.":"On the separate dynasty rankings, you would give up more overall asset value than you receive.");
  const future=[...incoming,...outgoing].filter(a=>a.audit?.kind==='prospect'||a.audit?.kind==='pick');
  if(future.length)summary.push('Part of this trade depends on future help from prospects or draft picks. Their value does not mean they are ready to improve your lineup now. Any next-season comparison involving a prospect depends on the saved arrival assumptions.');
  if(mode==='contender'&&horizon.complete)summary.push('This compares projected production before fitting players into your lineup. Actual playing opportunities can change the benefit.');
  if(range&&finite(range.low)&&finite(range.high)&&range.low<0&&range.high>0)summary.push("The longer-term result can favor the other side when forecast assumptions change.");
 }
 return {release:RELEASE,mode,complete,received,sent,net,balancedNet,neutralNet,rows,paragraphs,summary,horizon,range};
}
export function renderPlainSummary(doc,explanation,owner){
 const section=doc.createElement('section');section.className='trade-plain-summary';
 const title=doc.createElement('h3');title.textContent=owner;section.append(title);
 for(const text of explanation.summary){const p=doc.createElement('p');p.textContent=text;section.append(p);}
 return section;
}
export function renderExplanation(doc,explanation,owner){
 const make=(tag,text,cls)=>{const e=doc.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
 const section=make('section',undefined,'trade-reasoning-team');section.append(make('h3',`${owner} · eight-year score ${signed(explanation.net)}`));
 const h=explanation.horizon;section.append(make('h4',`${h.forecastYear} production comparison`));
 if(h.complete)section.append(make('p',`Next season: ${f(h.nextSeason.received)} received − ${f(h.nextSeason.sent)} sent = ${signed(h.nextSeason.net)} annual contribution units. First three years: ${signed(h.firstThreeYears.net)}; later years: ${signed(h.laterYears.net)}. These are not the eight-year display score or dynasty-value points.`));else section.append(make('p','Next-season comparison unavailable: missing production or calendar-aligned timing evidence is not zero.'));
 section.append(make('p',h.limits));
 for(const r of h.rows)section.append(make('p',`${r.name}: ${r.annual?f(r.annual[0]):'Unavailable'} next-season units. ${r.reason}`));
 for(const text of explanation.paragraphs)section.append(make('p',text));
 const wrap=make('div',undefined,'trade-ledger-wrap');wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label',owner+' score calculation');const table=make('table');const head=make('thead'),tr=make('tr');for(const label of ['Asset','Direction','Strategy fit','Dynasty value']){const th=make('th',label);th.scope='col';tr.append(th);}head.append(tr);table.append(head);const body=make('tbody');for(const r of explanation.rows){const row=make('tr');row.append(make('th',r.name),make('td',r.direction===1?'Receives':'Sends'),make('td',signed(r.signedFit)),make('td',f(r.neutral)));row.firstChild.scope='row';body.append(row);}table.append(body);wrap.append(table);section.append(wrap,make('p','Displayed rows are rounded; the net uses full precision. Dynasty values in the last column are asset prices, not extra fit points.','trade-explanation-note'));
 const details=make('details',undefined,'trade-player-evidence');details.append(make('summary','Player evidence and forecast assumptions'));for(const row of explanation.rows){details.append(make('h4',row.name));for(const note of row.notes)details.append(make('p',note));if(!row.notes.length)details.append(make('p','No additional supported forecast detail is available for this asset. The score above comes from the active saved ledger.'));}section.append(details);return section;
}
