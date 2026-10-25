"""Shared helpers for the BangaLangin roster-aware audit. No production code is imported or modified."""
import gzip, json, hashlib
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FROZEN = ROOT / 'frozen_inputs'
RES = ROOT / 'results'
SNAPSHOT = FROZEN / 'assets_snapshot.json.gz'

# League rules (06-League-Rules-Summary.txt): active 22, reserve 11, minors 30, IR 8; non-IR cap 63.
# IR may hold ANY player ("Only players on the MLB IL may be moved to IR: No").
CAP = dict(active=22, reserve=11, minors=30, ir=8)
HIT = {'C', '1B', '2B', '3B', 'SS', 'OF', 'UT'}
PIT = {'SP', 'RP', 'P'}
SLOTS = ['C', '1B', '2B', '3B', 'SS', 'CI', 'MI', 'UT'] + ['OF'] * 5 + ['P'] * 9  # 22 slots = max active
SLOT_OK = {'C': {'C'}, '1B': {'1B'}, '2B': {'2B'}, '3B': {'3B'}, 'SS': {'SS'}, 'CI': {'1B', '3B'},
           'MI': {'2B', 'SS'}, 'OF': {'OF'}}

def load():
    with gzip.open(SNAPSHOT, 'rt', encoding='utf-8') as f:
        return json.load(f)

def nd(a):
    return a['values']['neutral']['display']

def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def pos_tokens(a):
    return set(a.get('position', '').split(',')) if a.get('position') else set()

def is_pitcher(a):
    return bool(pos_tokens(a) & PIT)

def slot_eligibility(a):
    """Slot types this asset can fill. Hitters: listed positions + CI/MI + UT. Pitchers: P."""
    t = pos_tokens(a)
    out = set()
    if t & PIT:
        out.add('P')
    if t & HIT:
        out.add('UT')
        for s, ok in SLOT_OK.items():
            if t & ok:
                out.add(s)
    return out

def near_term_share(a):
    """Share of discounted 8-year expected utility earned in the first 3 seasons (0.88 annual discount, as in the UI)."""
    u = a.get('annual_expected_utility') or []
    w = [0.88 ** i for i in range(len(u))]
    tot = sum(x * y for x, y in zip(w, u))
    near = sum(x * y for x, y in zip(w[:3], u[:3]))
    return float(near / tot) if tot > 1e-12 else 0.0

def is_ranking_led(a):
    return bool(a.get('ranking_policy'))

def is_pick(a):
    return a['audit']['kind'] == 'pick'

def pairs_ranking_led_mlb(d):
    """(contribution_value, display, asset) for ranking-led non-prospect assets: the only overlap evidence on both scales."""
    return [(a['ranking_policy']['contribution_value'], nd(a), a) for a in d['assets']
            if not is_pick(a) and is_ranking_led(a) and a['audit']['kind'] != 'prospect']

def value_maps(d):
    """Value treatments. 'shipped' is the baseline; the others are sensitivity treatments, not recommendations."""
    A = d['assets']
    pairs = pairs_ranking_led_mlb(d)
    contrib = np.array([p[0] for p in pairs]); disp = np.array([p[1] for p in pairs])
    ok = contrib >= np.percentile(contrib, 25)  # support-limited: rank list truncates low production
    k = float(np.median(disp[ok] / np.maximum(contrib[ok], 1e-9)))
    floor = float(min(nd(a) for a in A if not is_pick(a) and is_ranking_led(a)))
    maps = {t: {} for t in ('shipped', 'production', 'bridge', 'capped')}
    for a in A:
        v = nd(a); i = a['id']
        maps['shipped'][i] = v
        if is_pick(a):
            for t in ('production', 'bridge', 'capped'):
                maps[t][i] = v
            continue
        if is_ranking_led(a):
            # prospects' contribution_value is an archived diagnostic (timing withdrawn): keep shipped value there
            maps['production'][i] = v if a['audit']['kind'] == 'prospect' else a['ranking_policy']['contribution_value']
            maps['bridge'][i] = v
            maps['capped'][i] = v
        else:
            maps['production'][i] = v
            maps['bridge'][i] = v * k
            maps['capped'][i] = min(v, floor)
    return maps, dict(bridge_factor=k, rank_floor=floor)


_EXPO = None
def career_exposure(a):
    """Observed MLB exposure (PA for hitters, IP for pitchers) summed over the years in role-display-scenarios.json (2023-2026).
    Returns None when the player has no observation record. Pre-2023 career totals are NOT available (understates veterans)."""
    global _EXPO
    if _EXPO is None:
        _EXPO = json.loads((FROZEN / 'role-display-scenarios.json').read_text(encoding='utf-8'))['players']
    v = _EXPO.get(a['id'])
    if not v or 'observations' not in v:
        return None
    return sum((o['exposure'] or 0) for o in v['observations'] if str(o.get('status', '')).startswith('observed'))

def minors_eligible(a, ab_per_pa=0.89):
    """Rule: career+current AB <= 503 (hitters) / IP <= 162 (pitchers). Proxy: Minors group, or estimated exposure under the limit."""
    if a['group'] == 'Minors':
        return True
    c = career_exposure(a)
    if c is None:
        return False
    return (c * ab_per_pa <= 503) if not is_pitcher(a) else (c <= 162)
