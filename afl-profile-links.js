// ProspectRank profiles verified by MLBAM ID and page name on 2026-10-13.
const verifiedProspectRankIds=new Set([695484, 834962, 815352, 815793, 804560, 815792, 701333, 827665, 702695, 808234, 686944, 806061, 703177, 703637, 826928, 816111, 815608, 700321, 682625, 692110, 828076, 702679, 691942, 829643, 703606, 800195, 695494, 814414, 823918, 808277, 687766, 703449, 695493, 807957, 703160, 805795, 825412, 800169, 800051, 805951, 804871, 828202, 695517, 695573, 807276, 804966, 683149, 800607, 702619, 702265, 806964, 687930, 806988, 805799, 815520, 804911, 800614, 702607, 807275, 800724, 702518, 807726, 809763, 701592, 687783, 800440, 807083, 806441, 823809, 800294, 814307, 801932, 695722, 822578, 694806, 801629, 800176, 807728, 702610, 813664, 700815, 803679, 806191, 829210, 701689, 691398, 801590, 702995, 805796, 829052, 813833, 696286, 814457, 834404, 827719, 829040, 820835, 702517, 805801, 695301]);
// MLBAM is the identity key; names, accents, position and listed team may change.
// No name-only fallback: duplicate names never select somebody else's profile.
export function aflProfileDestination(player, roster) {
 const id=Number(player?.mlbamId);
 if (!Number.isSafeInteger(id)||id<=0||roster?.season!==2026) return null;
 const matches=roster.players.filter(row=>row.mlbamId===id);
 if(matches.length!==1)return null;
 if(!verifiedProspectRankIds.has(id))return null;
 const route=`https://www.prospect-portfolio.com/player/mlb_${id}`;
 return route;
}
export function aflProfileLink(player, roster) {
 const route=aflProfileDestination(player,roster);
 return route?`<a href="${route}" target="_blank" rel="noopener noreferrer"><u>ProspectRank — player profile ↗</u></a>`:'<span class="muted">ProspectRank player profile unavailable.</span>';
}
