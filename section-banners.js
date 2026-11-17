const banners={
 league:{eyebrow:'BANGALANGIN PIPELINE / NOVEMBER 2026',title:'League Top 100'},
 draft:{eyebrow:'THE NEXT GENERATION / DOMESTIC DRAFT',title:'2026 Draft Rankings'},
 international:{eyebrow:'THE NEXT INTERNATIONAL CLASS',title:'J15 Candidates'},
 dsl:{eyebrow:'DOMINICAN SUMMER LEAGUE / 2026',title:'2026 DSL Rankings'},
 professionals:{eyebrow:'NPB / KBO / GLOBAL SCOUTING',title:'International Professionals'}
};
function motif(kind){
 const start='<svg class="title-banner-motif" viewBox="0 0 1200 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true">';
 if(kind==='league')return start+'<g fill="none" stroke="#a8c8a4" stroke-opacity=".3"><path d="m870 28-160 118 160 118 160-118zM870 28v118m-160 0h320"/><path d="m870 105-43 41 43 41 43-41z"/><path d="M1080 25v150M650 20v140" stroke-width="2"/></g><g fill="#eee4bd" fill-opacity=".35"><rect x="620" y="16" width="60" height="6"/><rect x="1050" y="21" width="60" height="6"/></g><g fill="none" stroke="#d6e5b5" stroke-opacity=".12"><ellipse cx="880" cy="225" rx="340" ry="95"/><ellipse cx="880" cy="225" rx="310" ry="75"/></g></svg>';
 if(kind==='draft')return start+'<g stroke="#c0a263" stroke-opacity=".28" fill="none"><path d="M610 0 520 200m185-200-90 200m185-200-90 200m185-200-90 200m185-200-90 200m185-200-90 200M590 40h610M570 80h630M550 120h650M530 160h670"/></g><g fill="#f5eacb" fill-opacity=".07" stroke="#c0a263" stroke-opacity=".45"><path d="m850 20 96-8 8 37-96 8z"/><path d="m970 14 96-8 8 37-96 8z"/><path d="m1090 20 96-8 8 37-96 8z"/></g></svg>';
 if(kind==='international')return start+'<g fill="none" stroke="#c0a263" stroke-opacity=".3"><ellipse cx="900" cy="180" rx="380" ry="260"/><ellipse cx="900" cy="180" rx="240" ry="260"/><ellipse cx="900" cy="180" rx="100" ry="260"/><path d="M550 60h650M520 120h680M520 180h680"/><circle cx="1115" cy="75" r="56"/><circle cx="1115" cy="75" r="49" stroke-dasharray="3 5"/></g><text x="1115" y="80" text-anchor="middle" fill="#cfb36e" opacity=".6" font-family="inherit" font-size="20" font-weight="700" transform="rotate(-12 1115 75)">JAN 15</text></svg>';
 if(kind==='dsl')return start+'<defs><radialGradient id="dsl-sunset"><stop stop-color="#dfb75e" stop-opacity=".52"/><stop offset="1" stop-color="#123e3b" stop-opacity="0"/></radialGradient></defs><ellipse cx="1020" cy="110" rx="380" ry="180" fill="url(#dsl-sunset)"/><circle cx="990" cy="115" r="58" fill="#d6b064" opacity=".3"/><path d="M550 150h650v50H550Z" fill="#203f32"/><path d="m720 200 240-65 240 65M960 135v65" fill="none" stroke="#d8bd7e" stroke-opacity=".3"/><path d="M1020 105h180v54h-180zM1000 105l110-45 110 45z" fill="#0b302b" stroke="#ad9d65" stroke-opacity=".3"/><g stroke="#0d342e" fill="#0d342e"><path d="M742 155q12-59 2-109" fill="none" stroke-width="8"/><path d="m744 48-44-15 23-5 22 14-2-31 12 15-4 19 35-20-10 21-26 4 39 15-23 5-18-15-17 27-6-12z"/></g></svg>';
 return start+'<g fill="none" stroke="#c0a263" stroke-opacity=".42"><path d="M610 170Q850-90 1160 105M640 190Q960-20 1170 145"/><circle cx="670" cy="153" r="5"/><circle cx="1150" cy="115" r="5"/><path d="M530 20h650M530 180h650" stroke-opacity=".15"/></g><g fill="#c0a263" fill-opacity=".12"><path d="m1100 15 20 15-9 15-17-5-9 18-16-5-3-20zM1080 70l-13 19-17 3-9 20-21 6-18 22-28 7-13 18-22 6 7-17 19-14 16-26 20-11 10-17 22-4 12-17z"/><path d="m770 26 20 18-5 21 18 25-10 25-20 6-8-17 7-27-14-20z"/></g></svg>';
}

export function sectionBanner(kind){
 const b=banners[kind];if(!b)return '';
 return '<header class="page-title-banner page-title-banner--'+kind+'">'+motif(kind)+'<div class="page-title-copy"><span class="eyebrow">'+b.eyebrow+'</span><h1>'+b.title+'</h1></div></header>';
}
