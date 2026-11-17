import {jerseySvg} from './jerseys.js';
const banners={
 draft:{eyebrow:'THE NEXT GENERATION / DOMESTIC DRAFT',title:'2026 Draft Rankings',players:[{name:'Grady Emerson',mlbOrg:'TB'},{name:'Roch Cholowsky',mlbOrg:'CWS'},{name:'Drew Burress',mlbOrg:'ATH'}]},
 international:{eyebrow:'THE NEXT INTERNATIONAL CLASS',title:'J15 Candidates',players:[{name:'Alfredo Sena',country:'DO'},{name:'Jose Tarifa',country:'VE'},{name:'Shoki Oda',country:'JP'}]},
 dsl:{eyebrow:'DOMINICAN SUMMER LEAGUE / 2026',title:'2026 DSL Rankings',players:[{name:'Angeibel Gomez',mlbOrg:'KC',number:'15'},{name:'Yostin Peña',mlbOrg:'NYY',number:'27'},{name:'Leanders Matos',mlbOrg:'MIL',number:'9'}]},
 professionals:{eyebrow:'NPB / KBO / GLOBAL SCOUTING',title:'International Professionals',players:[{name:'Teruaki Sato',number:'8',jerseyDesign:[null,'Hanshin Tigers','#f7f5ef','#141414','#f9c900','Tigers','stripe']},{name:'Kaima Taira',number:'61',jerseyDesign:[null,'Saitama Seibu Lions','#102137','#ffffff','#b8c5d5','Lions']},{name:'Shugo Maki',number:'2',jerseyDesign:[null,'Yokohama DeNA BayStars','#f8f8f4','#0067b2','#0067b2','BAYSTARS','stripe']}]}
};
const countryFlags={
 DO:'<rect x="64" y="92" width="24" height="16" fill="#003b70"/><rect x="92" y="92" width="24" height="16" fill="#ce2637"/><rect x="64" y="112" width="24" height="16" fill="#ce2637"/><rect x="92" y="112" width="24" height="16" fill="#003b70"/><path d="M90 92v36m-26-18h52" stroke="#fff" stroke-width="4"/>',
 VE:'<path d="M64 98h52" stroke="#f9ca23" stroke-width="12"/><path d="M64 110h52" stroke="#164788" stroke-width="12"/><path d="M64 122h52" stroke="#ce2637" stroke-width="12"/><path d="m78 111 4-3 4-1 4-1 4 1 4 1 4 3" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="1 3"/>',
 JP:'<rect x="64" y="92" width="52" height="36" fill="#fff"/><circle cx="90" cy="110" r="11" fill="#c72e40"/>'
};
function shirt(p){
 if(!p.country){const svg=jerseySvg(p);const word={TB:'RAYS',CWS:'WHITE SOX',ATH:'ATHLETICS'}[p.mlbOrg];return !p.number&&word?svg.replace('<text x="90" y="155"','<text x="90" y="118" text-anchor="middle" fill="'+({TB:'#092c5c',CWS:'#111111',ATH:'#efb21e'}[p.mlbOrg])+'" font-family="Arial,sans-serif" font-size="18" font-weight="800">'+word+'</text><text x="90" y="155"'):svg;}
 const svg=jerseySvg({...p,jerseyDesign:[null,'International class','#f5efdd','#123e3b','#c0a263','INTERNATIONAL']});
 return svg.replace('</g><g class="jersey-front">',countryFlags[p.country]+'</g><g class="jersey-front">');
}
function motif(kind){
 const start='<svg class="title-banner-motif" viewBox="0 0 1200 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true">';
 if(kind==='draft')return start+'<g stroke="#c0a263" stroke-opacity=".28" fill="none"><path d="M610 0 520 200m185-200-90 200m185-200-90 200m185-200-90 200m185-200-90 200m185-200-90 200M590 40h610M570 80h630M550 120h650M530 160h670"/></g><g fill="#f5eacb" fill-opacity=".07" stroke="#c0a263" stroke-opacity=".45"><path d="m850 20 96-8 8 37-96 8z"/><path d="m970 14 96-8 8 37-96 8z"/><path d="m1090 20 96-8 8 37-96 8z"/></g></svg>';
 if(kind==='international')return start+'<g fill="none" stroke="#c0a263" stroke-opacity=".3"><ellipse cx="900" cy="180" rx="380" ry="260"/><ellipse cx="900" cy="180" rx="240" ry="260"/><ellipse cx="900" cy="180" rx="100" ry="260"/><path d="M550 60h650M520 120h680M520 180h680"/><circle cx="1115" cy="75" r="56"/><circle cx="1115" cy="75" r="49" stroke-dasharray="3 5"/></g><text x="1115" y="80" text-anchor="middle" fill="#cfb36e" opacity=".6" font-family="inherit" font-size="20" font-weight="700" transform="rotate(-12 1115 75)">JAN 15</text></svg>';
 if(kind==='dsl')return start+'<defs><radialGradient id="dsl-sunset"><stop stop-color="#dfb75e" stop-opacity=".52"/><stop offset="1" stop-color="#123e3b" stop-opacity="0"/></radialGradient></defs><ellipse cx="1020" cy="110" rx="380" ry="180" fill="url(#dsl-sunset)"/><circle cx="990" cy="115" r="58" fill="#d6b064" opacity=".3"/><path d="M550 150h650v50H550Z" fill="#203f32"/><path d="m720 200 240-65 240 65M960 135v65" fill="none" stroke="#d8bd7e" stroke-opacity=".3"/><path d="M1020 105h180v54h-180zM1000 105l110-45 110 45z" fill="#0b302b" stroke="#ad9d65" stroke-opacity=".3"/><g stroke="#0d342e" fill="#0d342e"><path d="M742 155q12-59 2-109" fill="none" stroke-width="8"/><path d="m744 48-44-15 23-5 22 14-2-31 12 15-4 19 35-20-10 21-26 4 39 15-23 5-18-15-17 27-6-12z"/></g></svg>';
 return start+'<g fill="none" stroke="#c0a263" stroke-opacity=".42"><path d="M610 170Q850-90 1160 105M640 190Q960-20 1170 145"/><circle cx="670" cy="153" r="5"/><circle cx="1150" cy="115" r="5"/><path d="M530 20h650M530 180h650" stroke-opacity=".15"/></g><g fill="#c0a263" fill-opacity=".12"><path d="m1100 15 20 15-9 15-17-5-9 18-16-5-3-20zM1080 70l-13 19-17 3-9 20-21 6-18 22-28 7-13 18-22 6 7-17 19-14 16-26 20-11 10-17 22-4 12-17z"/><path d="m770 26 20 18-5 21 18 25-10 25-20 6-8-17 7-27-14-20z"/></g></svg>';
}
export function sectionBanner(kind){
 const b=banners[kind];if(!b)return '';
 return '<header class="page-title-banner page-title-banner--'+kind+'">'+motif(kind)+'<div class="page-title-copy"><span class="eyebrow">'+b.eyebrow+'</span><h1>'+b.title+'</h1></div><div class="title-banner-jerseys" aria-hidden="true">'+b.players.map(p=>'<span class="title-banner-shirt" title="'+p.name+(p.country?' · country-inspired jersey concept':' · club-inspired jersey concept')+'">'+shirt(p)+'</span>').join('')+'</div></header>';
}
