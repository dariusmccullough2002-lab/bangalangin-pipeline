// Shared policy sensitivity, separate from actual cuts, fit utility and base prices.
export function evaluateSpaceSensitivity(data,evidence,state,costs){
 if(![costs.active,costs.minors].every(x=>Number.isFinite(x)&&x>=0&&x<=20))return {status:'blocked',reason:'Enter costs from 0 to 20 points.'};
 const catalog=new Map(data.assets.map(a=>[a.id,a])),seen=new Set(),packages=[];
 if(!state.sides.every(s=>s.length))return{status:'empty',reason:'Add assets to both sides to compare shared space costs.'};
 for(const ids of state.sides){const rows=[];for(const id of ids){const a=catalog.get(id),identity=a?.playerIdentity??id;if(!a||seen.has(identity))return{status:'blocked',reason:'Missing or duplicate asset identity.'};seen.add(identity);const price=a.values?.neutral?.display;if(!Number.isFinite(price)||price<0)return{status:'blocked',reason:'An asset has no supported neutral price.'};
 const pick=a.audit?.kind==='pick',eligible=evidence.players[id]?.minorsEligible,bucket=pick?'pick':eligible===true?'minors':'active/reserve',assumed=!pick&&eligible==null;
 const allowance=pick?0:Math.min(price,bucket==='minors'?costs.minors:costs.active);rows.push({id,name:a.name,price,bucket,assumed,allowance,adjusted:price-allowance});}packages.push(rows);}
 const totals=packages.map(rows=>({price:rows.reduce((s,a)=>s+a.price,0),allowance:rows.reduce((s,a)=>s+a.allowance,0)}));
 return {status:'ready',costs:{...costs},policy:'Shared capacity allowance; price-capped player cost; no immediate pick cost; alternative to actual-drop ledger.',packages,results:totals.map((out,i)=>{const incoming=totals[1-i],gross=incoming.price-out.price,adjustment=out.allowance-incoming.allowance;return{team:state.teams[i],gross,adjustment,adjusted:gross+adjustment};})};
}
export function mountSpaceSensitivity(data,evidence,anchor){
 const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;},fmt=x=>(x>=0?'+':'')+x.toFixed(1);
 const panel=el('section',undefined,'neutral-summary space-sensitivity');anchor.before(panel);
 const header=el('div',undefined,'space-heading');header.append(el('span','EXPLORE THE TRADE','space-kicker'),el('h2','Roster-space sensitivity'),el('p','What is the flexibility of an extra player spot worth? Compare assumptions without changing base prices or strategy fit.'));panel.append(header);
 const layout=el('div',undefined,'space-layout'),work=el('div',undefined,'space-workbench'),guide=el('aside',undefined,'space-guide');guide.setAttribute('aria-label','Roster-space cost guide from zero to six');layout.append(work,guide);panel.append(layout);
 guide.append(el('span','0–6 POINT GUIDE','space-kicker'),el('h3','Choose an assumption'),el('p','Illustrative levels, not measured slot prices. Apply the same assumption to both teams.'));
 const levels=[['Baseline','Ignore space cost; compare the original asset values.'],['Minimal','Little value assigned to preserving an open spot.'],['Low','A small allowance for future pickups or roster moves.'],['Moderate','Useful flexibility; alternatives are worth considering.'],['Meaningful','Carrying an extra player may block a useful addition.'],['High','Give substantial weight to keeping space for alternatives.'],['Very high','A strong flexibility assumption; check whether it drives the verdict.']];
 const list=el('ol',undefined,'space-scale');list.start=0;levels.forEach(([name,description],i)=>{const li=el('li'),badge=el('span',String(i),'space-level');li.append(badge);const copy=el('div');copy.append(el('strong',name),el('span',description));li.append(copy);list.append(li);});guide.append(list,el('p','Compare 0, 2, 4 and 6. If the verdict flips, the trade depends on your space-cost assumption. Values above 6 are additional stress tests.','space-guide-tip'));
 const controls=el('div',undefined,'space-controls'),inputs={};
 for(const [key,text,hint]of [['active','Active / reserve space cost','For players using an active or bench spot.'],['minors','Minors space cost','For players with saved minors eligibility.']]){const label=el('label');label.append(el('span',text+' (points)'));const input=el('input');input.type='number';input.min='0';input.max='20';input.step='.5';input.value='0';input.setAttribute('aria-label',text);label.append(input,el('small',hint));controls.append(label);inputs[key]=input;}
 const reset=el('button','Reset to zero','space-reset');reset.type='button';controls.append(reset);work.append(controls);
 const output=el('div');output.setAttribute('aria-live','polite');work.append(output);
 const note=el('p','This is a shared flexibility assumption, not a measure of either team’s urgency. Picks have no immediate player-space cost.','space-policy-note');work.append(note);
 let state=null,result=null;
 function render(){if(!state)return;const cost=k=>inputs[k].value.trim()===''?NaN:Number(inputs[k].value);result=evaluateSpaceSensitivity(data,evidence,state,{active:cost('active'),minors:cost('minors')});output.replaceChildren();if(result.status!=='ready'){output.append(el('p',result.reason,'space-empty'));return;}
 const grid=el('div',undefined,'space-results');for(const r of result.results){const card=el('section',undefined,'space-result');card.append(el('h3',r.team),el('span','Adjusted asset balance','space-metric-label'),el('strong',fmt(r.adjusted),'space-metric'));const ledger=el('dl',undefined,'space-ledger');for(const [label,value]of [['Base balance',r.gross],['Space adjustment',r.adjustment]]){const row=el('div');row.append(el('dt',label),el('dd',fmt(value)));ledger.append(row);}card.append(ledger);grid.append(card);}output.append(grid);
 const details=el('details',undefined,'space-breakdown');details.append(el('summary','Player allowances and assumptions'),el('p','Known minors eligibility uses the minors setting. Unknown eligibility uses active/reserve cost. Each allowance is capped at the player’s price, so a disposable throw-in can contribute zero.'));
 result.packages.forEach((rows,i)=>{details.append(el('h4',state.teams[i]+' sends'));const list=el('ul');for(const a of rows)list.append(el('li',a.name+' · '+a.bucket+(a.assumed?' (assumed; eligibility unverified)':'')+' · allowance '+a.allowance.toFixed(1)+' · adjusted value '+a.adjusted.toFixed(1)));details.append(list);});output.append(details);
 }
 const footer=el('p','Read this as an alternative to the actual-drop calculation below. Do not add the two adjustments together.','space-footnote');panel.append(footer);
 for(const input of Object.values(inputs))input.addEventListener('input',render);reset.addEventListener('click',()=>{for(const i of Object.values(inputs))i.value='0';render();});
 return {render(next){state=next;render();},export(){return result;}};
}
