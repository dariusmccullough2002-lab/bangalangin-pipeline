// DD supplies the baseline. Missing supporting lists never acquire extra weight.
export const weights = Object.freeze({dd: .60, pl: .15, fg: .10, jb: .10, ba: .05});
export function rankEquivalent(ranks) {
  if (!Object.values(ranks).some(Number.isFinite)) return null;
  const baseline = ranks.dd ?? 501;
  let score = Math.log(baseline);
  for (const [source, weight] of Object.entries(weights)) {
    if (source === 'dd' || !Number.isFinite(ranks[source])) continue;
    const difference = Math.log(ranks[source] / baseline);
    score += weight * Math.max(-Math.log(2), Math.min(Math.log(2), difference));
  }
  return Math.round(Math.exp(score) * 1e6) / 1e6;
}
