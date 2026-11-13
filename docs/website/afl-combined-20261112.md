# Combined AFL regular-season and postseason coverage

The website now uses one combined view for the homepage, AFL tracker, inline player stats and CBS+. Included MLB game types: R, D, L, W. Fall Stars/exhibition types remain excluded. The archived regular-season closing files are unchanged.

MLB does not aggregate a comma-separated gameType list in the tested stats endpoint. The shared browser/Node helper fetches each type separately, adds counting stats by MLBAM identity (team ID for team lines), and recomputes batting rates, ERA and WHIP. Innings are summed as outs. CBS+ is recalculated from combined offense, team offense and completed-game matchups rather than averaging scores. Existing sample thresholds and roster membership are preserved. Feed failure/truncation retains prior data rather than silently dropping postseason production.

The daily CBS+ workflow also saves the combined fallback stats. The existing refresh schedule remains active. PitchIQ is used as supplied, with its generation timestamp visible; the provider has not confirmed a postseason through-date, so no claim is made that its latest pitching-quality inputs include the playoff game.

Validation: 27 focused tests pass, including unequal-sample rates, decimal-innings handling, all four game types, postseason-only players, exhibition exclusion and partial-feed failures. The broader AFL suite has 33 passes and one pre-existing ProspectRank verification-test failure; that failure was reproduced on the unmodified HEAD snapshot, and all player roster records are unchanged. Production build passes.

Refresh evidence: {
  "generatedAt": "2026-11-13T00:39:53.155Z",
  "through": "2026-11-12",
  "scope": "regular-season-and-postseason",
  "regularSeasonGames": 85,
  "postseasonGames": 1,
  "completedGames": 86,
  "totalPa": 6862,
  "matchedPa": 6862,
  "pitchSourceGeneratedAt": "2026-11-12T09:32:28.336647"
}
