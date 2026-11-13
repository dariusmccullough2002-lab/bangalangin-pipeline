import {mkdir, readFile, rename, writeFile} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {pathToFileURL} from 'node:url';
import {calculatePitcherOqi} from './pitcher-oqi.mjs';
import {AFL_GAME_TYPES, combineAflStats} from '../afl-season-stats.js';

const MLB = 'https://statsapi.mlb.com/api/v1';
const pitchUrl = 'https://api.prospecttilt.com/afl_leaderboard.json';
const season = 'season=2026&leagueIds=119&sportIds=17';
export const includedAflGames = schedule => schedule.dates.flatMap(d => d.games.filter(g =>
  AFL_GAME_TYPES.includes(g.gameType) && g.status.abstractGameState === 'Final' &&
  !['Cancelled', 'Postponed', 'Suspended'].includes(g.status.detailedState)
).map(g => ({id:g.gamePk,date:d.date,gameType:g.gameType})));
const components = [
  ['filth_plus', .40], ['csw_pct', .20], ['whiff_pct', .15], ['chase_pct', .10], ['kMinusBB', .15]
];
// These official play results end a PA. Runner-only events can end an inning
// without completing the batter's turn and must never enter the matchup counts.
const plateEvents = new Set([
  'field_out', 'strikeout', 'walk', 'intent_walk', 'single', 'double', 'triple',
  'home_run', 'hit_by_pitch', 'force_out', 'grounded_into_double_play', 'field_error',
  'sac_fly', 'sac_bunt', 'fielders_choice', 'fielders_choice_out', 'double_play',
  'triple_play', 'strikeout_double_play', 'sac_fly_double_play', 'sac_bunt_double_play',
  'catcher_interf', 'batter_interference', 'other_out'
]);
const round = (value, places) => Number(value.toFixed(places));
function standardize(values) {
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  const sd = Math.sqrt(values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / values.length);
  return value => sd > 0 ? (value - mean) / sd : 0;
}

export function gamePaEvents(feed,gameTeams) {
  if (!Array.isArray(feed.allPlays)) throw Error('Invalid MLB play-by-play');
  const entries = [];
  for (const play of feed.allPlays) {
    if (!play.about?.isComplete || !plateEvents.has(play.result?.eventType)) continue;
    let batter = play.matchup?.batter?.id;
    const pitcher = play.matchup?.pitcher?.id;
    // A substitute who inherits two strikes does not receive the PA when the
    // turn ends in a strikeout. Match the officially charged batter, including
    // successive substitutions, rather than the feed's final matchup name.
    if (['strikeout', 'strikeout_double_play'].includes(play.result.eventType)) {
      for (const event of [...(play.playEvents ?? [])].reverse()) {
        if (event.details?.eventType === 'offensive_substitution' && event.count?.strikes >= 2 &&
            event.player?.id === batter && Number.isSafeInteger(event.replacedPlayer?.id)) {
          batter = event.replacedPlayer.id;
        }
      }
    }
    if (!Number.isSafeInteger(batter) || !Number.isSafeInteger(pitcher)) throw Error('Completed PA lacks MLBAM IDs');
    const team=gameTeams?.[play.about.isTopInning?'away':'home']?.team?.id??null;
    const shiftAward=play.result.eventType==='field_error'&&play.playEvents?.some(e=>e.details?.violation?.type==='defensive_shift');
    entries.push([batter,pitcher,team,shiftAward?'defensive_shift_violation':play.result.eventType]);
  }
  if (!entries.length) throw Error('Final AFL game has no completed plate appearances');
  return entries;
}
export function gameMatchups(feed) {
  const counts=new Map();
  for(const [batter,pitcher] of gamePaEvents(feed)){
    const key=batter+':'+pitcher;counts.set(key,(counts.get(key)??0)+1);
  }
  return [...counts].map(([key,count])=>[...key.split(':').map(Number),count]);
}

export function calculateCps(games, pitch, hitting, teams) {
  const actualPitchers = new Set(games.flatMap(g => g.matchups.map(([, pitcher]) => pitcher)));
  const pitchers = pitch.filter(p => actualPitchers.has(p.pitcher_id) && Number.isFinite(p.pitches) && p.pitches > 0)
    .map(p => ({...p, kMinusBB: Number.isFinite(p.k_pct) && Number.isFinite(p.bb_pct) ? p.k_pct - p.bb_pct : null}))
    .filter(p => components.every(([key]) => Number.isFinite(p[key])));
  if (pitchers.length < 2 || new Set(pitchers.map(p => p.pitcher_id)).size !== pitchers.length) throw Error('Missing or duplicate AFL PitchIQ inputs');
  const metrics = components.map(([key, weight]) => [key, weight, standardize(pitchers.map(p => p[key]))]);
  const pqi = new Map(pitchers.map(p => [p.pitcher_id,
    metrics.reduce((sum, [key, weight, z]) => sum + weight * z(p[key]), 0) * p.pitches / (p.pitches + 150)]));
  const matchups = new Map();
  for (const game of games) for (const [batter, pitcher, count] of game.matchups) {
    const row = matchups.get(batter) ?? {total: 0, matched: 0, quality: 0};
    row.total += count;
    if (pqi.has(pitcher)) {
      row.matched += count;
      row.quality += count * pqi.get(pitcher);
    }
    matchups.set(batter, row);
  }
  const totalPa = [...matchups.values()].reduce((sum, row) => sum + row.total, 0);
  const matchedPa = [...matchups.values()].reduce((sum, row) => sum + row.matched, 0);
  if (matchedPa < totalPa * .8) throw Error('PitchIQ matched fewer than 80% of completed PA');
  const teamOps = new Map(teams.map(row => [row.team.id, Number(row.stat.ops)]));
  const rows = hitting.flatMap(row => {
    const id = row.player.id, match = matchups.get(id), pa = Number(row.stat.plateAppearances);
    const ops = Number(row.stat.ops), team = teamOps.get(row.team?.id);
    if (pa < 20 || !match || match.matched < 20 || !(ops > 0) || !(team > 0)) return [];
    return [{mlbamId: id, name: row.player.fullName, team: row.team.name, pa, ops, teamOps: team,
      relativeOps: Math.log(ops / team), matchedPa: match.matched, oqiRaw: match.quality / match.matched}];
  });
  if (!rows.length) throw Error('No qualified AFL hitters in the inputs');
  const zOps = standardize(rows.map(r => r.ops)), zRelative = standardize(rows.map(r => r.relativeOps));
  const zOpponent = standardize(rows.map(r => r.oqiRaw));
  const hitters = rows.map(({oqiRaw, ...r}) => {
    const opponent = zOpponent(oqiRaw);
    const offense = (.65 * zOps(r.ops) + .35 * zRelative(r.relativeOps)) * Math.min(1, Math.sqrt(r.pa / 60));
    return {...r, oqi: 100 + 10 * opponent, cps: 100 + 15 * (offense + (opponent >= 0 ? .30 : .45) * opponent)};
  }).sort((a, b) => b.cps - a.cps || b.ops - a.ops || a.mlbamId - b.mlbamId)
    .map((r, index) => ({...r, rank: index + 1, relativeOps: round(r.relativeOps, 4), oqi: round(r.oqi, 3), cps: round(r.cps, 3)}));
  return {hitters, totalPa, matchedPa, pitcherCount: pitchers.length};
}

async function fetchJson(url) {
  let lastError;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const response = await fetch(url, {signal: AbortSignal.timeout(30000)});
      if (!response.ok) throw Error('HTTP ' + response.status);
      return await response.json();
    } catch (error) {
      lastError = error;
    }
  }
  throw Error(url + ': ' + lastError.message);
}
const splits = payload => {
  const group = payload.stats?.find(g => g.group?.displayName === 'hitting');
  if (!group?.splits?.length || group.splits.length < (group.totalSplits ?? 0)) throw Error('Incomplete MLB hitting stats');
  return group.splits;
};
async function atomicJson(path, value, spaces=0) {
  await writeFile(path + '.tmp', JSON.stringify(value,null,spaces) + '\n');
  await rename(path + '.tmp', path);
}

async function refresh() {
  const fixtures = process.env.AFL_CPS_FIXTURES;
  const get = async (name, url) => {
    if(fixtures)return JSON.parse(await readFile(join(fixtures,name+'.json'),'utf8'));
    const value=await fetchJson(url);
    if(process.env.AFL_CPS_CAPTURE){const path=join(process.env.AFL_CPS_CAPTURE,name+'.json');await mkdir(dirname(path),{recursive:true});await atomicJson(path,value);}
    return value;
  };
  const [schedule, pitch, hitterPayloads, teamPayloads] = await Promise.all([
    get('schedule', MLB + '/schedule?sportId=17&leagueId=119&season=2026'),
    get('pitch', pitchUrl),
    Promise.all(AFL_GAME_TYPES.map(type=>get('players-'+type, MLB + '/stats?stats=season&group=hitting,pitching&' + season + '&gameType='+type+'&playerPool=ALL&limit=1000'))),
    Promise.all(AFL_GAME_TYPES.map(type=>get('teams-'+type, MLB + '/teams/stats?stats=season&group=hitting&' + season + '&gameType='+type+'&limit=100')))
  ]);
  const hitting=combineAflStats(hitterPayloads),teams=combineAflStats(teamPayloads,{teamStats:true});
  const included=includedAflGames(schedule);
  const finals = new Map(included.map(g=>[g.id,g.date]));
  const gameTypes=new Map(included.map(g=>[g.id,g.gameType]));
  const gameTeams=new Map(schedule.dates.flatMap(d=>d.games.map(g=>[g.gamePk,g.teams])));
  const cachePath = 'data/afl/cps-matchups-2026.json';
  const previous = await readFile(cachePath, 'utf8').then(JSON.parse).catch(error => {
    if (error.code !== 'ENOENT') throw error;
    return [];
  });
  // The closing audit can re-read completed feeds to capture later scoring corrections.
  const cached = process.env.AFL_CPS_REVALIDATE === '1' ? new Map() : new Map(previous.filter(game=>Array.isArray(game.plateAppearances)).map(game => [game.id, game]));
  if (previous.some(game => !finals.has(game.id))) throw Error('MLB schedule lost previously ingested final games');
  const games = [...finals].flatMap(([id]) => cached.has(id) ? [{...cached.get(id),gameType:gameTypes.get(id)}] : []);
  const missing = [...finals].filter(([id]) => !cached.has(id));
  for (let i = 0; i < missing.length; i += 8) {
    games.push(...await Promise.all(missing.slice(i, i + 8).map(async ([id,date])=>{
      const feed=await get('games/'+id,MLB+'/game/'+id+'/playByPlay');
      return {id,date,gameType:gameTypes.get(id),matchups:gameMatchups(feed),plateAppearances:gamePaEvents(feed,gameTeams.get(id))};
    })));
  }
  const teamRows = splits(teams);
  if (teamRows.length !== 6) throw Error('Expected six official AFL team lines');
  const hitterRows = splits(hitting);
  const result = calculateCps(games, pitch.pitchers, hitterRows, teamRows);
  const officialPa = teamRows.reduce((sum, row) => sum + row.stat.plateAppearances, 0);
  if (officialPa !== result.totalPa) {
    throw Error(`Official team stats and final-game matchups are out of sync (${officialPa} vs ${result.totalPa} PA)`);
  }
  const batterPa=new Map();
  for(const game of games)for(const [batter,,count] of game.matchups)batterPa.set(batter,(batterPa.get(batter)??0)+count);
  if(hitterRows.some(r=>(batterPa.get(r.player.id)??0)!==r.stat.plateAppearances))throw Error('Official hitter PA totals and game matchups disagree');
  const pitchingRows=hitting.stats.find(g=>g.group?.displayName==='pitching')?.splits??[];
  const pitcherOqi=calculatePitcherOqi(games,hitterRows,pitchingRows);
  const dataset = {generatedAt: new Date().toISOString(), version: 'CPS_v1', status: 'complete',
    scope: 'regular-season-and-postseason', gameTypes:AFL_GAME_TYPES,
    regularSeasonGames:games.filter(g=>g.gameType==='R').length,
    postseasonGames:games.filter(g=>g.gameType!=='R').length, pitchSourceGeneratedAt: pitch.generated ?? null,
    completedGames: games.length, through: [...finals.values()].sort().at(-1), ...result,pitcherOqi};
  await mkdir('data/afl', {recursive: true});
  await atomicJson(cachePath, games.sort((a, b) => a.id - b.id));
  await atomicJson('data/afl/cps-2026.json', dataset);
  // The homepage, tracker and player profiles share this combined fallback.
  const fullPath='data/afl/full-2026.json';
  const full=JSON.parse(await readFile(fullPath,'utf8'));
  full.statsSnapshot=hitting;full.statsRetrievedAt=dataset.generatedAt;
  full.statsScope=dataset.scope;full.statsGameTypes=AFL_GAME_TYPES;
  await atomicJson(fullPath,full,2);
  console.log(`CPS refreshed: ${games.length} games, ${result.matchedPa}/${result.totalPa} matched PA, ${result.hitters.length} qualified hitters`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  refresh().catch(error => {
    console.error('AFL CPS refresh failed. Keep the previous published dataset.', error);
    process.exitCode = 1;
  });
}
