// Reproducible editorial insertions; publication ranks and performance counts stay separate.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const date='2026-10-10';
const load=path=>JSON.parse(fs.readFileSync(path,'utf8'));
const save=(path,data,pretty=false)=>fs.writeFileSync(path,JSON.stringify(data,null,pretty?2:undefined)+'\n');
const draftPath='data/draft/2026.json',intlPath='data/international/2027.json';
const draft=load(draftPath),intl=load(intlPath);
const newSources=[
 {id:'yankees-september-review',name:'Yankees Farm Report — Aaron Lichstrahl, early pro scouting',date:'2026-09-08',url:'https://www.yankeesfarmreport.com/post/early-look-at-2026-draft-prospects',context:'Original scouting analysis of Potestio and Armstrong. Small Low-A samples; not a numbered FYPD ranking.'},
 {id:'potestio-draft-report',name:'Pinstripe Alley — Anthony Potestio draft profile',date:'2026-07-12',url:'https://www.pinstripealley.com/yankees-mlb-draft/196988/yankees-mlb-draft-2026-day-2-picks-top-prospects-rounds-11-15',context:'Draft and college context, with attributed Baseball America scouting. Not a FYPD rank.'},
 {id:'armstrong-draft-report',name:'Pinstripe Alley — Tyce Armstrong draft profile',date:'2026-07-12',url:'https://www.pinstripealley.com/yankees-mlb-draft/197032/yankees-mlb-draft-2026-picks-top-prospects-all-star-break',context:'College power production, first-base profile and 19th-round selection. Not a FYPD rank.'}
];
for(const s of newSources)if(!draft.sources.some(x=>x.id===s.id))draft.sources.push(s);
const draftInsertions=[
 {id:'anthony-potestio',at:70,confidence:'Moderate-low',sourceIds:['yankees-september-review','potestio-draft-report'],rationale:'Pipeline editorial placement in the middle-to-late developmental tier: contact and strike-zone judgment offer a more complete offensive foundation than a power-only lottery ticket. Modest projected impact and just 80 Low-A PA keep him below the established upper half. Inserted after Jason DeCaro and before Caden Sorrell; this is not an outside FYPD ranking.',paragraphs:[
 'Scouting update: July 12 draft coverage describes a patient left-handed hitter with contact skills and defensive versatility, but limited projected power. Aaron Lichstrahl’s September 8 scouting review supports the contact-and-decisions foundation and reports improved access to game power. Those are attributed evaluations, not Pipeline tool grades. The preserved official sample is 80 PA, five HR, 17.5% strikeouts and 23.8% walks.',
 'Pipeline placement: #70 of this 112-player MLB-draft board, provisionally. The bat-to-ball and on-base foundation merits a developmental selection, while the short debut cannot establish everyday MLB impact. He sits after Jason DeCaro and before Caden Sorrell; uncertainty about sustained power and defensive home keeps him outside the higher-upside tiers. No DD or BA FYPD rank was verified for him.'
 ]},
 {id:'tyce-armstrong',at:95,confidence:'Low',sourceIds:['yankees-september-review','armstrong-draft-report'],rationale:'Pipeline editorial placement in the late developmental tier: power and walks merit inclusion, but a 23-year-old first baseman faces a high offensive threshold. An 86-PA Low-A debut is insufficient to infer advanced-level contact. Inserted after Ryne Barker and before Aiden Ruiz; no external FYPD position is asserted.',paragraphs:[
 'Scouting update: July 12 draft reporting documents 24 college home runs and a first-base profile. Lichstrahl’s September 8 review describes productive airborne power and encouraging early contact, while emphasizing his age relative to Low-A competition. The preserved official debut has 86 PA, six HR, 23.3% strikeouts and 15.1% walks. Neither the small sample nor the college output establishes an MLB power grade.',
 'Pipeline placement: #95 of this 112-player MLB-draft board, provisionally. Power and on-base production justify a late developmental selection, but his age and first-base-only pathway leave less margin if advanced pitching exposes the contact. This is a Pipeline judgment, not a published DD or BA FYPD rank. Sustained contact and impact above Low-A would be the clearest reason to move him up.'
 ]}
];
const baseline=draft.players.filter(p=>p.consensusRank!=null).sort((a,b)=>a.consensusRank-b.consensusRank);
assert.equal(baseline.length,110);
const ordered=[...baseline];
for(const spec of draftInsertions){const p=draft.players.find(p=>p.id===spec.id);assert.ok(p);assert.equal(p.consensusRank,null);assert.equal(p.consensusScore,null);p.scoutingParagraphs=spec.paragraphs;p.ranking={asOf:date,basis:'Pipeline editorial insertion',confidence:spec.confidence,conditional:false,rationale:spec.rationale,sourceIds:spec.sourceIds};p.sourceIds=[...new Set([...p.sourceIds,...spec.sourceIds])];p.profileContext='Dated independent scouting informs a provisional Pipeline placement. Published source ranks remain separate; no market-wide consensus is claimed.';ordered.splice(spec.at-1,0,p);}
for(const [i,p]of ordered.entries())p.pipelineRank=i+1;
draft.players=ordered;draft.asOf=date;
draft.methodology='The preserved 110-player public-input baseline uses 70% DD domestic class position and 30% imported BA FYPD rank on a logarithmic scale. Missing DD is censored at 99 and missing BA at 101. Those consensus ranks and scores remain unchanged. Potestio (#70) and Armstrong (#95) are explicit Pipeline editorial insertions based on dated scouting, demonstrated contact/power, age, defensive pathway and sample uncertainty. Existing baseline players retain their relative order; numbered Pipeline places shift where insertions occur. Exact placements are provisional judgments, not statistical estimates or outside publication ranks. This board contains only 2026 MLB draftees eligible for the league FYPD; Japanese amateurs and 2027 J15 candidates remain on their separate page. Actual league FYPD picks remain unknown.';
const perez=intl.players.find(p=>p.id==='sebastian-perez-acuna'),oda=intl.players.find(p=>p.id==='shoki-oda');
assert.equal(perez.classYear,2027);assert.equal(oda.classYear,null);assert.equal(oda.expectedOrganization,null);
perez.ranking={asOf:date,basis:'Pipeline editorial placement',confidence:'Low',conditional:false,sourceIds:['perez-si','perez-romero'],rationale:'Provisional #8 of the 13-name comparison board (#7 among the 12 J15 candidates). Reported offensive impact and catching defense justify a place above less-defined developmental profiles; sparse independent game evidence keeps him below Arteaga and the more fully described impact group. Neither source supplies this numbered class rank.'};
perez.tier='Development upside · provisional';
perez.scoutingParagraphs=perez.scoutingParagraphs.map(s=>s.replace('before upgrading this unranked watch','before raising this provisional placement'));
oda.ranking={asOf:date,basis:'Pipeline conditional comparison',confidence:'Moderate-low',conditional:true,sourceIds:['oda-official','oda-scout','oda-velocity','oda-game','oda-status'],rationale:'Provisional #2 on this 13-name comparison board only if he chooses an MLB international route. The documented arsenal, reported upper-90s peak and U18 competition support impact starter upside. Pitcher attrition, consistency and a still-unresolved career path prevent treating him as a safe MLB investment. Sena remains first for his broader position-player pathway. This is not a confirmed J15 class rank or an external publication rank.'};
oda.tier='Impact upside · MLB route conditional';
const original=intl.players.filter(p=>!['sebastian-perez-acuna','shoki-oda'].includes(p.id)).sort((a,b)=>a.pipelineRank-b.pipelineRank);
assert.equal(original.length,11);
const international=[...original];international.splice(1,0,oda);international.splice(7,0,perez);
for(const [i,p]of international.entries())p.pipelineRank=i+1;
intl.players=international;intl.title='J15 Candidates';intl.asOf=date;
intl.methodology='Provisional Pipeline editorial comparison of 12 researched 2027 J15 candidates plus one separately labeled Japanese amateur. The original eleven candidates retain their relative order. Pérez Acuña is inserted at comparison #8 (#7 among J15 candidates) on reported offensive impact and catching defense, discounted for limited game evidence. Oda is comparison #2 only conditional on choosing the MLB international route; he is not assigned a confirmed J15 class year, MLB organization or signing. His asterisk denotes this condition, not a source rank. Scouting breadth, offensive or pitching foundation, positional pathway and evidence confidence determine editorial placement. Exact positions are judgment calls, not market consensus, measured tool grades or statistical probabilities. A comparison rank does not confer league draft eligibility. Expected bonus size is not a scoring input.';
save(draftPath,draft);save(intlPath,intl,true);
console.log('Ranked Potestio #70, Armstrong #95, Pérez #8, Oda #2 conditional; source ranks and counts preserved.');
