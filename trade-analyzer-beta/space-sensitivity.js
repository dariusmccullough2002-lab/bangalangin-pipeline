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
 const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;},fmt=x=>(x>=0?'+':'')+x.toFixed(1);
 const panel=el('section');panel.className='neutral-summary space-sensitivity';anchor.before(panel);panel.append(el('h2','Roster-space sensitivity'),el('p','Explore a shared cost for carrying players. Zero is the starting assumption; these costs are not calibrated. Base prices and strategy fit stay unchanged.'));
 const controls=el('div');controls.className='space-controls';const inputs={};
 for(const [key,text]of [['active','Active / reserve space cost'],['minors','Minors space cost']]){const label=el('label',text+' (points)');const input=el('input');input.type='number';input.min='0';input.max='20';input.step='.5';input.value='0';input.setAttribute('aria-label',text);label.append(input);controls.append(label);inputs[key]=input;}
 const reset=el('button','Reset space costs');reset.type='button';controls.append(reset);panel.append(controls);
 const output=el('div');output.setAttribute('aria-live','polite');panel.append(output,el('p','Picks use no immediate space. Minors eligibility follows saved evidence; unknown eligibility uses active/reserve cost. Each player’s allowance is capped at their price, allowing a disposable throw-in to contribute zero. This is an alternative to the actual-drop calculation below; do not add the two adjustments together.'));
 let state=null,result=null;
 function render(){if(!state)return;const cost=k=>inputs[k].value.trim()===''?NaN:Number(inputs[k].value);result=evaluateSpaceSensitivity(data,evidence,state,{active:cost('active'),minors:cost('minors')});output.replaceChildren();if(result.status!=='ready'){output.append(el('p',result.reason));return;}
 const grid=el('div');grid.className='space-results';for(const r of result.results){const s=el('section');s.append(el('h3',r.team),el('strong',fmt(r.adjusted)+' adjusted asset balance'),el('p','Base '+fmt(r.gross)+' · shared space adjustment '+fmt(r.adjustment)));grid.append(s);}output.append(grid);
 const details=el('details');details.append(el('summary','Player allowances and assumptions'));for(const rows of result.packages)for(const a of rows)details.append(el('p',a.name+': '+a.bucket+(a.assumed?' (eligibility unverified; assumed active/reserve)':'')+' · allowance '+a.allowance.toFixed(1)+' · adjusted asset value '+a.adjusted.toFixed(1)));output.append(details);
 }
 for(const input of Object.values(inputs))input.addEventListener('input',render);reset.addEventListener('click',()=>{for(const i of Object.values(inputs))i.value='0';render();});
 return {render(next){state=next;render();},export(){return result;}};
}
