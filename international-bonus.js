// Only dedicated bonus fields are read; historical agreements in scouting text
// must not silently replace the current reported expectation.
export function internationalBonus(player){
 const verified=player.signingBonus;
 if(typeof verified==='number'&&Number.isFinite(verified)&&verified>0)
  return {amount:verified,label:format(verified),detail:'Verified signing bonus'};
 const raw=player.reportedBonusExpectation;
 if(typeof raw!=='string')return {amount:null,label:'TBD',detail:'Bonus amount not reported'};
 const match=raw.match(/\$\s*([\d,]+(?:\.\d+)?)\s*(million|thousand|m\b|k\b)?/i);
 if(!match)return {amount:null,label:'TBD',detail:raw};
 const unit=(match[2]??'').toLowerCase();
 const amount=Number(match[1].replaceAll(',',''))*(unit==='m'||unit==='million'?1e6:unit==='k'||unit==='thousand'?1e3:1);
 if(!Number.isFinite(amount)||amount<=0)return {amount:null,label:'TBD',detail:raw};
 const prefix=raw.slice(0,match.index);
 const qualifier=/more than|over|>/i.test(prefix)?'>':/less than|under|</i.test(prefix)?'<':/approximately|approx\.?|roughly|about|≈|~/i.test(prefix)?'≈ ':'';
 return {amount,label:qualifier+format(amount),detail:`Reported bonus expectation, not a verified paid amount: ${raw}`};
}
function format(amount){
 return '$'+(amount>=1e6?`${Number((amount/1e6).toFixed(3))}M`:amount>=1e3?`${Number((amount/1e3).toFixed(3))}K`:amount.toLocaleString('en-US'));
}
export function compareInternationalBonuses(a,b,direction='desc'){
 const first=internationalBonus(a).amount,second=internationalBonus(b).amount;
 const rank=(a.pipelineRank??10000)-(b.pipelineRank??10000);
 if(first===null)return second===null?rank:1;
 if(second===null)return -1;
 return (direction==='asc'?first-second:second-first)||rank;
}
