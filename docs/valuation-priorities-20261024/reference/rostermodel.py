"""OFFLINE roster-aware candidate. Not wired to production.

Per-asset value v (display under a chosen scale treatment) is split into
  c = v * s   near-term lineup contribution (s = first-3-season share of discounted expected utility)
  l = v - c   long-run asset value, retained in ANY roster slot (active/reserve/minors/IR)
Team value V*(roster) = best legal arrangement of: 22 active slots (position-eligible optimal assignment),
reserve (11), minors (30, Minors-group proxy only), IR (8, any player). Value counted:
  owned, in lineup : l + c            owned, benched : l + rho*c          owned, dropped : 0
  free-agent add (only if it fills a lineup slot and capacity/legality allows): c   (FAs are non-scarce: no asset value)
Forced drops/adds come out of the legality loop, lowest retention loss first.
Trade delta for a team = V*(after) - V*(before) + net pick value (picks never consume a slot unless cfg['pick_slots']=='2027').
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import *
from scipy.optimize import linear_sum_assignment, milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix

DEFAULT = dict(treatment='shipped', rho=0.25, fa_excl=0.10, fa_on=True, ir_any=True, pick_slots='none')
SLOT_INDEX = {}
for j, s in enumerate(SLOTS):
    SLOT_INDEX.setdefault(s, []).append(j)

def build_records(d, vmap):
    recs = {}
    for a in d['assets']:
        if is_pick(a):
            recs[a['id']] = dict(id=a['id'], name=a['name'], owner=a['owner'], pick=True, val=vmap[a['id']], group=a['group'],
                                 year=a['audit']['year'], rnd=a['audit']['round'])
            continue
        v = vmap[a['id']]; s = near_term_share(a); c = v * s
        recs[a['id']] = dict(id=a['id'], name=a['name'], owner=a['owner'], pick=False, val=v, s=s, c=c, l=v - c,
                             elig=slot_eligibility(a), minors=minors_eligible(a), group=a['group'], pitcher=is_pitcher(a))
    return recs

def fa_pool(recs, cfg):
    if not cfg['fa_on']:
        return []
    fas = [r for r in recs.values() if not r['pick'] and r['owner'] == 'Free agent' and r['group'] in ('MLB', 'Minors')]
    fas.sort(key=lambda r: -r['val'])
    fas = fas[int(len(fas) * cfg['fa_excl']):]          # assume the most valuable FAs are not truly obtainable
    keep = {}
    for bucket, n in (('P', 25), ('C', 10), ('1B', 10), ('2B', 10), ('3B', 10), ('SS', 10), ('OF', 15), ('UT', 10)):
        rs = sorted([r for r in fas if bucket in r['elig']], key=lambda r: -r['c'])[:n]
        for r in rs:
            keep[r['id']] = r
    return list(keep.values())

def lineup(players):
    """Optimal assignment to the 22 slots maximising sum of c. Returns set of ids in lineup."""
    cand = [p for p in players if p['c'] > 1e-9 and p['elig']]
    if not cand:
        return set()
    M = np.zeros((len(cand), len(SLOTS)))
    for i, p in enumerate(cand):
        for s in p['elig']:
            for j in SLOT_INDEX.get(s, []):
                M[i, j] = -p['c']
    ri, ci = linear_sum_assignment(M)
    return {cand[i]['id'] for i, j in zip(ri, ci) if M[i, j] < 0}

def legal(kept, L, cfg):
    bench = [p for p in kept if p['id'] not in L]
    nel = sum(1 for p in bench if p['minors'])
    need = (len(bench) - nel) + max(0, nel - CAP['minors'])
    return need <= CAP['reserve'] + (CAP['ir'] if cfg['ir_any'] else 0) + cfg.get('slack', 0)

def _score(owned, pool, excluded, cfg):
    P = owned + [f for f in pool if f['id'] not in excluded]
    L = lineup(P)
    v = 0.0
    for p in owned:
        v += p.get('l', p['val']) + (p.get('c', 0.0) if p['id'] in L else cfg['rho'] * p.get('c', 0.0))
    for f in pool:
        if f['id'] in L and f['id'] not in excluded:
            v += f['c']
    return v, L

def _need(kept, L, cfg):
    bench = [p for p in kept if p['id'] not in L]
    nel = sum(1 for p in bench if p['minors'])
    return (len(bench) - nel) + max(0, nel - CAP['minors'])

def optimize_heuristic(owned, pool, cfg, lookahead=6):
    """owned: records (players + optional phantom pick placeholders). Drops are restricted to moves that reduce the binding
    bench constraint; among the `lookahead` cheapest such moves the one with the best re-optimised team value is taken."""
    owned = list(owned); excluded = set(); drops = []; first_legal = None
    limit = CAP['reserve'] + (CAP['ir'] if cfg['ir_any'] else 0) + cfg.get('slack', 0)
    for _ in range(400):
        _, L = _score(owned, pool, excluded, cfg)
        kept = owned + [f for f in pool if f['id'] in L and f['id'] not in excluded]
        ok = _need(kept, L, cfg) <= limit
        if first_legal is None:
            first_legal = ok
        if ok:
            break
        nel = sum(1 for p in kept if p['id'] not in L and p['minors'])
        overflow = nel > CAP['minors']
        cands = []
        for p in owned:
            if p['id'] not in L and ((not p['minors']) or overflow):
                cands.append((p.get('l', p['val']) + cfg['rho'] * p.get('c', 0.0), 'own', p))
        for f in pool:
            if f['id'] in L and f['id'] not in excluded:
                cands.append((f['c'], 'fa', f))
        if not cands:
            cands = [(p.get('l', p['val']) + cfg['rho'] * p.get('c', 0.0), 'own', p) for p in owned if p['id'] not in L]
        if not cands:
            break
        cands.sort(key=lambda x: x[0]); best = None
        for _, kind, p in cands[:lookahead]:
            if kind == 'own':
                sc, _ = _score([o for o in owned if o['id'] != p['id']], pool, excluded, cfg)
            else:
                sc, _ = _score(owned, pool, excluded | {p['id']}, cfg)
            if best is None or sc > best[0]:
                best = (sc, kind, p)
        _, kind, p = best
        if kind == 'own':
            owned = [o for o in owned if o['id'] != p['id']]; drops.append(p['id'])
        else:
            excluded.add(p['id'])
    value, L = _score(owned, pool, excluded, cfg)
    adds = [f['id'] for f in pool if f['id'] in L and f['id'] not in excluded]
    return dict(value=value, drops=drops, adds=adds, legal_before_moves=first_legal, lineup=L)

def optimize_exact(owned, pool, cfg):
    """Exact joint optimisation (MILP): lineup assignment + keep/drop + free-agent adds + bench legality, maximising team value."""
    P = owned + pool; nO = len(owned)
    xs = []                                    # (player index, slot column)
    for i, p in enumerate(P):
        if p.get('c', 0.0) > 1e-9:
            for sname in p['elig']:
                for j in SLOT_INDEX.get(sname, []):
                    xs.append((i, j))
    nx = len(xs); ny = nO; nz = 1; N = nx + ny + nz
    cvec = np.zeros(N)
    for k, (i, j) in enumerate(xs):
        p = P[i]; cvec[k] = (1 - cfg['rho']) * p['c'] if i < nO else p['c']
    for i in range(nO):
        p = owned[i]; cvec[nx + i] = p.get('l', p['val']) + cfg['rho'] * p.get('c', 0.0) + 1e-6  # tie-break: keep zero-value players when feasible
    rows = []; lo = []; hi = []
    A = lil_matrix((len(SLOTS) + len(P) + 2, N)); r = 0
    for j in range(len(SLOTS)):
        for k, (i, jj) in enumerate(xs):
            if jj == j: A[r, k] = 1
        lo.append(-np.inf); hi.append(1); r += 1
    for i in range(len(P)):
        for k, (ii, jj) in enumerate(xs):
            if ii == i: A[r, k] = 1
        if i < nO: A[r, nx + i] = -1; lo.append(-np.inf); hi.append(0)
        else: lo.append(-np.inf); hi.append(1)
        r += 1
    limit = CAP['reserve'] + (CAP['ir'] if cfg['ir_any'] else 0) + cfg.get('slack', 0)
    # overflow: sum_{elig owned}(y - lineup) - minors_cap - z <= 0
    for i in range(nO):
        if owned[i]['minors']: A[r, nx + i] = 1
    for k, (i, jj) in enumerate(xs):
        if i < nO and owned[i]['minors']: A[r, k] = -1
    A[r, nx + ny] = -1; lo.append(-np.inf); hi.append(CAP['minors']); r += 1
    # need: sum_{non-elig owned}(y - lineup) + z <= limit
    for i in range(nO):
        if not owned[i]['minors']: A[r, nx + i] = 1
    for k, (i, jj) in enumerate(xs):
        if i < nO and not owned[i]['minors']: A[r, k] = -1
    A[r, nx + ny] = 1; lo.append(-np.inf); hi.append(limit); r += 1
    integrality = np.r_[np.ones(nx + ny), 0]
    bounds = Bounds(np.zeros(N), np.r_[np.ones(nx + ny), 200])
    res = milp(-cvec, constraints=LinearConstraint(A.tocsr()[:r], lo, hi), integrality=integrality, bounds=bounds, options=dict(mip_rel_gap=1e-9))
    if not res.success:
        return None
    x = np.round(res.x)
    Lset = {P[i]['id'] for k, (i, j) in enumerate(xs) if x[k] > 0.5}
    drops = [owned[i]['id'] for i in range(nO) if x[nx + i] < 0.5]
    adds = [pool[i - nO]['id'] for k, (i, j) in enumerate(xs) if i >= nO and x[k] > 0.5]
    return dict(value=float(-res.fun) - 1e-6 * (nO - len(drops)), drops=drops, adds=adds, lineup=Lset)

def optimize(owned, pool, cfg):
    """Exact optimum. `legal_before_moves` = whether keeping every owned player is feasible (no drops needed)."""
    ex = optimize_exact(owned, pool, cfg)
    if ex is None:
        return optimize_heuristic(owned, pool, cfg)
    ex['legal_before_moves'] = (len(ex['drops']) == 0) if True else None
    return ex

class League:
    def __init__(self, d, cfg=None):
        self.cfg = dict(DEFAULT); self.cfg.update(cfg or {})
        vm, self.meta = value_maps(d)
        self.recs = build_records(d, vm[self.cfg['treatment']])
        self.pool = fa_pool(self.recs, self.cfg)
        self.base_owner = {i: r['owner'] for i, r in self.recs.items()}
        self._cache = {}
        self.slack = {}

    def calibrate_slack(self, owner_map, teams):
        """Real pre-trade rosters are legal by construction. Where the eligibility proxy makes one illegal, grant the minimum
        'unknown eligibility' slack that legalises it (flagged in outputs). Slack is a data-gap absorber, not a rule."""
        for t in teams:
            pl, pk = self.team_assets(owner_map, t)
            for k in range(0, 30):
                if self.value(pl, pk, k)['legal_before_moves']:
                    self.slack[t] = k
                    break

    def team_assets(self, owner_map, team):
        pl = [r for i, r in self.recs.items() if not r['pick'] and owner_map.get(i) == team and r['group'] in ('MLB', 'Minors')]
        pk = [r for i, r in self.recs.items() if r['pick'] and r['group'] == 'Picks' and owner_map.get(i) == team]
        return pl, pk

    def _phantoms(self, picks):
        if self.cfg['pick_slots'] != '2027':
            return []
        return [dict(id='ph:' + p['id'], val=p['val'], l=p['val'], c=0.0, elig=set(), minors=True, pick=False, name='phantom ' + p['name'])
                for p in picks if p['year'] == 2027]

    def value(self, players, picks, slack=0):
        key = (tuple(sorted(p['id'] for p in players)), tuple(sorted(p['id'] for p in picks)), slack)
        if key in self._cache:
            return self._cache[key]
        ph = self._phantoms(picks)
        res = optimize(players + ph, self.pool, dict(self.cfg, slack=slack))
        direct = sum(p['val'] for p in picks if not (self.cfg['pick_slots'] == '2027' and p['year'] == 2027))
        res = dict(res, total=res['value'] + direct)
        self._cache[key] = res
        return res

    def delta(self, owner_map, team, give, get):
        """Candidate value change for `team` receiving `get` ids and sending `give` ids (players and picks)."""
        pl, pk = self.team_assets(owner_map, team)
        give = set(give); get_r = [self.recs[i] for i in get]
        pl2 = [p for p in pl if p['id'] not in give] + [r for r in get_r if not r['pick']]
        pk2 = [p for p in pk if p['id'] not in give] + [r for r in get_r if r['pick'] and r['group'] == 'Picks']
        sl = self.slack.get(team, 0)
        before = self.value(pl, pk, sl); after = self.value(pl2, pk2, sl)
        base = sum(self.recs[i]['val'] for i in get) - sum(self.recs[i]['val'] for i in give)
        n_before = set(before['drops']); n_after = set(after['drops'])
        return dict(candidate=after['total'] - before['total'], baseline=base,
                    new_drops=[x for x in after['drops'] if x not in n_before], new_adds=[x for x in after['adds'] if x not in set(before['adds'])],
                    forced_drops_after=len(after['drops']), pre_trade_roster_legal=bool(before['legal_before_moves']),
                    post_trade_legal_without_moves=bool(after['legal_before_moves']))
