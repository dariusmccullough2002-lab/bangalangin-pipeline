// MLBAM is the identity key; names, accents, position and listed team may change.
// No name-only fallback: duplicate names never select somebody else's profile.
export function aflProfileDestination(player, roster) {
 const id=Number(player?.mlbamId);
 if (!Number.isSafeInteger(id)||id<=0||roster?.season!==2026) return null;
 const matches=roster.players.filter(row=>row.mlbamId===id);
 if(matches.length!==1)return null;
 const route=`#afl-player/${id}`;
 return route;
}
export function aflProfileLink(player, roster) {
 const route=aflProfileDestination(player,roster);
 return route?`<a href="${route}"><u>Prospect AFL Tracker — player profile →</u></a>`:'<span class="muted">Prospect AFL Tracker profile unavailable.</span>';
}
