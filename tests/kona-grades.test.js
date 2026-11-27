import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import{prospectGrades}from'../profile-context.js';
const d=JSON.parse(fs.readFileSync('data/international/professionals-2026.json')),p=d.players.find(x=>x.id==='kona-takahashi');
test('Kona leaves unpublished tools blank and retains the historical published reference',()=>{const h=prospectGrades(p);assert.ok(h.includes('FV 35+'));assert.ok(h.includes('not available'));assert.ok(!h.includes('Pipeline scouting estimates'));assert.ok(!h.includes('>45</b>'));assert.equal(p.pipelineRank,8);});
test('statistics and internal estimates cannot create published grades',()=>{const changed={...p,performance:{stats:{ERA:'0.50',K:'200',BB:'1'}}};assert.equal(prospectGrades(changed),prospectGrades(p));});
