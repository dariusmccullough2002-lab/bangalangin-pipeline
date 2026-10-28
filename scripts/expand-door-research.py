"""Freeze player-specific editorial interpretation; build-door-watch.py publishes it offline."""
import json
from pathlib import Path
D=Path(__file__).resolve().parents[1]/'docs/door-opportunity-research-20261027'
# Interpretations below use the separately frozen league performance, scouting and roster inputs.
# They are conditional editorial assessments, not collected pitch metrics or club promises.
cases={
'Ryan Sloan': (
 'The strongest part of his case is how often he gets ahead without giving away first base. That makes him more than a radar-gun prospect. The remaining starter test is whether hitters have to respect his whole mix after seeing him once; a low walk total by itself cannot show that the slider works deep into games.',
 'A spot start is the simpler route than an immediate permanent rotation place. Seattle could value his innings even while preferring an established starter over a full season.',
 ['A second reliable secondary pitch would make it harder to sit on his fastball.', 'Compare late-start execution with early innings before assuming he can hold the same quality through a full workload.']),
'Liam Doyle': (
 'Strikeouts show that the fastball can miss bats, but the walks make the route less straightforward than the draft pedigree suggests. If hitters can reject his breaker, he has to return to the fastball in predictable counts. Getting a secondary pitch over for a strike and getting chase with it are different tests; he needs evidence of both.',
 'A short relief look could arrive before a stable rotation assignment. That would demonstrate a narrower MLB use, while leaving the starting-pitcher question open.',
 ['Look for fewer hitter-friendly counts over consecutive starts, rather than one low-walk outing.', 'A better breaker must still work against hitters who have already seen the fastball.']),
'Jamie Arnold': (
 'The five-inning Triple-A line is an introduction, not a readiness verdict. His broader starting workload gives the pitching case substance, but the health interruption changes the order of the questions: first clearance and normal preparation, then strike throwing against advanced hitters. Earlier concerns about fastball location should be retested rather than assumed fixed by one scoreless outing.',
 'If healthy, rotation depth is a plausible first assignment. Without a verified recovery update, a spring roster place should remain conditional.',
 ['Confirm a normal throwing and fielding progression before interpreting spring results.', 'Watch whether fastball strikes create usable counts for the slider, instead of the slider constantly rescuing him.']),
'Carlos Lagrange': (
 'The first-role question is especially important here. A shorter assignment can let the fastball and best secondary play without requiring the same command and endurance as a start. Strong relief work would therefore support a call-up case, but it would not settle whether he can turn over a lineup or keep walks under control over longer outings.',
 'The announced relief experiment gives him a concrete route beyond waiting for a rotation vacancy. The club’s long-term starter view and his near-term bullpen use should be tracked separately.',
 ['Check strike throwing and recovery on a reliever’s schedule.', 'Evaluate changeup use and longer-outing execution separately if the club stretches him back out.']),
'Jack Wenninger': (
 'Triple-A volume makes him a practical next-man-up candidate, but the walk total weakens the claim that he is ready to hold a job. A good splitter can finish hitters only after he earns counts in which they must protect the zone. The useful question is whether the breaker and fastball let him reach those counts consistently.',
 'Spot starts or bulk coverage are more defensible than projecting an immediate regular rotation role. Sustained control improvement would make the assignment easier to retain.',
 ['Look for a repeatable breaker rather than occasional standout pitches.', 'Separate early-season scouting praise from what the later saved walk totals actually show.']),
'Andrew Fischer': (
 'The power is already loud enough to deserve attention; the question is how much survives when pitchers can repeatedly target the contact weakness. Walks help, but they do not cancel empty swings on hittable changeups. Third-base competence matters because shifting to first would raise the offensive standard and place him in the same queue as Burke and Adams.',
 'A share of third-base work is the more useful first role than another first-base-only bat. He must offer enough offense and reliable defense to justify that choice.',
 ['Distinguish strike-zone changeup misses from chases outside the zone.', 'Routine slow-roller decisions matter alongside arm strength and highlight plays.']),
'Luke Adams': (
 'His Triple-A walk and strikeout counts suggest a different profile from the more swing-and-miss-heavy corner bats. The next question is whether that selectivity produces enough damage when MLB pitchers challenge him. A high on-base percentage alone does not create a first-base opening, especially when the incumbent bats have already produced.',
 'Corner-infield reserve work becomes more plausible if third base is usable. If he is limited to first, a transaction or injury is a much larger part of the opportunity case.',
 ['Judge damage on strikes alongside the walk rate, not in place of it.', 'Follow actual third-base assignments and routine-play reliability.']),
'Jesus Made': (
 'A long Double-A season with relatively few strikeouts provides more support for an aggressive promotion than a short hot streak. The distinction is between arm strength and dependable defense: a spectacular throw cannot establish that routine plays are clean. His chance of skipping Triple-A depends on the bat and the available defensive assignment lining up at the same time.',
 'An infield reshuffle or third-base share is easier to explain than assuming second base opens. A debut could precede an everyday shortstop job.',
 ['Keep contact quality as the level improves without giving away swing decisions.', 'Evaluate routine footwork and throwing accuracy across a run of games.']),
'Sebastian Walcott': (
 'Nine Triple-A plate appearances tell us almost nothing about that level. The more useful questions come from his broader return and the dated scouting report: does the bat continue to produce, and can his throwing support a real defensive home? DH production and defensive readiness must be kept separate after an elbow interruption.',
 'A bat-first opportunity needs somewhere to play. An infield injury or a demonstrated alternative position could help; outfield drills alone are not a job offer.',
 ['Follow the number and frequency of defensive innings, not just whether he appears in a lineup.', 'Use a larger advanced-level sample before treating a short burst as a settled MLB offensive projection.']),
'Leo De Vries': (
 'His Double-A record supports the talent case, but the shoulder recovery now takes priority over the depth-chart discussion. An old ETA cannot establish readiness to hit and throw after surgery. Once he resumes games, defensive accuracy and the ability to sustain normal work become more informative than comparing his rank with another healthy prospect.',
 'A later-season infield opportunity is conditional on rehabilitation and subsequent baseball preparation. This is not an Opening Day forecast.',
 ['Obtain a dated club recovery update before moving the expected window earlier.', 'Reassess throwing and game workload after the return rather than carrying pre-injury assumptions forward.']),
'Caleb Bonemer': (
 'Power gives Chicago a reason to explore ways to fit the bat, and the announced center-field trial makes that exploration concrete. Learning a position is still different from being ready to play it in MLB. The offensive checkpoint remains whether added damage holds up when pitchers challenge the upper-away area and change speeds.',
 'A multi-position role could be a bridge to more at-bats. Center-field reps add an option; they do not prove he has displaced an established outfielder.',
 ['Track actual center-field reads, routes and throwing decisions, not just assignment announcements.', 'Look for better contact against the specific pitches identified in the older scouting report.']),
'Charlie Condon': (
 'A full Triple-A workload is a meaningful proximity signal. Still, a strong slugging line in that environment cannot answer the specific concern about recognizing spin. The next useful evidence would show whether he can damage mistakes while refusing breaking balls that finish outside the zone, with the same approach away from favorable hitting conditions.',
 'A corner-outfield share makes more sense than assuming first base is free. A club can test the bat in a partial role before offering everyday work.',
 ['Separate park-driven production from contact and swing decisions.', 'Check whether breaking-ball recognition holds when pitchers stop offering fastballs in predictable counts.']),
'Ralphy Velazquez': (
 'The Triple-A combination of power and manageable strikeouts makes the offensive case more tangible than raw-power grades alone. But first base demands continued production, and several alternatives already occupy that lane. A second playable position would matter because it could let the club keep his bat without making one irreversible choice at first.',
 'First-base competition is plausible; occasional corner-outfield work would expand the ways to get him into the lineup. Neither route removes the need to outperform the existing options.',
 ['Maintain contact and damage when pitchers change their two-strike approach.', 'Confirm usable outfield routes over real games before counting that versatility as established.']),
'Franklin Arias': (
 'The Triple-A contact record gives his readiness case a firmer base than a reputation for defense alone. The important development question is whether the extra power can coexist with that contact as pitchers adjust. Boston’s infield alternatives mean a promotion decision still depends on how much offense and defensive reliability he can provide together.',
 'Shortstop competition or a flexible infield role could get him started. Strong minor-league production does not by itself establish which incumbent the club would move.',
 ['Watch whether power remains when opponents attack him with better velocity.', 'Preserve routine defensive execution as the game speeds up.']),
'Theo Gillen': (
 'His Double-A contact and power provide more support than a High-A breakout alone. The unresolved piece is whether the swing remains controlled against more advanced sequencing while his center-field defense develops. If he cannot stay in center, the offensive standard rises and the range of realistic openings narrows.',
 'An outfield share becomes easier to justify if he can cover center reliably. A direct Double-A jump would require both the bat and that defensive assignment to be ready.',
 ['Look for a steadier head and balanced contact against changing speeds.', 'Review first steps and routes in center rather than equating speed with finished defense.']),
'Nelson Rada': (
 'A long Triple-A season supports proximity, but the limited extra-base production changes the kind of role he needs. His value to an MLB bench could come through center-field coverage, contact and useful baserunning. That is a credible debut route without claiming that low power automatically plays in an everyday lineup.',
 'Defense, pinch-running and selected starts are a more modest first use than an immediate full-time job. Keeping that job requires creating value without costly outs on the bases.',
 ['Measure successful decisions on the bases, not stolen-base attempts alone.', 'Check whether contact remains useful against MLB-quality velocity rather than merely putting weak balls in play.']),
'Max Anderson': (
 'His Triple-A strikeout and walk counts make the offensive case worth testing. The remaining concern is whether an aggressive hitter with a late load can still choose and reach pitches he can drive when the velocity improves. Defensive range also affects whether he can fit as a flexible reserve instead of needing a dedicated starting position.',
 'A bench-infield upgrade is easier to see than a clear everyday opening. Showing he can handle more than one assignment would help the club fit the bat.',
 ['Review contact against firm pitches separately from the overall batting average.', 'Follow usable second- and third-base work rather than treating a position listing as proof of versatility.']),
'Parks Harber': (
 'His shorter Triple-A sample has not carried the same obvious impact as his raw-power reputation. That is a reason to ask for evidence, not to discard the tools. Closing early with the hips could make soft stuff away and premium velocity difficult to cover together; better timing must show up without requiring him to guess one pitch.',
 'Third-base depth is the cleaner route than a first-base or DH role behind established bats. A bench opportunity would still require useful offense on irregular starts.',
 ['Look for contact through the outer half without losing the ability to turn on velocity.', 'Keep third-base play reliable enough that the club does not have to find a bat-only slot.']),
'James Tibbs III': (
 'A full Triple-A season with both walks and power is a substantial offensive record. The obstacle is fit, not simply whether he has reached the right level. His corner profile competes with established bats, and fair defense gives him fewer reserve uses than a true center fielder. Results against premium velocity and good left-handers are the next useful differentiators.',
 'A corner-outfield share or injury replacement is more plausible than taking a regular DH or first-base role immediately. Everyday work would need an opening and enough offense to hold it.',
 ['Separate production against strong left-handers from the overall line.', 'Show dependable corner defense while maintaining damage against premium fastballs.']),
'Enrique Bradfield Jr.': (
 'His path is less dependent on home runs than most players here. Center-field defense and speed can create a reserve use, but the bat still has to keep opponents from exploiting low strikes. A useful adjustment would turn those pitches into better contact without sacrificing the disciplined approach that helps him reach base.',
 'Defensive coverage, pinch-running and selective starts are plausible first assignments. That is different from forecasting enough offense to play every day.',
 ['Review low-zone contact quality instead of asking only for more lift everywhere.', 'Confirm sustained availability; past hamstring trouble is context, not proof of a current injury.']),
'Blake Burke': (
 'The Triple-A sample is still modest, but the combination of strikeouts and limited damage is a real warning for a first-base-only route. A future promotion case needs improvement in the exact area the role demands: hitting enough to justify a bat-first roster place. Adding another position to a label would not solve that standard.',
 'First-base depth is possible after better offensive evidence or a roster change. There is little basis here for assuming an immediate upgrade over the current left-handed option.',
 ['Ask whether he can reach high-end fastballs without losing coverage of slower pitches.', 'Test the approach against left-handers before assuming a full-time role.']),
'Alfredo Duno': (
 'The Double-A line is encouraging, but a catcher’s promotion also requires trust behind the plate. Backup work could expose him to MLB pitching while offering too few starts to develop receiving and contact. The club has to balance that short-term role against the value of regular catching repetitions in the minors.',
 'Catching depth is a possible route, but an everyday minor-league assignment may remain more useful than a lightly used MLB bench role. A move to DH would create different competition.',
 ['Check receiving consistency through repeated starts, not one throwing highlight.', 'Revisit elevated-fastball contact with current data; the older contact percentage is not a fresh measurement.']),
'Mike Sirota': (
 'Nine Triple-A plate appearances cannot establish readiness. His impact on contact is promising, but the older report’s in-zone misses ask whether he can get to that impact often enough. Center-field reliability is particularly valuable because it could create a reserve role even when the corner bats and DH position are occupied.',
 'A flexible outfield reserve is the narrower first route. A regular corner job would require a stronger offensive case and a change in the existing lineup.',
 ['Check timing and contact on strikes before treating hard-hit contact as a complete hitting profile.', 'Confirm center-field routes across real innings and sustained availability after the earlier knee interruption.']),
'Rainiel Rodriguez': (
 'A substantial Double-A power line makes the bat difficult to ignore. The catcher label adds opportunity only if the receiving and throwing can handle the assignment. Moving him away from catching could speed access to at-bats but would also change the positional competition and the offensive threshold he has to clear.',
 'A catching opportunity requires passing other young options, not merely comparing his bat with an incumbent’s OPS. First base is a separate route that should not be counted as an automatic fallback.',
 ['Watch outer-half breaking-ball contact and popup frequency together.', 'Review receiving over a sustained catching workload, including ordinary blocking and throwing decisions.']),
'Eli Willits': (
 'Seventeen Double-A plate appearances are evidence of an aggressive assignment, not proof that advanced pitching is solved. His contact and defense can support a fast rise, but an immediate MLB projection would need more evidence that he can drive firm pitches. A path requiring another player to change positions also needs an actual club decision.',
 'An infield reshuffle is possible, but a longer advanced-level assignment is a reasonable next step. His age and rank should not be converted directly into an Opening Day prediction.',
 ['Look for timely extra-base contact on fastballs without a rise in empty swings.', 'Wait for a meaningful advanced-level sample before treating the first good games as the new baseline.']),
'Aidan Miller': (
 'The highest-level sample is far too small to grade the comeback. Getting back into games is encouraging, but repeated availability matters before drawing conclusions from the bat or glove. Only after normal work resumes can the club judge whether the old outer-half breaking-ball and routine-throwing concerns have improved.',
 'Infield depth or third-base competition is conditional on health and sustained preparation. A return announcement alone is not confirmation that he is ready for a full MLB season.',
 ['Confirm consecutive healthy game workloads rather than relying on a single rehab appearance.', 'Recheck swing coverage and routine defensive accuracy after that workload is established.']),
'Jarlin Susana': (
 'The brief Triple-A line is not a starter-readiness sample. His first MLB use could depend more on how much healthy work he can handle than on the maximum velocity. A fastball/slider combination may support shorter assignments before the changeup and command can support a rotation job; those are two different milestones.',
 'Shorter relief or managed depth innings could precede a regular starting role. The Fall League is useful follow-up evidence, but it should not be folded into regular-season totals.',
 ['Watch recovery between outings and a gradual increase in usable workload.', 'Check strikes and third-pitch execution separately from velocity peaks.']),
'Jaxon Wiggins': (
 'The Triple-A walks are a larger obstacle than the strikeout total alone reveals. Falling behind can force a powerful fastball into predictable situations, while uneven breaker feel limits his escape route. Health and command therefore have to improve together: a single electric outing does not establish either durability or a repeatable starting role.',
 'Managed depth innings are more defensible than a guaranteed rotation job. Shorter work could be an option, but it would need evidence of effective strikes rather than simply a new role label.',
 ['Look for consecutive healthy outings with fewer free passes.', 'Check whether the breaker can earn early strikes as well as finish hitters.']),
'Kemp Alderman': (
 'Raw impact gives him a reason to stay in the conversation, but the Triple-A strikeout total shows why the contact question cannot be skipped. Pitchers who can use soft stuff away and then beat him with a fastball may prevent him from reaching that power. As a corner bat, he has fewer ways to earn a reserve role through defense alone.',
 'Part-time power or injury coverage is a narrower first use than a vacant everyday corner job. A stable role needs more contact without giving away his damage.',
 ['Separate chase below and away from misses on strikes.', 'Look for earlier fastball timing without guessing so aggressively that breaking balls become easier to exploit.']),
'Brandon Clarke': (
 'Four Double-A innings are an introduction, even with an encouraging strikeout-to-walk result. The bigger question is whether he can repeat his delivery and recover through a sustained run of outings. A well-located slider does not remove the need to establish fastball strikes, especially when a small sample can hide occasional wild misses.',
 'A managed pitching-depth route is more defensible than an immediate full-season rotation claim. He and Doyle are competing for the same future innings, not separate guaranteed vacancies.',
 ['Build repeated healthy outings before extrapolating the first Double-A result.', 'Check fastball misses and free baserunners separately from the quality of the slider.'])
}
assert len(cases)==30
role_headings={'Ryan Sloan': 'Spot starts in a crowded rotation', 'Liam Doyle': 'A bullpen look while the starter case develops', 'Jamie Arnold': 'Healthy innings come before rotation depth', 'Carlos Lagrange': 'The bullpen experiment opens another door', 'Jack Wenninger': 'Spot starts and bulk innings', 'Andrew Fischer': 'Third base offers the better opening', 'Luke Adams': 'Third-base defense broadens his options', 'Jesus Made': 'An infield reshuffle could create room', 'Sebastian Walcott': 'Finding a position for the bat', 'Leo De Vries': 'Rehabilitation sets the timetable', 'Caleb Bonemer': 'Center field adds a possible route', 'Charlie Condon': 'A share of the corner-outfield work', 'Ralphy Velazquez': 'First-base competition, with an outfield option', 'Franklin Arias': 'Shortstop competition or infield flexibility', 'Theo Gillen': 'Center-field defense could help the bat fit', 'Nelson Rada': 'Defense and speed offer a foothold', 'Max Anderson': 'Making room on the infield bench', 'Parks Harber': 'Third-base depth is the cleaner fit', 'James Tibbs III': 'A corner-outfield opening to earn', 'Enrique Bradfield Jr.': 'A route through defense and baserunning', 'Blake Burke': 'First-base depth still needs an opening', 'Alfredo Duno': 'Catching reps or a place on the MLB bench?', 'Mike Sirota': 'Outfield versatility could unlock reserve work', 'Rainiel Rodriguez': 'Passing the other young catching options', 'Eli Willits': 'Advanced-level reps before an infield opening', 'Aidan Miller': 'Health comes before third-base competition', 'Jarlin Susana': 'Managed innings as the starting case develops', 'Jaxon Wiggins': 'Effective strikes must support the workload', 'Kemp Alderman': 'Power off the bench or injury coverage', 'Brandon Clarke': 'Building innings before claiming a rotation place'}
players=[{'name':name,'assessment':a,'firstRole':r,'firstRoleHeading':role_headings[name],'checkpoints':c} for name,(a,r,c) in cases.items()]
(D/'Deep_Research.json').write_text(json.dumps({'asOf':'2026-10-27','interpretationLabel':'Our assessment — conditional on the dated evidence below','players':players},indent=2,ensure_ascii=False)+'\n')
print('Saved 30 individual research interpretations')
