const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));
const metrics = {cps: 'CBS+', oqi: 'Pitching Difficulty (OQI)', ops: 'OPS', pa: 'PA', age: 'Age'};
const decimal = (value, digits) => value.toFixed(digits).replace(/^0\./, '.');

export async function loadAflCps() {
  try {
    const response = await fetch('data/afl/cps-2026.json', {cache: 'no-cache'});
    if (!response.ok) throw Error('CBS+ dataset unavailable');
    const data = await response.json();
    if (data.version !== 'CPS_v1' || data.status !== 'complete' || !data.hitters?.length) return null;
    const mean = data.hitters.reduce((sum, hitter) => sum + hitter.cps, 0) / data.hitters.length;
    return {...data, hitters: data.hitters.map(hitter => ({...hitter, cps: hitter.cps - mean + 100}))};
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
  const intro = '<a href="#afl">← AFL Tracker</a><h1>CBS+ Hitter Leaderboard</h1>';
  if (!data) {
    app.innerHTML = intro + '<p role="status">CBS+ data is currently unavailable.</p>';
    return;
  }
  const date = new Date(data.generatedAt);
  const tz = {timeZone: 'America/New_York'};
  const day = new Intl.DateTimeFormat('en-US', {...tz, dateStyle: 'medium'}).format(date);
  const time = new Intl.DateTimeFormat('en-US', {...tz, hour: 'numeric', minute: '2-digit'}).format(date);
  const profiles = new Map(players.map(p => [p.mlbamId, p]));
  const mlbTeam = row => profiles.get(row.mlbamId)?.mlbOrg;
  const teamGroups = [['AFL teams', 'afl', row => row.team], ['MLB teams', 'mlb', mlbTeam]];
  const teamOptions = teamGroups.map(([label, kind, teamOf]) => {
    const teams = [...new Set(data.hitters.map(teamOf).filter(Boolean))].sort();
    return `<optgroup label="${label}">${teams.map(team => `<option value="${esc(kind + ':' + team)}">${esc(team)}</option>`).join('')}</optgroup>`;
  }).join('');
  app.innerHTML = intro + `
    <p>CBS+ evaluates AFL offense in the context of team environment, sample size and the actual pitchers each hitter faced.</p>
    <p class="muted">CBS+ updated ${esc(day)} · ${esc(time)} ET · ${data.completedGames} completed games</p>
    ${data.scope==='regular-season-and-postseason'?`<p class="muted">Regular season + postseason combined · ${data.postseasonGames??0} playoff games · Fall Stars Game excluded.</p>`:''}
    ${data.pitchSourceGeneratedAt ? `<p class="muted">PitchIQ input timestamp: ${esc(data.pitchSourceGeneratedAt.replace('T', ' ').slice(0, 16))} (provider time zone unspecified).</p>` : ''}
    <div class="controls" style="display:flex;align-items:center;flex-wrap:wrap;gap:12px;width:100%;max-width:none"><input style="box-sizing:border-box;height:44px;flex:1 1 280px;min-width:0;max-width:100%;margin:0" id="cps-search" type="search" aria-label="Search CBS+ players" placeholder="Search players…"><select id="cps-team" aria-label="Filter by AFL or MLB team" style="height:44px;max-width:100%;margin:0"><option value="">All teams</option>${teamOptions}</select><label for="cps-sort" style="display:flex;align-items:center;gap:10px;margin:0 0 0 auto"><span>Sort by</span><select id="cps-sort" style="box-sizing:border-box;height:44px;margin:0">${Object.entries(metrics).map(([key, label]) =>
      `<option value="${key}">${label}</option>`).join('')}</select></label></div>
    <div class="tablewrap" role="region" aria-label="CBS+ hitter rankings"><table><thead><tr>
      ${['CBS+ rank', 'Player', 'Age', 'AFL / MLB team', 'PA', 'OPS', 'Pitching Difficulty (OQI)', 'CBS+'].map(label =>
        `<th scope="col">${label}</th>`).join('')}</tr></thead><tbody id="cps-rows"></tbody></table></div>
    <section aria-label="CBS+ and OQI definitions">
      <p><strong>CBS+ (Contextual Batting Score)</strong> measures AFL hitting performance after accounting for team offense, sample size, and the quality of pitching faced. The average qualified AFL hitter scores 100. A 130 is 30 points above average on this scale.</p>
      <p><strong>OQI (Opponent Quality Index)</strong> measures the difficulty of the pitchers a hitter actually faced, weighted by matched plate appearances. A score of 100 is average among qualified hitters. Higher scores indicate tougher pitching.</p>
    </section>
    <details class="afl-method" style="width:100%;max-width:none"><summary>How CBS+ works</summary>
      <p>Pitcher Quality Index (PQI) weights standardized PitchIQ Filth+ (40%), CSW% (20%), whiff rate (15%), chase rate (10%) and K−BB% (15%). Pitch samples are regressed toward league average using pitches ÷ (pitches + 150).</p>
      <p>Official MLB play-by-play identifies the pitcher in each completed plate appearance. OQI weights pitcher PQI by matched plate appearances and scales the result around 100. Higher OQI means tougher opposition. This update matched ${data.matchedPa.toLocaleString()} of ${data.totalPa.toLocaleString()} completed PA.</p>
      <p>The underlying score combines standardized OPS (65%) and relative OPS (35%). Relative OPS is ln(player OPS ÷ team OPS). Offensive reliability rises with sample size and reaches full weight at 60 PA. Above-average opposition adds a modest boost, while softer opposition receives a larger penalty. The board requires 20 official PA and 20 matched PA. Featured hitters require 35 PA and .850 OPS. CBS+ subtracts the mean underlying score of qualified hitters and adds 100.</p>
      <p><strong>CBS+ is an experimental performance-context metric, not an MLB projection or prospect grade.</strong> Sources include PitchIQ pitcher metrics and official MLB AFL hitting statistics and completed-game feeds.</p>
    </details>
    <details class="afl-method" style="width:100%;max-width:none"><summary>How OQI works</summary>
      <p>Official MLB play-by-play identifies the pitcher each hitter faced in every completed plate appearance. Each matched appearance counts once, so pitchers faced more often carry more weight.</p>
      <p>OQI starts with the hitter’s plate-appearance-weighted average Pitcher Quality Index (PQI). PQI uses PitchIQ’s Filth+, called strikes plus whiffs (CSW%), whiff rate, chase rate, and strikeout rate minus walk rate. Smaller pitching samples are pulled toward league average.</p>
      <p>The weighted averages are standardized across qualified hitters and converted to <strong>OQI = 100 + 10 × z-score</strong>. A score of 100 is average, and 110 means the hitter faced pitching one standard deviation tougher than average.</p>
    </details>`;
  const asOf = data.through ?? data.generatedAt.slice(0, 10);
  const hitters = data.hitters.map(row => {
    const dob = profiles.get(row.mlbamId)?.bio?.birthDate;
    const age = /^\d{4}-\d{2}-\d{2}$/.test(dob ?? '') && dob <= asOf
      ? Number(asOf.slice(0, 4)) - Number(dob.slice(0, 4)) - (asOf.slice(5) < dob.slice(5) ? 1 : 0)
      : null;
    return {...row, age};
  });
  const select = app.querySelector('#cps-sort');
  const team = app.querySelector('#cps-team');
  const search = app.querySelector('#cps-search');
  const normalize = value => value.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
  const render = () => {
    const terms = normalize(search.value).trim().split(/\s+/);
    const matches = hitters.filter(row => (!team.value || team.value === 'afl:' + row.team || team.value === 'mlb:' + mlbTeam(row)) && terms.every(term => normalize(row.name).includes(term)));
    app.querySelector('#cps-rows').innerHTML = sortCpsHitters(matches, select.value).map(row => {
      const route = profiles.get(row.mlbamId)?.route;
      const name = route ? `<a href="${esc(route)}">${esc(row.name)}</a>` : esc(row.name);
      return `<tr><td>${row.rank}</td><td>${name}</td><td>${row.age ?? '—'}</td><td>${esc(row.team)}<small>${esc(mlbTeam(row) || '—')}</small></td><td>${row.pa}</td><td>${decimal(row.ops,3)}</td><td>${row.oqi.toFixed(1)}</td><td><strong>${row.cps.toFixed(1)}</strong></td></tr>`;
    }).join('') || '<tr><td colspan="8">No players match your search.</td></tr>';
  };
  team.onchange = render;
  search.oninput = render;
  select.onchange = render;
  render();
}

const cpsIndicatorColors = [
  [126, 35, 41],   // 80 and below
  [191, 78, 42],   // 90
  [211, 163, 37],  // 100
  [143, 159, 46],  // 110
  [48, 133, 67],   // 120
  [62, 177, 62],   // 130 and above
];

function cpsIndicatorColor(score) {
  const position = (Math.min(130, Math.max(80, score)) - 80) / 10;
  const index = Math.min(Math.floor(position), cpsIndicatorColors.length - 2);
  const fraction = position - index;
  const channels = cpsIndicatorColors[index].map((channel, i) =>
    Math.round(channel + fraction * (cpsIndicatorColors[index + 1][i] - channel))
  );
  return `rgb(${channels.join(', ')})`;
}

export function aflCpsTile(data, player) {
  if (player.type !== 'H') return '';
  const score = data?.hitters?.find(row => row.mlbamId === player.mlbamId)?.cps;
  if (!Number.isFinite(score)) return '';
  const displayedScore = score.toFixed(1);
  const value = Number(displayedScore);
  let rating = 'Around average';
  if (value <= 80) rating = 'Poor';
  else if (value < 90) rating = 'Below average';
  else if (value >= 130) rating = 'Exceptional';
  else if (value >= 120) rating = 'Excellent';
  else if (value >= 110) rating = 'Strong';

  const description = `${rating} contextual AFL performance`;
  return `<div class="afl-cps-tile">
    <span>CBS+</span><b>${displayedScore}</b>
    <i class="afl-cps-indicator" role="img" aria-label="${description}" title="${description}" style="background-color:${cpsIndicatorColor(score)}"></i>
  </div>`;
}

export const aflCpsFootnote = '<p class="muted"><small><strong>CBS+</strong> adjusts AFL hitting for playing time, team offense, and the pitchers faced. Among qualified hitters, 100 is average and 130 is 30 index points above average. Scores are available for hitters with at least 20 official and 20 matched plate appearances.</small></p>';
