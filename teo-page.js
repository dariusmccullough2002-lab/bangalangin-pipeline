export function showTeoPage(app){
 app.innerHTML=`<article class="report">
 <span class="eyebrow">POWER TRANSLATION LAB</span>
 <h1>TEO explained</h1>
 <p><b>TEO is an experimental profile-survival index, not an MLB success probability.</b></p>
 <p>It asks one question: given how much a hitter chases and misses, does his impact support that offensive profile?</p>
 <h2>Score interpretation</h2>
 <ul>
  <li><b>85–100:</b> Elite survival margin</li>
  <li><b>70–84:</b> Strong survival margin</li>
  <li><b>55–69:</b> Impact supports the risk</li>
  <li><b>45–54:</b> Borderline / near frontier</li>
  <li><b>30–44:</b> Concerning</li>
  <li><b>0–29:</b> Impact does not support the risk</li>
 </ul>
 <h2>Coverage tiers</h2>
 <p><b>Tier A:</b> Chase + Whiff + observed Hard-Hit + observed Barrel.</p>
 <p><b>Tier B:</b> Chase + Whiff + one observed impact metric.</p>
 <p><b>Tier C:</b> Chase + Whiff + an estimated impact proxy when measured Hard-Hit/Barrel coverage is unavailable.</p>
 <p><b>Tier D:</b> insufficient data.</p>
 <h2>Power Survival Frontier</h2>
 <p>The fitted frontier estimates the amount of impact historically associated with a viable power profile at each level of Chase + Whiff risk. It is a historical reference, not a deterministic success threshold.</p>
 <h2>Important limitations</h2>
 <p>Tier C is proxy-based and should not be treated with the same certainty as Tier A. Raw minor-league measurements are not automatically MLB-equivalent, and TEO should remain separate from official prospect rankings until the model is validated further.</p>
 <p><a class="button" href="#power-translation-lab">Open the visualization →</a></p>
 </article>`;
}