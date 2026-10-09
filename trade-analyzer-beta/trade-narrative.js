// Read-only explanation layer: scores, projections and identity remain in V2.3C.
const list=names=>names.length<2?names[0]??'the package':names.length===2?names.join(' and '):names.slice(0,-1).join(', ')+', and '+names.at(-1);
const value=a=>a?.values?.neutral?.display??-Infinity;
const ordered=assets=>[...assets].sort((a,b)=>value(b)-value(a));
const lead=assets=>list(ordered(assets).slice(0,2).map(a=>a.name))+(assets.length>2?` and ${assets.length-2} other assets`:'');
export const assetKind=a=>a?.audit?.kind==='pick'?'pick':a?.audit?.kind==='prospect'?'prospect':a?.audit?.kind==='hybrid'?'limited MLB':a?.audit?.kind==='MLB'?'MLB':'unknown';
const age=a=>a?.career_profile?.age??a?.prospect_evidence?.saved_age;
const future=a=>['pick','prospect'].includes(assetKind(a));
const role=a=>a?.audit?.role;
export function tradeNarrative({owner,strategy,incoming=[],outgoing=[],fit,range,assessment='',otherFit,otherStrategy,nearChange,etas={}}){
 if(!incoming.length||!outgoing.length)return 'Build both packages to explain the exchange.';
 const received=ordered(incoming),sent=ordered(outgoing),anchor=received[0];
 const inFuture=incoming.every(future),outFuture=outgoing.every(future),inMLB=incoming.every(a=>assetKind(a)==='MLB'),outMLB=outgoing.every(a=>assetKind(a)==='MLB');
 const sentences=[];
 if(inMLB&&outFuture)sentences.push(`${owner} exchanges ${lead(sent)} for ${lead(received)}, shifting from development and draft opportunities toward players with recorded MLB contributions.`);
 else if(inFuture&&outMLB)sentences.push(`${owner} converts ${lead(sent)} into ${lead(received)}, accepting development and arrival risk instead of relying on the outgoing MLB production.`);
 else if(received.length<sent.length)sentences.push(`${owner} consolidates ${sent.length} assets, led by ${lead(sent)}, into ${lead(received)}. Fewer incoming assets concentrate the outcome in fewer players or selections.`);
 else if(received.length>sent.length)sentences.push(`${owner} spreads the value of ${lead(sent)} across ${lead(received)}. More assets create additional development or roster decisions; quantity alone does not replace the best outgoing player.`);
 else if(incoming.some(a=>role(a)==='SP')&&outgoing.some(a=>role(a)==='H'))sentences.push(`${owner} sends ${lead(sent)} for ${lead(received)}, shifting part of the package from hitting toward starting pitching; innings, strikeouts and QA3 are relevant, but a rotation need is not verified.`);
 else sentences.push(`${owner} exchanges ${lead(sent)} for ${lead(received)}, trading one mix of contribution and uncertainty for another.`);
 if(strategy==='contender')sentences.push(inFuture?'For a contender, this return is a future bet rather than verified immediate MLB help.':'The contender view emphasizes earlier modeled contribution; listed MLB status does not guarantee playing time.');
 else if(strategy==='rebuild')sentences.push(inFuture?'The rebuilding view places more emphasis on future contribution, while prospects and picks still require development before helping an MLB lineup.':`The rebuilding view still receives MLB experience${Number.isFinite(age(anchor))?`—${anchor.name} is ${age(anchor)} in the saved snapshot`:''}; later contribution matters more than current roster labels.`);
 else sentences.push('The balanced view weighs contribution across the forecast horizon rather than choosing only immediate output or distant upside.');
 const prospect=received.find(a=>assetKind(a)==='prospect');
 const pick=received.find(a=>assetKind(a)==='pick');
 if(prospect){const e=etas[prospect.id];sentences.push(`${prospect.name}${prospect.position?` is listed at ${prospect.position}`:' has a prospect development path'}${e?.value?`; the saved ${e.source} ETA is ${e.value}`:'; no independently dated arrival estimate is available here'}. Arrival and productive MLB playing time are separate questions.`);}
 else if(pick)sentences.push(`${pick.name} buys a selection opportunity, not an identified MLB contributor; class strength and who remains available can change the outcome.`);
 else if(Number.isFinite(nearChange))sentences.push(`The existing forecast shows ${Math.abs(nearChange).toFixed(1)} ${nearChange>=0?'more':'fewer'} underlying contribution units over the first three years; this is a projection, not verified lineup improvement.`);
 if(Number.isFinite(fit)&&!assessment.includes('Incomplete')){
  const crosses=range&&range.low<0&&range.high>0;
  sentences.push(`${fit>0?'The base strategy estimate supports':fit<0?'The base strategy estimate works against':'The base strategy estimate is even for'} this side (${fit>=0?'+':''}${fit.toFixed(1)} fit)${crosses?', although tested assumptions reverse the sign':'; the tested range should guide how firmly to read it'}.`);
  if(Number.isFinite(otherFit)&&strategy!==otherStrategy)sentences.push(fit>0&&otherFit>0?'Different timing preferences produce positive base fit estimates for both organizations; the uncertainty ranges still matter.':`The other organization uses ${otherStrategy} priorities; different objectives do not automatically make both sides winners.`);
 }else sentences.push('Missing valuation evidence prevents a complete numerical verdict.');
 if(incoming.length!==outgoing.length)sentences.push('Legal roster capacity and acquisition prices are unverified.');
 else sentences.push('Neither the fit score nor neutral value establishes an actual acquisition price or a verified roster need.');
 return sentences.join(' ');
}
