const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));
const metrics = {cps: 'CPS', oqi: 'Pitching Difficulty (OQI)', ops: 'OPS', pa: 'PA', relativeOps: 'Relative OPS', age: 'Age (youngest first)'};
const decimal = (value, digits) => value.toFixed(digits).replace(/^0\./, '.');

export async function loadAflCps() {
  try {
    const response = await fetch('data/afl/cps-2026.json', {cache: 'no-cache'});
    if (!response.ok) throw Error('CPS dataset unavailable');
    const data = await response.json();
    return data.version === 'CPS_v1' && data.status === 'complete' && data.hitters?.length ? data : null;
  } catch {
    return null;
  }
}

export function featuredCpsHitters(data, limit = 3) {
  return sortCpsHitters(data?.hitters ?? [], 'cps')
    .filter(row => row.pa >= 35 && row.ops >= .850).slice(0, limit);
}

export function sortCpsHitters(rows, metric) {
  const key = Object.hasOwn(metrics, metric) ? metric : 'cps';
  return [...rows].sort((a, b) => (key === 'age' ? (a.age ?? Infinity) - (b.age ?? Infinity) : b[key] - a[key]) || a.rank - b.rank);
}

export function renderAflCps(app, data, players) {
  const intro = '<a href="#afl">← AFL Tracker</a><h1>CPS Hitter Leaderboard</h1>';
  if (!data) {
    app.innerHTML = intro + '<p role="status">CPS data is currently unavailable.</p>';
    return;
  }
  const date = new Date(data.generatedAt);
  const tz = {timeZone: 'America/New_York'};
  const day = new Intl.DateTimeFormat('en-US', {...tz, dateStyle: 'medium'}).format(date);
  const time = new Intl.DateTimeFormat('en-US', {...tz, hour: 'numeric', minute: '2-digit'}).format(date);
  app.innerHTML = intro + `
    <p>CPS evaluates AFL offense in the context of team environment, sample size and the actual pitchers each hitter faced.</p>
    <p class="muted">CPS updated ${esc(day)} · ${esc(time)} ET · ${data.completedGames} completed games</p>
    <div class="controls" style="display:flex;align-items:center;flex-wrap:wrap;gap:12px;width:100%;max-width:none"><input style="box-sizing:border-box;height:44px;flex:1 1 280px;min-width:0;max-width:100%;margin:0" id="cps-search" type="search" aria-label="Search CPS players" placeholder="Search players…"><label for="cps-sort" style="display:flex;align-items:center;gap:10px;margin:0 0 0 auto"><span>Sort by</span><select id="cps-sort" style="box-sizing:border-box;height:44px;margin:0">${Object.entries(metrics).map(([key, label]) =>
      `<option value="${key}">${label}</option>`).join('')}</select></label></div>
    <div class="tablewrap" role="region" aria-label="CPS hitter rankings"><table><thead><tr>
      ${['CPS rank', 'Player', 'Age', 'AFL team', 'PA', 'OPS', 'Relative OPS', 'Pitching Difficulty (OQI)', 'CPS'].map(label =>
        `<th scope="col">${label}</th>`).join('')}</tr></thead><tbody id="cps-rows"></tbody></table></div>
    <section aria-label="CPS and OQI definitions">
      <p><strong>CPS (Contextual Performance Score)</strong> measures AFL hitting performance after accounting for team offense, sample size, and the quality of pitching faced. Higher CPS means stronger performance in context.</p>
      <p><strong>OQI (Opponent Quality Index)</strong> measures the difficulty of the pitchers a hitter actually faced, weighted by matched plate appearances. A score of 100 is average among qualified hitters. Higher scores indicate tougher pitching.</p>
    </section>
    <details class="afl-method" style="width:100%;max-width:none"><summary>How CPS works</summary>
      <p>Pitcher Quality Index (PQI) weights standardized PitchIQ Filth+ (40%), CSW% (20%), whiff rate (15%), chase rate (10%) and K−BB% (15%). Pitch samples are regressed toward league average using pitches ÷ (pitches + 150).</p>
      <p>Official MLB play-by-play identifies the pitcher in each completed plate appearance. OQI weights pitcher PQI by matched plate appearances and scales the result around 100. Higher OQI means tougher opposition. This update matched ${data.matchedPa.toLocaleString()} of ${data.totalPa.toLocaleString()} completed PA.</p>
      <p>CPS combines standardized OPS (65%) and relative OPS (35%). Relative OPS is ln(player OPS ÷ team OPS). Offensive reliability rises with sample size and reaches full weight at 60 PA. Above-average opposition adds a modest boost, while softer opposition receives a larger penalty. The board requires 20 official PA and 20 matched PA. Featured hitters require 35 PA and .850 OPS.</p>
      <p><strong>CPS is an experimental performance-context metric, not an MLB projection or prospect grade.</strong> Sources include PitchIQ pitcher metrics and official MLB AFL hitting statistics and completed-game feeds.</p>
    </details>
    <details class="afl-method" style="width:100%;max-width:none"><summary>How OQI works</summary>
      <p>Official MLB play-by-play identifies the pitcher each hitter faced in every completed plate appearance. Each matched appearance counts once, so pitchers faced more often carry more weight.</p>
      <p>OQI starts with the hitter’s plate-appearance-weighted average Pitcher Quality Index (PQI). PQI uses PitchIQ’s Filth+, called strikes plus whiffs (CSW%), whiff rate, chase rate, and strikeout rate minus walk rate. Smaller pitching samples are pulled toward league average.</p>
      <p>The weighted averages are standardized across qualified hitters and converted to <strong>OQI = 100 + 10 × z-score</strong>. A score of 100 is average, and 110 means the hitter faced pitching one standard deviation tougher than average.</p>
    </details>`;
  const profiles = new Map(players.map(p => [p.mlbamId, p]));
  const asOf = data.through ?? data.generatedAt.slice(0, 10);
  const hitters = data.hitters.map(row => {
    const dob = profiles.get(row.mlbamId)?.bio?.birthDate;
    const age = /^\d{4}-\d{2}-\d{2}$/.test(dob ?? '') && dob <= asOf
      ? Number(asOf.slice(0, 4)) - Number(dob.slice(0, 4)) - (asOf.slice(5) < dob.slice(5) ? 1 : 0)
      : null;
    return {...row, age};
  });
  const select = app.querySelector('#cps-sort');
  const search = app.querySelector('#cps-search');
  const normalize = value => value.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
  const render = () => {
    const terms = normalize(search.value).trim().split(/\s+/);
    const matches = hitters.filter(row => terms.every(term => normalize(row.name).includes(term)));
    app.querySelector('#cps-rows').innerHTML = sortCpsHitters(matches, select.value).map(row => {
      const route = profiles.get(row.mlbamId)?.route;
      const name = route ? `<a href="${esc(route)}">${esc(row.name)}</a>` : esc(row.name);
      return `<tr><td>${row.rank}</td><td>${name}</td><td>${row.age ?? '—'}</td><td>${esc(row.team)}</td><td>${row.pa}</td><td>${decimal(row.ops,3)}</td><td>${row.relativeOps.toFixed(3)}</td><td>${row.oqi.toFixed(1)}</td><td><strong>${row.cps.toFixed(1)}</strong></td></tr>`;
    }).join('') || '<tr><td colspan="9">No players match your search.</td></tr>';
  };
  search.oninput = render;
  select.onchange = render;
  render();
}
