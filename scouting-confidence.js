const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const caveats={
 international:'International amateur projections carry substantial uncertainty: public scouting and competitive samples are limited, and tools can change as players develop. A reported bonus or agreement does not establish a professional floor.',
 draft:'Amateur production and published scouting inform this projection, but the transition to professional competition remains uncertain. A verified draft pick or bonus does not verify the projected tools or MLB outcome.',
 dsl:'DSL results come from young players facing uneven competition in limited samples. Early production and published tools can change substantially with physical development and tougher assignments.',
 professional:'Native-league performance provides evidence, but its translation to MLB remains uncertain. Posting, signing and role expectations remain separate from the talent evaluation.',
 afl:'AFL results cover a short season against mixed competition. They supplement the longer performance and scouting record; a strong or weak fall alone does not establish a new talent level.',
 archive:'This is an archived ranking snapshot, not a newly verified scouting evaluation. Source coverage and player development may have changed since publication.',
 prospect:'This projection synthesizes dated public scouting and performance evidence, rather than a firsthand Pipeline scouting look. Coverage, sample size and level of competition limit how precisely future tools and roles can be judged.'
};
export function scoutingConfidence(p={},kind='prospect'){
 const rating=kind==='international'?p.ranking?.confidence:null;
 const label=rating?`${rating} confidence. `:'';
 return `<section class="scouting-confidence" aria-label="Scouting confidence"><h3>Scouting confidence</h3><p>${rating?`<strong>${esc(label)}</strong>`:''}${caveats[kind]??caveats.prospect}</p><p>Confidence describes the evidence behind the projection, not talent rank or the probability of reaching MLB.</p></section>`;
}
