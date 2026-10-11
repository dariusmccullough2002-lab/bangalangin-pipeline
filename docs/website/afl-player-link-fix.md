# AFL player link correction

The old aflCard used prospectRankUrl when available, otherwise https://www.prospect-portfolio.com/afl. That fallback is a hitter listing, including on pitcher pages. The AFL-specific profile sidebar independently linked to the same generic external listing.

The tracker action now opens Pipeline's existing #afl-player/MLBAM-ID route, which contains the named player's separate AFL performance. It is not represented as a verified external ProspectRank pitcher URL. All251 full-roster IDs were checked against the route handler and unique roster membership (152P,99H). The30 prospect-card participants each exist in the full roster. Generic resource-board links remain explicitly boards, not player actions.

Names/accents/team/position are not used to choose the destination. A unique stable MLBAM ID is required; duplicate or unsupported IDs show unavailable with no href. Two-way eligibility cannot change the ID. The snapshot has no verified two-way players, so two-way identity behavior is exercised with a fixture, not a claimed live two-way AFL assignment.

Regression coverage includes Jarlin Susana (703186) pitching, every251 destination, name/accent variants, ambiguous IDs, missing profiles, and existing inline stat behavior. Existing source identity checks in aflParticipant remain. These player-link changes do not alter AFL statistics, roster data, rankings, projection models or valuation inputs.
