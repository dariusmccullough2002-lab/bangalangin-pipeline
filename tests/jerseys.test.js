import test from 'node:test';
import assert from 'node:assert/strict';
import {jerseySurname,jerseySvg} from '../jerseys.js';
test('jersey labels preserve compound surnames and remove generational suffixes',()=>{
 for(const [name,expected] of Object.entries({'James Tibbs III':'TIBBS','Enrique Bradfield Jr.':'BRADFIELD','Leo De Vries':'DE VRIES','George Lombard Jr':'LOMBARD','Fernando De La Cruz':'DE LA CRUZ','Juan De Los Santos':'DE LOS SANTOS','Victor Mesa Jr.':'MESA','Pete Crow-Armstrong':'CROW-ARMSTRONG',"Jack O’Dowd":"O’DOWD",'Ryan Sloan':'SLOAN'})){
  assert.equal(jerseySurname({name}),expected,name);
  assert.ok(jerseySvg({name}).includes('>'+expected+'</text>'),name);
 }
 assert.equal(jerseySurname({name:'A Different Name',lastName:'De Vries'}),'DE VRIES');
 assert.equal(jerseySurname({name:'A Different Name',surname:'Smith-Jones'}),'SMITH-JONES');
 assert.equal(jerseySurname({}),'');
});
test('long surnames fit the jersey nameplate without truncation and remain escaped',()=>{
 const svg=jerseySvg({name:'Pete Crow-Armstrong'});
 assert.match(svg,/textLength="105" lengthAdjust="spacingAndGlyphs"/);
 assert.ok(svg.includes('>CROW-ARMSTRONG</text>'));
 assert.ok(jerseySvg({surname:'<Smith>'}).includes('&lt;SMITH&gt;'));
});
