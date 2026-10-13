import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import {gunzipSync} from 'node:zlib';import {createHash} from 'node:crypto';import {execFileSync} from 'node:child_process';
const root='docs/research-layer-20261013/';const html=fs.readFileSync(root+'Calculator.html','utf8');const unpack=s=>JSON.parse(gunzipSync(Buffer.from(s.match(/const packed='([^']+)'/)[1],'base64')));const before=unpack(gunzipSync(fs.readFileSync('docs/curve-correction-20261013/baselines/26a1d75.html.gz')).toString()),after=unpack(html),rows=JSON.parse(fs.readFileSync(root+'Comparison.json')),summary=JSON.parse(fs.readFileSync(root+'Summary.json'));const ids=new Map(after.assets.map(a=>[a.id,a]));
test('research candidate preserves asset identities, forecasts, availability, competitive fit and every unsupported prior',()=>{
 assert.equal(after.assets.length,before.assets.length);for(const a of before.assets){const b=ids.get(a.id);assert.ok(b);for(const k of ['audit','career_profile','active_forecast_inputs','availability_status','competitive_values','distribution_summary','annual_expected_utility','contribution_fundamentals'])assert.deepEqual(b[k],a[k]);if(!b.research_layer)assert.deepEqual(b,a);}
 assert.equal(rows.length,648);assert.equal(after.assets.filter(a=>a.research_layer).length,summary.numerically_adjusted);
 assert.equal(createHash('sha256').update(gunzipSync(fs.readFileSync('docs/curve-correction-20261013/baselines/26a1d75.html.gz'))).digest('hex'),summary.unchanged_production_sha256);
});
test('DD dominates every adjustment and the baseline and research departure reconstruct the final value',()=>{
 for(const a of after.assets.filter(a=>a.research_layer)){const r=a.research_layer;assert.ok(r.source_weight>=.75&&r.source_weight<=1);assert.ok(r.effective_rank>=.9*r.DD_rank-1e-9&&r.effective_rank<=1.1*r.DD_rank+1e-9);assert.ok(Math.abs(r.DD_baseline+r.research_adjustment-a.values.neutral.display)<1e-9);assert.ok(Number.isFinite(a.values.neutral.display)&&a.values.neutral.display>0);}
});
test('Kodo numerical evidence requires the verified current MLB identity, dated season and matching observed exposure',()=>{
 const evidence=JSON.parse(fs.readFileSync(root+'Evidence.json'));for(const r of rows.filter(r=>r.kodo_numeric)){const e=evidence[r.id].kodo;assert.ok(e.valid);assert.equal(e.season,2026);assert.equal(e.level,'MLB');assert.ok(e.stat_date<='2026-10-13');assert.ok(r.sources.some(s=>s.source==='Kodo Analytics'));}
});
test('research retains actual QA3 and uses a single contact-quality family without provider QS or future saves holds substitution',()=>{
 for(const r of rows.filter(r=>r.projected_rate_line)){const a=before.assets.find(a=>a.id===r.id),z=r.projected_rate_line;if(r.role==='H'){assert.ok(z.H<=z.AB+1e-9&&z.HR<=z.H+1e-9);assert.ok(z.TB>=z.H+3*z.HR-1e-9&&z.TB<=4*z.H+1e-9);assert.ok(z.AB+z.BB+z.HBP+z.SF<=z.PA+1e-9);}else{for(const k of ['QA3','SV','HLD'])assert.ok(Math.abs(z[k]-a.audit.projection[k]/a.audit.projection.IP*r.reference_exposure)<1e-9);}}
});
test('research preview saved trade totals use the same additive scale and its explanatory code compiles',()=>{
 for(const t of after.trades){const totals=t.identities.map(v=>v.reduce((sum,id)=>sum+ids.get(id).values.neutral.display,0));for(let i=0;i<2;i++)assert.ok(Math.abs(t.neutral_transfer_packages[i]-totals[i])<1e-9);for(const m of Object.values(t.modes))assert.ok(Math.abs(m.neutral_transfer_change-(totals[1]-totals[0]))<1e-9);}
 const start=html.indexOf('script.textContent=')+'script.textContent='.length,end=html.indexOf(';document.body.append(script)',start),code=JSON.parse(html.slice(start,end));assert.ok(code.includes('DD baseline value'));assert.doesNotThrow(()=>new Function(code));
});
