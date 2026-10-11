import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
const source=JSON.parse(readFileSync('data/role-display-scenarios.json'));
const html=readFileSync('trade-analyzer-beta/index.html','utf8');
const catalog=JSON.parse(gunzipSync(Buffer.from(html.match(/const packed='([^']+)'/)[1],'base64')));
globalThis.fetch=async()=>({ok:true,json:async()=>source});
const {projectionViews,hitterRatios}=await import('../trade-analyzer-beta/role-display.js');
const rates=(l,k)=>k==='H'?hitterRatios(l):{ERA:l.IP?9*l.ER/l.IP:null,WHIP:l.IP?(l.H+l.BB)/l.IP:null};
const rows=[];
for(const a of catalog.assets){const s=source.players[a.id];if(!s)continue;const v=projectionViews(a,source),p=(a.audit.MLB||a.audit).projection;
 const row={id:a.id,name:a.name,role:s.role,supported:!!v?.scenario,fallback:s.reason||s.method,observation:JSON.stringify(s.observations?.[0]),full_role_appearances:v?.scenario?.appearances??null,full_role_PA_IP:v?.scenario?.workload??null,preserved_full_role:s.preservedFullWorkload??null,conditional_given_participation:s.researchConditionalActive??null,research_expected:s.researchExpected??null,participation:s.participation??null,probabilities:JSON.stringify(s.probabilities),team_adjustment:0,medical_adjustment:0};
 for(const [prefix,line] of [['expected',p],['scenario',v?.scenario?.line]])if(line)for(const [key,value] of Object.entries({...line,...rates(line,s.kind)}))row[prefix+'_'+key]=value;
 rows.push(row);
}
const keys=[...new Set(rows.flatMap(r=>Object.keys(r)))],quote=v=>v===undefined||v===null?'':JSON.stringify(String(v));
writeFileSync('docs/website/role-display-comparison.csv',[keys.map(quote).join(','),...rows.map(r=>keys.map(k=>quote(r[k])).join(','))].join('\n')+'\n');
const names=['Aaron Judge','Matt Olson','Shea Langeliers','Gavin Lux','Raisel Iglesias','Matt Brash'];
writeFileSync('docs/website/role-display-example-lines.json',JSON.stringify(rows.filter(r=>names.includes(r.name)),null,2)+'\n');
console.log('Audited',rows.length,'routed/evidence records; supported',rows.filter(x=>x.supported).length);
