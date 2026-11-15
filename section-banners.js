const headings = {
 draft: ['THE NEXT GENERATION / DOMESTIC DRAFT', '2026 Draft Rankings'],
 international: ['THE NEXT INTERNATIONAL CLASS', 'J15 Candidates'],
 dsl: ['INTERNATIONAL / DOMINICAN SUMMER LEAGUE', '2026 DSL Rankings'],
 professionals: ['INTERNATIONAL / PROFESSIONAL LEAGUES', 'International Professionals']
};
export function sectionBanner(kind) {
 const heading = headings[kind];
 return heading ? `<span class="eyebrow">${heading[0]}</span><h1>${heading[1]}</h1>` : '';
}
