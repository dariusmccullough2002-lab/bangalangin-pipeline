import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
const html=readFileSync(new URL('../trade-analyzer-beta/index.html',import.meta.url),'utf8');
const data=JSON.parse(gunzipSync(Buffer.from(html.match(/const packed='([^']+)'/)[1],'base64')));
test('ranking-led release applies reviewed values and preserves contribution separation',()=>{
 const cases={'Josue De Paula':51.61220462736102,'Leo De Vries':50.874659314455165,'Kaelen Culpepper':25.850921327486976,'Walker Jenkins':38.02416176975817,'Kade Anderson':38.02416176975817};
 for(const [name,v] of Object.entries(cases)){const a=data.assets.find(a=>a.name===name);assert.equal(a.values.neutral.display,v);assert.ok(a.ranking_policy);assert.ok(a.ranking_policy.source_weight>.5);assert.equal(a.values.neutral.underlying,null);}
 assert.equal(data.assets.filter(a=>a.ranking_policy).length,265);
 for(const a of data.assets.filter(a=>a.ranking_policy)){for(const v of Object.values(a.values))assert.equal(v.display,a.values.neutral.display);assert.ok(a.range.low.neutral<=a.values.neutral.display&&a.range.high.neutral>=a.values.neutral.display);assert.equal(a.ranking_policy.contribution_value,a.contribution_fundamentals.values.neutral.display);}
});
test('saved neutral trade packages use released policy values',()=>{
 const by=new Map(data.assets.map(a=>[a.id,a]));for(const t of data.trades){const sums=t.identities.map(ids=>ids.reduce((n,id)=>n+by.get(id).values.neutral.display,0));sums.forEach((v,i)=>assert.ok(Math.abs(t.neutral_transfer_packages[i]-v)<1e-10));for(const m of Object.values(t.modes))assert.ok(Math.abs(m.neutral_transfer_change-(sums[1]-sums[0]))<1e-10);}
});
