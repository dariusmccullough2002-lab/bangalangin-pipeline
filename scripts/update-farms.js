import {readFileSync,writeFileSync} from 'node:fs';
import {scoreFarms,farmWeights} from './farm-model.js';
const path='data/editions/october-2026.json';
const edition=JSON.parse(readFileSync(path));
const organizations=JSON.parse(readFileSync('data/organizations.json'));
edition.farms=scoreFarms(edition.rankings,organizations);
edition.farmMethodology={weights:farmWeights,valueCurve:'100 / (1 + (leagueRank / 45)^1.25)',
  components:{elite:'60% best prospect value + 40% mean value of the top five (empty slots are zero).',topTen:'Mean value of top ten, empty slots zero.',depth:'Half count capped at 30; half count with value >=20 capped at 20.',ceiling:'Top-five dated impact tool signal, adjusted by development certainty. Unknown grades use ranking value, never an invented grade.',proximity:'Value-weighted top-ten highest verified 2026 level: AAA 1, AA .7, A+ .35, A .2, CPX .08, DSL .05; missing zero.',hitting:'Mean value of top ten hitters, empty slots zero.',pitching:'Mean value of top five pitchers, empty slots zero. Two-way players also count as hitters.',certainty:'Top-ten development certainty from level, contact/control and sample size. Higher means lower modeled risk; no inferred injury diagnosis.'},
  certaintyFormula:'55 + level adjustment (AAA15, AA10, A+4, A0, CPX-10, DSL-15, unknown-20), plus up to10 for sample (400 PA/100 IP); minus10 for <one-third sample; hitting penalty 1.1*(K%-20) above20; pitching penalty 2*(BB%-8) above8. Missing season stats minus15. Clamp 0–100.',
  ceilingFormula:'Selected impact tool future maximum: clamp((grade-30)*2,0,100), multiplied by .6+.4*certainty/100. Unknown: ranking value. Mean top five with zeros for empty slots.',
  normalization:'Each component is scaled to its league leader at 100, then weighted. Composite normalized to the leading farm at 100; gap = 100 - index.',
  tiers:'Elite >=90; Strong >=80; Above average >=65; Middle >=45; Thin <45. Relative to this league and this edition.',
  limitations:'Transparent model-based power rankings, not a publication scouting grade or talent probability. Rank and tool inputs overlap intentionally. Dated grades, missing samples and the non-debuted rule affect results. No sum of organizational ranks. Farm index is relative, not WAR or an absolute MLB grade.'};
writeFileSync(path,JSON.stringify(edition,null,2)+'\n');
console.log(edition.farms.map(f=>`${f.rank}. ${f.name}: ${f.index} (${f.eligibleCount})`).join('\n'));
