import {bonusProfile} from './ba-bonus-board.js';
import {checkpointHtml} from './development-checkpoints.js';
import {currentAge} from './player-bio.js';
import {sectionBanner} from './section-banners.js';
import {scoutingConfidence} from './scouting-confidence.js';
import {matchesInternationalClass} from './international-class.js';
import {internationalBonus,compareInternationalBonuses} from './international-bonus.js';
import {draftOutcomesHtml} from './draft-outcomes.js';
import {profileUnderlyingData,loadAfl,activateAflLive,aflCard,aflRegularSeason} from './afl.js';
import {loadProfileHistory,transactionHistory,activateProfileTabs,acquisitionContext} from './profile-history.js';
import {prospectGrades,prospectMetrics} from './profile-context.js?v=20261126-scouting-card-final4';

// BangaLangin Pipeline projected 2027 J15 scouting grades.
// Source: J15_2027_Pipeline_Scouting_Grades.csv (November 26, 2026 review).
// These are internal Pipeline projections, not published MLB Pipeline, Baseball America, or FanGraphs grades.
const j15PipelineGrades={
  "alfredo-sena": {
    "type": "H",
    "g": [
      65,
      65,
      60,
      60,
      null,
      60
    ],
    "fv": 60,
    "c": "Low"
  },
  "miguel-grullon": {
    "type": "H",
    "g": [
      65,
      60,
      60,
      null,
      null,
      null
    ],
    "fv": 55,
    "c": "Low"
  },
  "mairon-de-la-rosa": {
    "type": "H",
    "g": [
      50,
      65,
      60,
      70,
      null,
      60
    ],
    "fv": 55,
    "c": "Low"
  },
  "jose-tarifa": {
    "type": "H",
    "g": [
      60,
      60,
      55,
      null,
      null,
      null
    ],
    "fv": 55,
    "c": "Low"
  },
  "shoki-oda": {
    "type": "P",
    "g": [
      70,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": 55,
    "c": "Low"
  },
  "junior-fortunato": {
    "type": "H",
    "g": [
      60,
      55,
      55,
      null,
      null,
      null
    ],
    "fv": 55,
    "c": "Low"
  },
  "camilo-gutierrez": {
    "type": "H",
    "g": [
      60,
      50,
      45,
      null,
      null,
      null
    ],
    "fv": 50,
    "c": "Low"
  },
  "jesus-arteaga": {
    "type": "H",
    "g": [
      55,
      55,
      55,
      null,
      65,
      60
    ],
    "fv": 55,
    "c": "Low"
  },
  "dylan-rodriguez": {
    "type": "H",
    "g": [
      55,
      60,
      55,
      null,
      null,
      45
    ],
    "fv": 50,
    "c": "Low"
  },
  "nicolas-quintero": {
    "type": "H",
    "g": [
      55,
      60,
      55,
      null,
      null,
      null
    ],
    "fv": 50,
    "c": "Low"
  },
  "eddy-hernandez": {
    "type": "H",
    "g": [
      45,
      70,
      55,
      null,
      null,
      null
    ],
    "fv": 50,
    "c": "Low"
  },
  "joh-sung-chul": {
    "type": "H",
    "g": [
      50,
      55,
      50,
      null,
      null,
      null
    ],
    "fv": 50,
    "c": "Low"
  },
  "antonio-figueroa": {
    "type": "H",
    "g": [
      null,
      70,
      55,
      null,
      null,
      null
    ],
    "fv": 50,
    "c": "Low"
  },
  "cesar-montero": {
    "type": "H",
    "g": [
      55,
      55,
      50,
      55,
      null,
      null
    ],
    "fv": 50,
    "c": "Low"
  },
  "manuel-hernandez": {
    "type": "H",
    "g": [
      50,
      60,
      50,
      65,
      null,
      55
    ],
    "fv": 50,
    "c": "Low"
  },
  "jeiler-blanco": {
    "type": "H",
    "g": [
      45,
      60,
      50,
      60,
      null,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "michael-prado": {
    "type": "H",
    "g": [
      55,
      55,
      45,
      null,
      null,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "raider-sanchez-trutie": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "snaiker-garcia": {
    "type": "H",
    "g": [
      55,
      null,
      null,
      null,
      null,
      60
    ],
    "fv": 45,
    "c": "Low"
  },
  "yasleyker-parra": {
    "type": "H",
    "g": [
      55,
      55,
      50,
      50,
      null,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "axel-carrasco": {
    "type": "H",
    "g": [
      55,
      50,
      45,
      null,
      null,
      55
    ],
    "fv": 45,
    "c": "Low"
  },
  "snafe-alvarez": {
    "type": "H",
    "g": [
      55,
      40,
      35,
      65,
      null,
      60
    ],
    "fv": 45,
    "c": "Low"
  },
  "anthony-calderon": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "eudi-yuten": {
    "type": "H",
    "g": [
      40,
      65,
      50,
      null,
      60,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "cristian-oscar-lias-bieneme": {
    "type": "H",
    "g": [
      45,
      60,
      55,
      null,
      null,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "fernando-marmolejos": {
    "type": "H",
    "g": [
      55,
      55,
      45,
      null,
      null,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "sebastian-perez-acuna": {
    "type": "H",
    "g": [
      45,
      60,
      55,
      null,
      null,
      55
    ],
    "fv": 45,
    "c": "Low"
  },
  "euniel-de-la-cruz": {
    "type": "H",
    "g": [
      40,
      65,
      50,
      null,
      null,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "wilson-reyes": {
    "type": "H",
    "g": [
      55,
      40,
      35,
      null,
      null,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "kosei-hiroike": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "amaurys-martinez": {
    "type": "H",
    "g": [
      40,
      65,
      50,
      60,
      null,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "markus-rodriguez": {
    "type": "H",
    "g": [
      50,
      55,
      45,
      null,
      null,
      55
    ],
    "fv": 45,
    "c": "Low"
  },
  "salamon-millan": {
    "type": "H",
    "g": [
      50,
      70,
      55,
      null,
      null,
      40
    ],
    "fv": 45,
    "c": "Low"
  },
  "tatsuya-nogami": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "harris-miller-jackson": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "jhonn-rodriguez": {
    "type": "H",
    "g": [
      55,
      50,
      45,
      60,
      null,
      55
    ],
    "fv": 45,
    "c": "Low"
  },
  "marlon-polanco": {
    "type": "H",
    "g": [
      45,
      70,
      55,
      55,
      70,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "loryi-pineda": {
    "type": "H",
    "g": [
      45,
      60,
      45,
      null,
      null,
      null
    ],
    "fv": 40,
    "c": "Low"
  },
  "moises-alcalde": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "william-alejandro-alvarez-landa": {
    "type": "H",
    "g": [
      40,
      65,
      50,
      null,
      null,
      null
    ],
    "fv": 40,
    "c": "Low"
  },
  "albert-hernandez": {
    "type": "H",
    "g": [
      55,
      55,
      50,
      null,
      null,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "boni-guzman": {
    "type": "H",
    "g": [
      55,
      40,
      35,
      null,
      null,
      55
    ],
    "fv": 40,
    "c": "Low"
  },
  "angel-rojas": {
    "type": "H",
    "g": [
      55,
      50,
      45,
      40,
      null,
      null
    ],
    "fv": 40,
    "c": "Low"
  },
  "breidy-campusano": {
    "type": "H",
    "g": [
      55,
      50,
      45,
      60,
      null,
      null
    ],
    "fv": 45,
    "c": "Low"
  },
  "ashton-hernandez": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "denyer-ramirez": {
    "type": "H",
    "g": [
      null,
      55,
      null,
      null,
      null,
      60
    ],
    "fv": 40,
    "c": "Low"
  },
  "cai-chen-long": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "wilver-hernandez": {
    "type": "H",
    "g": [
      45,
      45,
      35,
      55,
      null,
      60
    ],
    "fv": 40,
    "c": "Low"
  },
  "erick-gonzalez-nicaragua-2027": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "eyder-orasma": {
    "type": "H",
    "g": [
      55,
      40,
      35,
      null,
      null,
      60
    ],
    "fv": 40,
    "c": "Low"
  },
  "yoel-king": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "omar-guerra": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "leandri-benitez": {
    "type": "H",
    "g": [
      40,
      60,
      45,
      55,
      null,
      null
    ],
    "fv": 40,
    "c": "Low"
  },
  "edenis-cruz": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": 40,
    "c": "Low"
  },
  "eudy-alcantara": {
    "type": "H",
    "g": [
      40,
      65,
      45,
      null,
      65,
      null
    ],
    "fv": 40,
    "c": "Low"
  },
  "alexis-liriano": {
    "type": "H",
    "g": [
      40,
      60,
      45,
      60,
      null,
      null
    ],
    "fv": 40,
    "c": "Low"
  },
  "raymer-moreno": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "yirvel-figuereo": {
    "type": "H",
    "g": [
      50,
      40,
      35,
      null,
      null,
      null
    ],
    "fv": 40,
    "c": "Low"
  },
  "jose-muniz": {
    "type": "H",
    "g": [
      45,
      55,
      50,
      null,
      null,
      45
    ],
    "fv": 40,
    "c": "Low"
  },
  "rodelvis-santiesteban": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "jendry-gonell": {
    "type": "H",
    "g": [
      40,
      45,
      35,
      70,
      null,
      60
    ],
    "fv": 40,
    "c": "Low"
  },
  "amaurys-dilon": {
    "type": "H",
    "g": [
      40,
      70,
      50,
      null,
      null,
      null
    ],
    "fv": 40,
    "c": "Low"
  },
  "luis-advincola": {
    "type": "H",
    "g": [
      50,
      40,
      35,
      55,
      null,
      null
    ],
    "fv": 40,
    "c": "Low"
  },
  "luis-fiallo": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "kendry-morales": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "yonewrys-garcia": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "enmanuel-beltre": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "yeferson-sanchez": {
    "type": "P",
    "g": [
      70,
      60,
      null,
      null,
      55,
      40
    ],
    "fv": 45,
    "c": "Low"
  },
  "cayro-hazel": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "marko-morua": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "jhonny-damon-proenza": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "carlos-adrian-hernandez-cuba": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "luis-garcia-nicaragua-2027": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "alayn-daniel-blanco": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "enyel-gonzalez": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "yeremy-de-leon": {
    "type": "P",
    "g": [
      45,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": 35,
    "c": "Low"
  },
  "orangel-guanaguaney": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "luis-zapata": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "lenyert-rios": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "alexis-medina": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "keddy-roa": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "sebastian-zorrilla": {
    "type": "H",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "maykoll-jaspe": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "elvin-cepeda": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "manuel-cordero": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  },
  "windel-encarnacion": {
    "type": "P",
    "g": [
      null,
      null,
      null,
      null,
      null,
      null
    ],
    "fv": null,
    "c": "Insufficient evidence"
  }
};

const hitterLabels=['Hit','Raw power','Game power','Run','Arm','Field'];
const pitcherLabels=['Fastball','Slider','Curveball','Changeup','Splitter','Control'];
const pct=grade=>grade==null?0:Math.max(0,Math.min(100,(Number(grade)-20)/60*100));
const tone=grade=>grade==null?'missing':grade>=60?'plus':grade>=45?'average':'below';

function pipelineJ15GradesCard(player){
  const row=j15PipelineGrades[player?.id];
  if((row?.type??player?.type)==='P'){
    const fv=row?.fv==null?null:row.fv>=60?55:row.fv>=55?50:row.fv>=50?45:row.fv;
    return prospectGrades({...player,j15Amateur:true,pipelineProjectedGrades:row?{...row,fv}:null});
  }
  const values=row?.g??Array(6).fill(null);
  const calibrate=(grade,tool)=>{
    if(grade==null)return null;
    const g=Number(grade);
    // International amateur grades are translated onto the same future-value
    // scale used for the domestic draft class. Pre-pro projection is not treated
    // as equivalent evidence to a polished domestic amateur or professional track record.
    if(tool==='Hit')return Math.min(55,g>=60?55:g);
    if(tool==='Raw Power')return g>=70?65:g>=65?60:g>=60?55:g;
    if(tool==='Game Power')return g>=55?Math.max(45,g-10):g>=50?45:g;
    if(tool==='Run')return Math.min(65,g);
    if(tool==='Fielding'||tool==='Throw')return Math.min(60,g);
    return g;
  };
  const fv=row?.fv==null?null:row.fv>=60?55:row.fv>=55?50:row.fv>=50?45:row.fv;
  const gradePairs=[
    ['Hit',calibrate(values[0],'Hit')],
    ['Raw Power',calibrate(values[1],'Raw Power')],
    ['Game Power',calibrate(values[2],'Game Power')],
    ['Run',calibrate(values[3],'Run')],
    ['Fielding',calibrate(values[5],'Fielding')],
    ['Throw',calibrate(values[4],'Throw')]
  ];
  const rows=[['Future Value',fv],...gradePairs]
    .map(([label,grade])=>`<div class="pipeline-grade-row ${grade==null?'is-missing':''}"><span class="pipeline-grade-label">${esc(label)}</span><div class="pipeline-grade-track" aria-hidden="true"><i class="pipeline-grade-fill pipeline-grade-fill--${tone(grade)}" style="width:${pct(grade)}%"></i></div><b class="pipeline-grade-value">${grade==null?'—':esc(grade)}</b></div>`).join('');
  return `<section class="pipeline-grade-card pipeline-grade-card--compact" aria-label="Scouting grades"><div class="pipeline-grade-grid">${rows}</div></section>`;
}

const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const amateurSearchText=p=>[p.name,p.nativeName,...(p.aliases??[])].filter(Boolean).join(' ').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();
const internationalCountry=p=>p.country??({'alfredo-sena':'Dominican Republic','mairon-de-la-rosa':'Dominican Republic','miguel-grullon':'Dominican Republic','nicolas-quintero':'Venezuela'}[p.id])??'-';
const normalize=v=>String(v).normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();
const classLabel=p=>p.entryClassLabel??(p.novemberUpdate?'2025–2026 international period':p.classYear===2026?'2026 J15':p.classYear===2027||/^2027(?:\s|$)/.test(p.classLabel??'')?'2027 J15':p.classLabel??'Unsigned scouting watch');
const destination=p=>p.officialOrganization?`Signed ${p.officialOrganization}`:p.expectedOrganization?`Expected ${p.expectedOrganization}`:'Team TBD';
const rank=n=>n==null?'—':`#${n}`;
export const amateurRank=p=>(p.novemberUpdate&&p.pipelineRank==null?'Unranked':rank(p.pipelineRank))+(p.ranking?.conditional?'*':'');
export function internationalAge(p,today=new Date().toLocaleDateString('en-CA',{timeZone:'America/New_York'})){
 if(p.ageEvidence?.birthDateRange){
  const [earliest,latest]=p.ageEvidence.birthDateRange;
  const older=internationalAge({birthDate:earliest},today).label,younger=internationalAge({birthDate:latest},today).label;
  return {label:`${younger===older?younger:`${younger}–${older}`}*`,detail:`Age inferred from dated reports, not an exact birth date. ${p.ageEvidence.note}`};
 }
 const dob=p.birthDate;
 if(/^\d{4}-\d{2}-\d{2}$/.test(dob??'')&&dob<=today){
  const [y,m,d]=today.split('-').map(Number),[by,bm,bd]=dob.split('-').map(Number);
  return {label:String(y-by-(m<bm||(m===bm&&d<bd)?1:0)),detail:`Born ${dob}${p.ageEvidence?.source?` · ${p.ageEvidence.source}`:''}`};
 }
 if(Number.isInteger(p.ageEvidence?.reportedAge))return {label:`${p.ageEvidence.reportedAge}*`,detail:`Reported age ${p.ageEvidence.reportedAge} as of ${p.ageEvidence.asOf} · ${p.ageEvidence.source}; exact birth date unverified${p.ageEvidence.note?` · ${p.ageEvidence.note}`:''}`};
 return {label:'-',detail:'No reliable age or birth date reported'};
}
export function internationalStatus(p){
 const raw=p.signingStatus??'';
 if(p.signingEvidence?.status==='reported-signed'&&!p.officialOrganization)return {label:'Signed · reported',kind:'reported'};
 if(p.officialOrganization)return {label:'Signed',kind:'signed'};
 if(/physical pending/i.test(raw))return {label:'Physical pending',kind:'pending'};
 if(/being finalized/i.test(raw))return {label:'Finalizing agreement',kind:'pending'};
 if(/acquisition route pending/i.test(raw))return {label:'Route pending',kind:'pending'};
 if(/^unsigned/i.test(raw))return {label:'Unsigned',kind:'unsigned'};
 if(/agreement|rights/i.test(raw))return {label:'Reported agreement',kind:'reported'};
 return {label:'-',kind:'unsigned'};
}
export function internationalMeasurements(p){
 const m=p.measurements??{};let height=p.novemberUpdate?'Not yet verified':'-',weight=p.novemberUpdate?'Not yet verified':'-';
 const raw=String(m.height??'').trim(),cm=raw.match(/^(\d+(?:\.\d+)?)\s*cm$/i),feet=raw.match(/^(\d+)\s*['′]\s*(\d+)\s*["″]?$/);
 if(cm){const inches=Math.round(Number(cm[1])/2.54);height=`≈ ${Math.floor(inches/12)} ft ${inches%12} in`;}
 else if(feet)height=`${Number(feet[1])} ft ${Number(feet[2])} in`;
 if(Number(m.weightKg)>0)weight=`≈ ${Math.round(Number(m.weightKg)*2.2046226218)} lb`;
 else if(Number(m.weightLb)>0)weight=`${Number(m.weightLb)} lb`;
 return {height,weight};
}
const rankingNote=p=>p.ranking?`<section class="notice amateur-ranking-note"><h3>Pipeline ranking · ${esc(p.ranking.asOf)}</h3><p>${esc(p.ranking.rationale)}</p><p class="muted">${esc(p.ranking.basis)} · ${esc(p.ranking.confidence)} confidence</p>${p.ranking.evidenceDate?`<p class="muted">Latest cited evidence: ${esc(p.ranking.evidenceDate)} · Review date: ${esc(p.ranking.asOf)}</p>`:''}${p.riskLevel?`<p><b>Development risk:</b> ${esc(p.riskLevel)}. Research confidence describes evidence quality, not the chance of reaching MLB.</p>`:''}</section>`:'';
const cache=new Map();
// Cross-section navigation lives in the main header.
const nav=()=>'';
const money=n=>n==null?'—':new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
const sourceList=sources=>sources.map(s=>`<div class="source-entry"><h3>${esc(s.name)}</h3><p class="muted">${esc(s.date??'Original publication date unavailable')} · ${esc(s.context)}</p>${s.url?`<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer"><u>Open source ↗</u></a>`:''}</div>`).join('');
function method(app,data,kind){app.innerHTML=`${nav()}<article class="report"><span class="eyebrow">${kind==='draft'?'DRAFT':'INTERNATIONAL'} / EDITORIAL METHOD</span><h1>Evidence before expectations.</h1><p>${esc(data.methodology)}</p><h2>Source context</h2>${sourceList(data.sources)}<p><a class="button" href="#${kind}">Return to the rankings →</a></p></article>`;}
export function internationalUpdateHtml(p,data){
 const u=p.novemberUpdate;if(!u)return '';
 const citations=ids=>(ids??[]).map(id=>data.sources.find(source=>source.id===id)).filter(Boolean).map(source=>`<a href="${esc(source.url)}" target="_blank" rel="noopener noreferrer"><u>${esc(source.name)}</u></a>`).join(' · ');
 const items=rows=>`<ul>${rows.map(text=>`<li>${esc(text)}</li>`).join('')}</ul>`;
 const age=internationalAge(p).label;
 const arsenal=u.pitchArsenal?.length?`<h2>Pitch arsenal</h2><p class="muted">Reported observations; no numerical scouting grades. Unverified velocity ranges are omitted.</p><div class="table-wrap"><table><thead><tr><th>Pitch</th><th>Velocity evidence</th><th>Development assessment</th></tr></thead><tbody>${u.pitchArsenal.map(row=>`<tr><th scope="row">${esc(row.pitch)}</th><td>${esc(row.velocity)}</td><td>${esc(row.assessment)}</td></tr>`).join('')}</tbody></table></div>`:'';
 return `<section class="international-signing-update"><h2>Scouting classification</h2><p><b>${esc(u.classification)}</b></p><p>Country: ${esc(p.country)} · Position: ${esc(p.position)} · Age: ${esc(age==='-'?'Not yet verified':age)}<br>Date of birth: ${esc(p.birthDate??(p.reportedBirthDate?p.reportedBirthDate+' (reported; primary record not yet verified)':'Not yet verified'))}<br>Bats: ${esc(p.bats??'Not yet verified')} · Throws: ${esc(p.throws??'Not yet verified')}</p><p><b>Signing status:</b> ${esc(p.signingStatus)}<br><b>Reported bonus:</b> ${esc(p.reportedBonusExpectation??'Not yet verified')}<br><b>Actual signing date:</b> ${esc(u.eligibility.actualSigningDate)}</p><div class="draft-outcome-grid"><section><h3>Strengths</h3>${items(u.strengths)}</section><section><h3>Developmental concerns</h3>${items(u.concerns)}</section></div><h2>Performance evidence</h2>${u.performanceEvidence.map(row=>`<section><h3>${esc(row.label)}</h3><p><b>${esc(row.status)}</b></p><p>${esc(row.detail)}</p><p class="muted">${citations(row.sourceIds)}</p></section>`).join('')}${arsenal}<section class="international-development-outcomes"><h2>Developmental outcomes</h2><p class="muted">Pipeline qualitative scouting assessment. These are possible paths, not grades, model-generated projections or statistical forecasts.</p><div class="draft-outcome-grid">${[['Ceiling',u.outcomes.ceiling],['Realistic outcome',u.outcomes.realistic],...(u.outcomes.alternative?[['Alternative outcome',u.outcomes.alternative]]:[]),['Downside',u.outcomes.downside]].map(([heading,text])=>`<section class="draft-outcome"><h3>${heading}</h3><p>${esc(text)}</p></section>`).join('')}</div><h3>Development timeline</h3><p>${esc(u.timeline.nextStep)}</p><p><b>MLB ETA:</b> ${esc(u.timeline.mlbEta)}</p><p class="muted">${esc(u.timeline.context)}</p></section><h3>Next research checkpoints</h3>${items(u.researchPriorities)}<h2>Signing period & fantasy eligibility</h2><p><b>${esc(u.eligibility.signingPeriod)}</b></p><dl><dt>Previous FYPD eligibility</dt><dd>${esc(u.eligibility.previousFypdEligibility)}</dd><dt>Fantrax public catalog</dt><dd>${esc(u.eligibility.fantraxCatalogStatus)}</dd><dt>Current league availability</dt><dd>${esc(u.eligibility.leagueAvailability)}</dd><dt>2027 FYPD simulator</dt><dd>${esc(u.eligibility.simulatorStatus)}</dd></dl><p class="muted">Catalog checked ${esc(u.eligibility.checkedAsOf)}. A missing catalog entry does not establish league eligibility. ${citations(u.eligibility.sourceIds)}</p><p class="muted">Last verification: ${esc(u.asOf)}. Unavailable information is not inferred from bonus size or raw tools.</p></section>`;
}
export function profile(app,data,kind,id){
 const p=data.players.find(p=>p.id===id);if(!p){app.innerHTML=`${nav()}<h1>Profile not found</h1><a href="#${kind}">Return to the class →</a>`;return;}
 const intl=kind==='international',physical=internationalMeasurements(p);
 const seasonStats=p.seasonStats??(p.aflProfile?aflRegularSeason(p):null);
 const facts=intl?[['CLASS',classLabel(p)],['PIPELINE RANK',amateurRank(p)],['REPORTED DESTINATION',p.expectedOrganization??'Team TBD'],['OFFICIAL ORGANIZATION',p.officialOrganization??(p.novemberUpdate?'Not yet verified':p.classification?'-':'Not signed')]]:[['PIPELINE CLASS RANK',amateurRank(p)],['HEIGHT / WEIGHT',[p.height, p.weight ? `${p.weight} lb` : null].filter(Boolean).join(' · ') || 'Not listed'],['CURRENT AGE',currentAge(p)],['MLB DRAFT PICK',`#${p.mlbDraftPick} · Round ${p.mlbDraftRound}`],['DRAFT ORGANIZATION',p.draftOrganization],['VERIFIED BONUS',money(p.signingBonus)]];
 if(intl)facts.push(['LISTED HEIGHT',physical.height],['LISTED WEIGHT',physical.weight]);
 const measurements=intl?`<h3>Physical measurements</h3><p>Height: ${esc(physical.height)} · Weight: ${esc(physical.weight)} · B-T: ${esc(p.bats??'-')}-${esc(p.throws??'-')}</p>${p.measurements?`<p class="muted">Reported by ${esc(p.measurements.source)} · ${esc(p.measurements.sourceDate)}. ${p.measurements.sourceUrl?`<a href="${esc(p.measurements.sourceUrl)}" target="_blank" rel="noopener noreferrer">Measurement source ↗</a>. `:''}Listed measurements; may change as he develops.${p.measurements.notes?` ${esc(p.measurements.notes)}`:''}</p>`:''}`:'';
 const src=(intl?bonusProfile(p)+'<p>Pipeline places are provisional editorial judgments. Talent rank remains independent of published bonus order.</p>':Object.entries({ 'DD November FYPD rank':p.sourceRanks.ddNovemberFypd,'DD domestic class order':p.sourceRanks.ddClass,'DD overall prospects':p.sourceRanks.ddOverall,'BA FYPD input':p.sourceRanks.baFypd,'Earlier DD pre-draft input':p.sourceRanks.ddPreDraft,'MLB pre-draft rank':p.sourceRanks.mlbDraft}).filter(([,v])=>v!=null).map(([k,v])=>`<p>${esc(k)} <b>${rank(v)}</b></p>`).join(''))+measurements;
 app.innerHTML=`${nav()}<a href="#${kind}">← ${esc(data.title)}</a><div class="player-nameplate-field"><h1>${esc(p.name)}</h1>${p.nativeName?`<p class="muted" lang="${p.country==='Taiwan'?'zh-Hant':'ja'}">${esc(p.nativeName)}</p>`:''}<div class="player-nameplate-meta"><span class="eyebrow">${intl?`INTERNATIONAL ${p.officialOrganization?'SIGNING':'AMATEUR'} / ${classLabel(p)}`:'2026 MLB DRAFT / CLASS PROFILE'}</span><p>${intl?`${esc(p.position)} - ${esc(destination(p))}`:`${esc(p.position)} · ${esc(p.draftTeamName)} · ${esc(p.playerType)}`}</p></div></div><div class="profile"${p.aflProfile?` data-checkpoint-route="afl-player/${p.mlbamId}"`:''}><div class="panel"><div class="facts">${facts.map(([k,v])=>`<div><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join('')}</div><h2>Scouting context & projection</h2>${p.scoutingParagraphs.map(s=>`<p>${esc(s)}</p>`).join('')}<p class="muted">${esc(p.profileContext)}</p>${intl?internationalUpdateHtml(p,data):''}${p.developmentCheckpoint?checkpointHtml(p.developmentCheckpoint):''}${intl&&p.research?`<h3>Research check · ${esc(p.research.asOf)}</h3><p><b>${esc(p.research.coverage)}</b></p><p>${esc(p.research.verifiedContext)}</p><p class="muted">${esc(p.research.limitations)}</p>`:''}${!intl?draftOutcomesHtml(p):''}${p.independentBonusBoardReview?`<section class="notice"><h3>Independent offensive review · ${esc(p.independentBonusBoardReview.asOf)}</h3><p>${esc(p.independentBonusBoardReview.assessment)}</p></section>`:''}${rankingNote(p)}${acquisitionContext(p)}<h3>Ranking context</h3><p>${intl?esc(p.tier):'Class rank is separate from the owned-prospect October Top 100. The initial Pipeline order uses the public-input model; professional evidence is displayed without automatic small-sample promotions.'}</p><p class="muted">Actual league FYPD selection: not recorded in this edition.</p>${scoutingConfidence(p,intl?'international':'draft')}</div><aside class="panel">${intl?pipelineJ15GradesCard(p):prospectGrades(p)}<h2>Source ranking inputs</h2>${src}<p><a href="#${kind}-method"><u>Dates, scope and ranking method →</u></a></p><h3>${intl?'Signing context':'Verified draft record'}</h3>${intl?`<p>Reported destination: <b>${esc(p.expectedOrganization??'Team TBD')}</b><br>Official organization: <b>${p.officialOrganization??(p.novemberUpdate?'Not yet verified':p.classification?'-':'Not signed')}</b></p>${p.reportedBonusExpectation?`<p>${p.novemberUpdate?'Reported signing bonus':'Reported bonus expectation'}: ${esc(p.reportedBonusExpectation)}</p><p class="muted">${p.novemberUpdate?'Reported amount; independent payment or club confirmation not yet verified.':'Reported expectation; see the dated research check and sources. Not a confirmed signing bonus.'}</p>`:''}`:`<p>${esc(p.school)}<br>${esc(p.bats)} / ${esc(p.throws)} · ${esc(p.height)} · ${esc(p.weight)} lb<br>${esc(p.level??'No verified 2026 pro level')}</p><a href="${esc(p.sourceUrl)}" target="_blank" rel="noopener noreferrer"><u>Official MLB draft data ↗</u></a><p><a href="https://www.milb.com/player/${p.mlbamId}" target="_blank" rel="noopener noreferrer"><u>Official player record ↗</u></a></p>`}${aflCard(p)}${profileUnderlyingData(p)}</aside></div>${transactionHistory(p)}${!intl&&seasonStats?prospectMetrics({...p,seasonStats}):''}<details class="panel amateur-sources"><summary>Profile sources and limitations</summary>${sourceList(data.sources.filter(s=>p.sourceIds.includes(s.id)))}</details>`;
 activateProfileTabs(app);activateAflLive(app);
}
function listing(app,data,kind){
 const intl=kind==='international';const clubs=[...new Set(data.players.map(p=>intl?p.expectedOrganization:p.draftOrganization).filter(Boolean))].sort();
 app.innerHTML=`${nav()}${sectionBanner(kind)}<p class="muted">${intl?`${data.players.filter(p=>p.pipelineRank!=null).length} ranked profiles · ${data.players.filter(p=>p.classYear===2027).length} reported 2027 J15 candidates · ${data.players.filter(p=>p.classYear!==2027).length} other-period or route-unconfirmed profiles · ${data.players.filter(p=>p.pipelineRank==null).length} unranked scouting watches`:`${data.players.length} researched draft selections · Public-input baseline with editorial placements`} · Updated ${esc(data.asOf)}</p>${intl?'<div class="notice"><b>One complete international board.</b> Independent dynasty evaluations set the order; BA’s bonus board remains a separate market reference. All profiles have a combined Pipeline rank; the separate BA bonus ranks remain available in the sort menu and profiles. Reported agreements remain unofficial until confirmed, and players without a verified destination are labeled Team TBD. <a href="#international-method"><u>Sources and methodology →</u></a></div>':''}<div class="controls amateur-controls"><input id="am-search" aria-label="Search amateur prospects" placeholder="Search players…">${intl?'<select id="am-class" aria-label="J15 class"><option value="">All classes</option><option value="2027">2027 J15</option><option value="2026">2026 signing period</option><option value="other">Other / unconfirmed</option></select>':''}<select id="am-type" aria-label="Amateur player type"><option value="">All positions</option><option value="H">Hitters</option><option value="P">Pitchers</option></select><select id="am-org" aria-label="Amateur MLB organization"><option value="">${intl?'All expected destinations':'All draft organizations'}</option>${clubs.map(c=>`<option value="${esc(c)}">${esc(c)}</option>`).join('')}</select><select id="am-sort" aria-label="Sort amateur prospects"><option value="rank">Pipeline rank</option>${intl?'<option value="ba">BA bonus rank</option>':''}<option value="name">Player name</option>${intl?'<option value="bonus-desc">Bonus</option>':''}${!intl?'<option value="age">Age</option><option value="draft">MLB draft pick</option>':''}</select></div><p id="am-count" class="muted" aria-live="polite"></p>${intl?'<p class="international-age-note muted">Age * = dated report or inferred age; birth date unverified. — = unknown. Bonus amounts are reported unless verified; ≈ = approximate, &gt; = more than. TBD = unreported. Select a player’s name for sources and signing details.</p>':''}<div class="tablewrap"><table><thead><tr><th id="am-rank-heading">PIPELINE</th><th>PROSPECT</th>${intl?'<th>HEIGHT<br>WEIGHT</th><th>AGE</th><th>NATION</th><th>B-T</th>':'<th>B-T</th>'}<th>${intl?'MLB':'DRAFT ORGANIZATION'}</th><th>${intl?'STATUS':'AGE / LEVEL'}</th>${intl?'<th>BONUS</th>':'<th>CONSENSUS</th>'}${!intl?'<th>NOV DD / BA FYPD</th>':''}</tr></thead><tbody id="am-rows"></tbody></table></div><p class="muted">${intl?'Pipeline places compare all listed international talents on one cross-period dynasty board. Close ranks have substantial uncertainty; signing status, organization and league FYPD eligibility remain separate from talent rank.':'Consensus remains the preserved DD/BA input order. Pipeline numbers include labeled editorial insertions; no missing source rank is invented. MLB Draft picks are actual MLB selections, not fantasy draft picks.'}</p>`;
 if(!intl&&data.ddNovemberFypd){const profiles=new Map(data.players.map(p=>[p.id,p]));const details=document.createElement('details');details.className='panel';details.innerHTML='<summary>Dynasty Dugout · November FYPD top 106</summary><ol>'+data.ddNovemberFypd.entries.map(row=>{const p=profiles.get(row.profileId);return '<li>'+(p?'<a href="#draft-player/'+esc(p.id)+'">'+esc(row.name)+'</a>':esc(row.name)+' · '+esc(row.position)+' · '+esc(row.team))+'</li>';}).join('')+'</ol>';app.append(details);}
 const render=()=>{const q=document.querySelector('#am-search').value.trim();const normalizedQuery=normalize(q),t=document.querySelector('#am-type').value,o=document.querySelector('#am-org').value,sort=document.querySelector('#am-sort').value,selectedClass=intl?document.querySelector('#am-class').value:'';let rows=data.players.filter(p=>(!intl||matchesInternationalClass(p,selectedClass))&&amateurSearchText(p).includes(normalizedQuery)&&(!t||p.type===t)&&(!o||(intl?p.expectedOrganization:p.draftOrganization)===o));rows.sort((a,b)=>intl&&sort.startsWith('bonus-')?compareInternationalBonuses(a,b,sort.slice(6)):sort==='name'?a.name.localeCompare(b.name):sort==='age'?String(b.birthDate??'').localeCompare(String(a.birthDate??'')):sort==='draft'?a.mlbDraftPick-b.mlbDraftPick:intl&&sort==='ba'?((a.baBonusRank??10000)-(b.baBonusRank??10000)||(a.pipelineRank??10000)-(b.pipelineRank??10000)):(a.pipelineRank??10000)-(b.pipelineRank??10000));if(intl)document.querySelector('#am-rank-heading').textContent=sort==='ba'?'BA BONUS':'PIPELINE';document.querySelector('#am-count').textContent=`${rows.length} of ${data.players.length} players shown`;document.querySelector('#am-rows').innerHTML=rows.map(p=>`<tr><td>${intl&&sort==='ba'?rank(p.baBonusRank):amateurRank(p)}</td><td><a href="#${kind}-player/${p.id}">${esc(p.name)}</a><small>${intl?`${esc(p.position)} · International amateur`:`${esc(p.position)} · ${esc(p.playerType)}`}</small></td>${intl?`<td class="international-measurement"><span>${esc(internationalMeasurements(p).height)}</span><span>${esc(internationalMeasurements(p).weight)}</span></td><td><span class="international-age" title="${esc(internationalAge(p).detail)}">${esc(internationalAge(p).label)}</span></td><td class="international-country">${esc(internationalCountry(p))}</td><td class="international-handedness">${esc(p.bats??'-')}-${esc(p.throws??'-')}</td>`:`<td class="international-handedness">${esc(p.bats??'-')}-${esc(p.throws??'-')}</td>`}<td>${intl?esc(p.officialOrganization??p.expectedOrganization??'TBD'):esc(p.draftOrganization)}</td><td>${intl?`<span class="international-status international-status--${internationalStatus(p).kind}" title="${esc(p.signingStatus)}">${esc(internationalStatus(p).label)}</span>`:`${currentAge(p)} · ${esc(p.level??'Pro level unavailable')}`}</td>${intl?`<td class="international-bonus" title="${esc(internationalBonus(p).detail)}">${esc(internationalBonus(p).label)}</td>`:`<td>${rank(p.consensusRank)}</td>`}${!intl?`<td>${rank(p.sourceRanks.ddNovemberFypd)} / ${rank(p.sourceRanks.baFypd)}</td>`:''}</tr>`).join('')||`<tr><td colspan="${intl?9:7}">No prospects match these filters.</td></tr>`;};document.querySelector('#am-search').oninput=render;for(const id of ['am-type','am-org','am-sort',...(intl?['am-class']:[])])document.querySelector('#'+id).onchange=render;render();
}
export function loadAmateurData(kind){
 if(!cache.has(kind))cache.set(kind,fetch(`data/${kind}/${kind==='draft'?'2026':'2027'}.json`).then(r=>{if(!r.ok)throw Error('Publication unavailable');return r.json();}).catch(error=>{cache.delete(kind);throw error;}));
 return cache.get(kind);
}
export async function showAmateurs(app,page,id){
 const kind=page.startsWith('international')?'international':'draft';const current=location.hash;
 app.innerHTML=`${nav()}<p>Loading ${kind==='draft'?'the draft class':'international prospects'}…</p>`;
 try{const data=await loadAmateurData(kind);if(page.endsWith('-player'))await Promise.all([loadProfileHistory(),loadAfl()]);if(location.hash!==current)return;if(page.endsWith('-method'))method(app,data,kind);else if(page.endsWith('-player'))profile(app,data,kind,id);else listing(app,data,kind);}catch(e){cache.delete(kind);if(location.hash===current)app.innerHTML=`${nav()}<h1>Publication unavailable</h1><p>Refresh to retry loading this class.</p>`;}
}

