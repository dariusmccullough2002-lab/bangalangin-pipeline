import test from 'node:test';
import assert from 'node:assert/strict';
import {currentAge} from '../player-bio.js';
test('age display respects birthdays and nested official bio records',()=>{
 assert.equal(currentAge({birthDate:'2006-11-20'},'2026-11-20',0),'20');
 assert.equal(currentAge({birthDate:'2006-11-21'},'2026-11-20',0),'19');
 assert.equal(currentAge({bio:{birthDate:'1999-10-22'}},'2026-11-20',0),'27');
 assert.equal(currentAge({birthDate:'2006-03-14'},'2026-11-20'),'20.7');
});
test('unknown or future DOB cannot silently reuse a dated analytical age',()=>{
 assert.equal(currentAge({age:17},'2026-11-20'),'—');
 assert.equal(currentAge({birthDate:'2027-01-01'},'2026-11-20'),'—');
});
