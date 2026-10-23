import fs from 'node:fs';
import zlib from 'node:zlib';
import {join} from 'node:path';
export const draftRules=Object.freeze({teams:12,totalRounds:17,tradableRounds:[1,2,3,4,5],freeAgentFirstRound:6,freeAgentLastRound:17,freeAgentSelections:144,source:'User correction, 2026-10-23',policy:'Rounds 6–17 are acquisition opportunities only, never trade assets.'});
export function correctText(s){return s.replace(/The old 17-round rules text is superseded by the user's 20-round clarification\./g,'The user confirmed a 17-round draft on October 23, 2026.').replace(/(rounds\s*|R)6([–—-])20/gi,(_,prefix,dash)=>prefix+'6'+dash+'17').replace(/(rounds\s*)6(\\+u2013)20/gi,(_,prefix,dash)=>prefix+'6'+dash+'17').replace(/20-round/g,'17-round');}
function correctObject(v){if(typeof v==='string')return correctText(v);if(Array.isArray(v))return v.map(correctObject);if(v&&typeof v==='object')return Object.fromEntries(Object.entries(v).map(([k,x])=>[k,correctObject(x)]));return v;}
export function correctDraftRules(output){
 for(const relative of ['trade-analyzer-beta/index.html','value-audit-preview/overall/index.html','value-audit-preview/spacing/index.html']){
  const path=join(output,relative);if(!fs.existsSync(path))continue;let html=fs.readFileSync(path,'utf8');
  const match=html.match(/const packed='([^']+)'/);if(!match)throw Error('Missing packed analyzer data: '+relative);
  const data=correctObject(JSON.parse(zlib.gunzipSync(Buffer.from(match[1],'base64'))));data.draft_rules=draftRules;
  html=html.replace(match[1],zlib.gzipSync(JSON.stringify(data)).toString('base64'));
  fs.writeFileSync(path,correctText(html));
 }
 for(const relative of ['trade-analyzer-beta/access-durability.js','data/access-durability.json']){
  const path=join(output,relative);if(fs.existsSync(path))fs.writeFileSync(path,correctText(fs.readFileSync(path,'utf8')));
 }
}
