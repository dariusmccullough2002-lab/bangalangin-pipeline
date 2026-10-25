// Evidence review only. No asset prices, forecasts, roster assignments or strategy scores are changed.
const finite=Number.isFinite;
export function assetReview(a,registry={},floor=null){
 const player=a.audit?.kind!=='pick',p=a.values?.neutral?.display,rp=a.ranking_policy,prior=registry.players?.[a.id]?.prospectEvidence??a.prospect_evidence?.snapshot??null;
 const observed=a.career_profile?.available_seasons??a.audit?.projection_audit?.observed_years??[];
 const reasons=[];
 if(player&&!rp){reasons.push('No saved dynasty-ranking anchor; this is a production-based estimate.');if(finite(floor)&&finite(p)&&p>floor)reasons.push('Estimate exceeds the lowest saved ranked-player value; review ranking coverage and price scale.');if(prior)reasons.push('Archived prospect evidence exists and needs continuity review.');if(observed.length>0&&observed.length<=2)reasons.push('Limited MLB history; absence from a ranking is not evidence of a low ceiling.');if(p===0)reasons.push('Zero modeled production surplus does not establish zero dynasty trade value.');}
 return {id:a.id,name:a.name,source:!player?'pick-selection policy':rp?.source_scope??'production-only',rankingAnchored:!!rp,price:p,rankedFloor:floor,aboveRankedFloor:player&&!rp&&finite(floor)&&finite(p)&&p>floor,recentUnranked:player&&!rp&&observed.length>0&&observed.length<=2,archivedProspectEvidence:!!prior,review:reasons.length>0,reasons};
}
export function reviewCatalog(data,registry={}){const ranked=data.assets.filter(a=>a.audit?.kind!=='pick'&&a.ranking_policy&&finite(a.values?.neutral?.display)),floor=ranked.length?Math.min(...ranked.map(a=>a.values.neutral.display)):null;return {release:'valuation-review-20261024',priceBaselineUnchanged:true,floor,assets:Object.fromEntries(data.assets.map(a=>[a.id,assetReview(a,registry,floor)]))};}
export function packageReview(data,state,review){
 const byId=new Map(data.assets.map(a=>[a.id,a])),ids=state.sides.flat(),messages=[];
 const rows=ids.map(id=>review.assets[id]).filter(Boolean),unanchored=rows.filter(r=>r.source==='production-only');
 if(unanchored.length)messages.push('Price review needed: '+unanchored.map(a=>a.name).join(', ')+'. These estimates use production rather than a saved dynasty ranking. Their prices have not been shown to match the ranking-based scale.');
 const zero=unanchored.filter(a=>a.price===0);if(zero.length)messages.push('A displayed zero for '+zero.map(a=>a.name).join(', ')+' means no modeled production surplus; it does not establish that the player has no trade value.');
 const counts=state.sides.map(side=>side.filter(id=>byId.get(id)?.audit?.kind!=='pick').length);
 const totals=state.sides.map(side=>{const vals=side.map(id=>byId.get(id)?.values?.neutral?.display);return vals.every(finite)?vals.reduce((a,b)=>a+b,0):null;});
 const unequal=counts[0]!==counts[1]&&Math.max(...counts)>=2;
 const near=totals.every(finite)&&Math.abs(totals[0]-totals[1])<=Math.max(2,.1*(totals[0]+totals[1])/2);
 if(state.sides.every(s=>s.length)&&unequal&&near)messages.push('Close package trade: adding player prices can overstate the usefulness of the larger return. Check playing opportunities, replacements and roster-space sensitivity before treating this as even. No automatic package penalty has been applied.');
 return {release:review.release,playerCounts:counts,neutralTotals:totals,nearEvenThresholdPolicy:'max(2 points, 10% of mean package price); warning policy, not a validated fairness threshold',closeUnevenPackage:unequal&&near,unanchoredAssetIds:unanchored.map(a=>a.id),messages,priceBaselineUnchanged:true};
}
export function renderReview(doc,report){const section=doc.createElement('section');section.className='trade-price-review';section.setAttribute('aria-label','Trade value review');section.hidden=!report.messages.length;if(section.hidden)return section;const h=doc.createElement('h3');h.textContent='Before using these values';section.append(h);for(const text of report.messages){const p=doc.createElement('p');p.textContent=text;section.append(p);}return section;}
