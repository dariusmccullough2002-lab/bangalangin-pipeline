const banners={
 draft:{title:'2026 Draft Rankings',eyebrow:'THE NEXT GENERATION / DOMESTIC DRAFT',tagline:'The next class. Your next pick.',asset:'draft'},
 international:{title:'J15 Candidates',eyebrow:'JANUARY 15 / INTERNATIONAL TALENT',tagline:'The next chapter. No borders.',asset:'j15'},
 dsl:{title:'2026 DSL Rankings',eyebrow:'DOMINICAN SUMMER LEAGUE / 2026',tagline:'Where the next wave begins.',asset:'dsl'},
 professionals:{title:'International Professionals',eyebrow:'NPB / KBO · 2026–27',tagline:'Proven overseas. Next stop?',asset:'professionals'}
};
export function sectionBanner(kind){
 const b=banners[kind];if(!b)return '';
 return `<header class="section-banner section-banner--${b.asset}"><div class="section-banner-copy"><span class="eyebrow">${b.eyebrow}</span><h1>${b.title}</h1><p>${b.tagline}</p></div><div class="section-banner-art" aria-hidden="true"><img src="assets/banners/${b.asset}.webp" alt="" width="900" height="500" fetchpriority="high"></div></header>`;
}
