#!/usr/bin/env python3
"""Data for the paper's figures (docs/figures/*.dat) and its measured properties
(model/stats/evaluation.json), from the published registry and the model statistics.

  python3 tools/paper-figures.py            # figures and evaluation
  python3 tools/paper-figures.py figures    # figures only (seconds)

Standard library only. The evaluation streams every registry file once (a few minutes,
under 1 GB of memory): uniqueness, digits, check digits, plate lengths, decoding of the
written forms, spot-code error, locality of the Hilbert numbering and the collisions that
per-area numbering would have caused.
"""
import collections, csv, gzip, json, math, os, random, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, 'engine', 'reference'))
import cm_engine as E  # noqa: E402

FIG = os.path.join(REPO, 'docs', 'figures')
REG = os.path.join(REPO, 'registry')
KX_EQ, KY = 111320.0, 110574.0


def areas():
    return list(csv.DictReader(gzip.open(os.path.join(REG, 'areas.csv.gz'), 'rt', encoding='utf-8')))


def blocks(r):
    return [tuple(int(x) for x in b.split('-')) for b in r['blocks'].split()]  # empty for an area with no compound yet


def write(name, header, rows):
    with open(os.path.join(FIG, name), 'w', encoding='utf-8') as f:
        f.write(' '.join(header) + '\n')
        for r in rows:
            f.write(' '.join(str(x) for x in r) + '\n')


def zone_rows(zkey):
    return csv.DictReader(gzip.open(os.path.join(REG, f'{zkey}.csv.gz'), 'rt', encoding='utf-8'))


# ---------------------------------------------------------------- figures

def simplify(pts, tol):
    """Douglas-Peucker on a closed ring of (lon, lat), tolerance in degrees."""
    if len(pts) < 5:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1e-12
        best, bi = -1.0, None
        for i in range(a + 1, b):
            x, y = pts[i]
            d = abs(dy * (x - x1) - dx * (y - y1)) / L if (dx or dy) else math.hypot(x - x1, y - y1)
            if d > best:
                best, bi = d, i
        if bi is not None and best > tol:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    out = [p for p, k in zip(pts, keep) if k]
    return out if len(out) >= 4 else pts


def ring_km2(ring):
    lat0 = sum(p[1] for p in ring) / len(ring)
    kx = KX_EQ * math.cos(math.radians(lat0)) / 1000
    ky = KY / 1000
    s = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        s += (x1 * kx) * (y2 * ky) - (x2 * kx) * (y1 * ky)
    return abs(s) / 2


def fig_zones(manifest):
    """Arrondissements shaded by compounds per km^2, in five classes."""
    g = json.load(open(os.path.join(REPO, 'model', 'units', 'zones.geojson'), encoding='utf-8'))
    edges = [10, 50, 200, 1000]
    out = [[] for _ in range(5)]
    dens = []
    for f in g['features']:
        k = f['properties']['key']
        polys = [f['geometry']['coordinates']] if f['geometry']['type'] == 'Polygon' else f['geometry']['coordinates']
        km2 = sum(ring_km2(p[0]) - sum(ring_km2(h) for h in p[1:]) for p in polys)
        d = manifest['byUnit'].get(k, 0) / km2
        dens.append((k, d, km2))
        c = sum(d >= e for e in edges)
        for p in polys:
            ring = simplify([tuple(x) for x in p[0]], 0.012)
            out[c] += [(round(x, 3), round(y, 3)) for x, y in ring] + [('nan', 'nan')]
    for i, rows in enumerate(out):
        write(f'zones-map-{i}.dat', ['x', 'y'], rows)
    hist = collections.Counter(sum(d >= e for e in edges) for _k, d, _a in dens)
    return {'classes': [hist[i] for i in range(5)], 'edges': edges,
            'densest': sorted(dens, key=lambda t: -t[1])[:5], 'sparsest': sorted(dens, key=lambda t: t[1])[:3]}


def fig_sources():
    b = json.load(open(os.path.join(REPO, 'model', 'stats', 'building-stats.json'), encoding='utf-8'))
    en = {'Adamaoua': 'Adamawa', 'Centre': 'Centre', 'Est': 'East', 'Extrême-Nord': 'Far North',
          'Littoral': 'Littoral', 'Nord': 'North', 'Nord-Ouest': 'North-West', 'Ouest': 'West', 'Sud': 'South',
          'Sud-Ouest': 'South-West'}
    rows = []
    for fr, v in sorted(b['regions'].items(), key=lambda kv: kv[1]['structures']):
        osm = v['fromOpenStreetMap']
        rows.append((en[fr].replace(' ', '~'), fr.replace(' ', '~'), osm, v['structures'] - osm, v['compounds']))
    write('sources.dat', ['en', 'fr', 'osm', 'other', 'compounds'], rows)
    return rows


def fig_area_sizes(ar):
    """Histogram of compounds per area on half-decade bins, split by the digits of the name's range."""
    edges = [1, 3, 10, 32, 100, 316, 1000, 3162, 10000, 31623]
    cnt = collections.Counter()
    for r in ar:
        n = int(r['compounds'])
        if n == 0:
            continue
        i = max(j for j, e in enumerate(edges) if n >= e)
        cnt[(i, r['digits'])] += 1
    rows = [(i, edges[i], cnt[(i, '3')], cnt[(i, '4')], cnt[(i, '5')]) for i in range(len(edges))]
    write('area-sizes.dat', ['bin', 'lo', 'd3', 'd4', 'd5'], rows)
    return rows


def fig_name_totals(ar):
    """Empirical distribution of T, the total block size of each name (Eq. 6)."""
    tot = collections.Counter()
    for r in ar:
        tot[r['name_id']] += sum(hi - lo + 1 for lo, hi in blocks(r))
    ts = sorted(t for t in tot.values() if t)  # names whose areas all wait for their first compound have no block
    n = len(ts)
    pts, last = [], None
    for i, t in enumerate(ts):
        if t != last and (i == n - 1 or ts[i + 1] != t):
            pts.append((t, round((i + 1) / n, 5)))
            last = t
    # thin to about 300 points on a log scale
    keep, lastx = [], 0
    for t, p in pts:
        if math.log10(t) - lastx > 0.012 or (t, p) == pts[-1]:
            keep.append((t, p))
            lastx = math.log10(t)
    write('name-totals.dat', ['t', 'p'], keep)
    return {'names': n, 'le810': sum(t <= 810 for t in ts), 'le8100': sum(810 < t <= 8100 for t in ts),
            'gt8100': sum(t > 8100 for t in ts), 'max': ts[-1]}


def fig_adjap(ar):
    nid = next(r['name_id'] for r in ar if r['plate_name'] == 'Adjap')
    fam = sorted((r for r in ar if r['name_id'] == nid), key=lambda r: blocks(r)[0][0])
    used = collections.defaultdict(list)
    for z in sorted({r['zone'].split('-')[0] for r in fam}):
        for row in zone_rows(z):
            if row['zone'] in {r['zone'] for r in fam}:
                used[row['zone']].append(int(row['number']))
    rows = []
    for r in fam:
        lo, hi = blocks(r)[0]
        main_hi = lo + (hi - lo + 1) * 2 // 3 - 1
        u = used[r['zone']]
        rows.append((r['zone'], r['plate_name'], r['zone_name'].replace(' ', '~'), lo, hi, main_hi, max(u) if u else lo - 1, len(u)))
    write('adjap-blocks.dat', ['area', 'plate', 'zonename', 'lo', 'hi', 'mainhi', 'usedhi', 'n'], rows)
    return rows


def fig_bonapriso(ar):
    a = next(r for r in ar if r['zone'] == 'DLA1-015')
    x0, y0, x1, y1 = (float(v) for v in a['frame'].split())
    kx = KX_EQ * math.cos(math.radians((y0 + y1) / 2))
    pts = sorted(((int(r['number']), float(r['entrance_lng']), float(r['entrance_lat']), r['machine'])
                  for r in zone_rows('DLA1') if r['zone'] == 'DLA1-015'))
    write('bonapriso-points.dat', ['n', 'x', 'y'],
          [(n, round((lon - x0) * kx, 1), round((lat - y0) * KY, 1)) for n, lon, lat, _m in pts])
    write('bonapriso-frame.dat', ['w', 'h'], [(round((x1 - x0) * kx, 1), round((y1 - y0) * KY, 1))])
    # the order-3 curve, cell centres in visiting order
    cells = sorted((E.hilbert_index(3, x, y), x, y) for x in range(8) for y in range(8))
    write('hilbert-order3.dat', ['d', 'x', 'y'], [(d, x + 0.5, y + 0.5) for d, x, y in cells])
    # the worked example of Eq. (8)-(9)
    me = next(p for p in pts if p[0] == 1401)
    n = (1 << E.ORDER) - 1
    gx, gy = int((me[1] - x0) / (x1 - x0) * n), int((me[2] - y0) / (y1 - y0) * n)
    hs = sorted((E.curve_pos(lon, lat, (x0, y0, x1, y1)), m) for _n, lon, lat, m in pts)
    rank = [m for _h, m in hs].index(me[3])
    return {'compounds': len(pts), 'numbers': [pts[0][0], pts[-1][0]], 'gx': gx, 'gy': gy,
            'h': E.hilbert_index(E.ORDER, gx, gy), 'rank0': rank,
            'xy': (round((me[1] - x0) * kx, 1), round((me[2] - y0) * KY, 1)),
            'frame_m': (round((x1 - x0) * kx), round((y1 - y0) * KY))}


def fig_spot():
    f = E.frames()['DLA1']
    kx = KX_EQ * math.cos(math.radians(f['latc']))
    rows = [r for r in zone_rows('DLA1')]
    me = next(r for r in rows if r['machine'] == 'CM-DLA1-015-1401-6')
    ex = (float(me['entrance_lng']) - f['lon0']) * kx
    ny = (float(me['entrance_lat']) - f['lat0']) * KY
    near = []
    for r in rows:
        x = (float(r['entrance_lng']) - f['lon0']) * kx
        y = (float(r['entrance_lat']) - f['lat0']) * KY
        if abs(x - ex) <= 55 and abs(y - ny) <= 55:
            near.append((round(x, 1), round(y, 1), r['written'].replace(' ', '~'), 1 if r is me else 0))
    write('spot-points.dat', ['x', 'y', 'label', 'me'], near)
    lat, lon = E.spot_decode('CM-DLA1 E0449 N0268')
    cx, cy = (lon - f['lon0']) * kx, (lat - f['lat0']) * KY
    write('spot-cell.dat', ['ex', 'ny', 'cx', 'cy', 'px', 'py'],
          [(449, 268, round(cx, 1), round(cy, 1), round(ex, 1), round(ny, 1))])
    return {'near': len(near), 'centre': (round(cx, 1), round(cy, 1)), 'point': (round(ex, 1), round(ny, 1)),
            'dist_m': round(math.hypot(cx - ex, cy - ny), 2)}


# ---------------------------------------------------------------- evaluation

def unaccent(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def evaluate(ar, manifest):
    rnd = random.Random(20261021)
    by_area = {r['zone']: r for r in ar}
    nid_of = {r['zone']: r['name_id'] for r in ar}
    zidx = {z['key']: int(z['index']) for z in E.zones()}
    seen_home = set()
    dup_home = 0
    n = 0
    digits = collections.Counter()
    bad_check = out_of_block = 0
    official = 0
    alert_codes = 0
    sample = []  # reservoir of (machine, written, lat, lon, zone, home)
    K = 20000
    step_d, rand_d = [], []
    for zkey in sorted(manifest['byUnit']):
        prev = None
        pts_by_area = collections.defaultdict(list)
        for r in zone_rows(zkey):
            n += 1
            num = r['number']
            digits[len(num)] += 1
            akey = r['zone']
            a = by_area[akey]
            k = (E.name_key(a['plate_name']), num)
            h = hash(k)
            if h in seen_home:
                dup_home += 1
            seen_home.add(h)
            idx = akey.split('-')[1]
            c = E.damm(f'{int(nid_of[akey]):05d}{zidx[zkey]:03d}{idx}{num}')
            if str(c) != r['check'] or not r['machine'].endswith(f'-{c}'):
                bad_check += 1
            if not any(lo <= int(num) <= hi for lo, hi in blocks(a)):
                out_of_block += 1
            if r['official_address']:
                official += 1
            if a['alert_zone'] == 'true':
                alert_codes += 1
            lat, lon = float(r['entrance_lat']), float(r['entrance_lng'])
            pts_by_area[akey].append((int(num), lat, lon))
            if len(sample) < K:
                sample.append((r['machine'], r['written'], lat, lon, zkey, r['home']))
            else:
                j = rnd.randrange(n)
                if j < K:
                    sample[j] = (r['machine'], r['written'], lat, lon, zkey, r['home'])
        # locality: consecutive numbers against random pairs of the same area
        for akey, ps in pts_by_area.items():
            if len(ps) < 3:
                continue
            ps.sort()
            kx = KX_EQ * math.cos(math.radians(ps[0][1]))
            for _ in range(min(5, len(ps) - 1)):
                i = rnd.randrange(len(ps) - 1)
                a, b = ps[i], ps[i + 1]
                step_d.append(math.hypot((a[2] - b[2]) * kx, (a[1] - b[1]) * KY))
                a, b = rnd.sample(ps, 2)
                rand_d.append(math.hypot((a[2] - b[2]) * kx, (a[1] - b[1]) * KY))
        print(zkey, n, file=sys.stderr)
    # decoding of the written form, as typed in four ways
    dec = collections.Counter()
    spot_max = 0.0
    for m, w, lat, lon, zkey, home in sample:
        for form, text in (('written', w), ('lower', w.lower()), ('unaccented', unaccent(w).upper()),
                           ('joined', home)):
            try:
                ok = E.resolve_remembered(text)['code'] == m
            except ValueError:
                ok = False
            dec[(form, ok)] += 1
        sl, so = E.spot_decode(E.spot_encode(lat, lon, zkey))
        kx = KX_EQ * math.cos(math.radians(lat))
        spot_max = max(spot_max, math.hypot((so - lon) * kx, (sl - lat) * KY))
    # Damm: every single substitution and adjacent transposition of 1,000 machine codes
    subs = subs_caught = trans = trans_caught = 0
    for m, *_ in sample[:1000]:
        _cc, z, ix, num, c = m.split('-')
        s = f'{int(nid_of[z + "-" + ix]):05d}{zidx[z]:03d}{ix}{num}' + c
        for i in range(len(s)):
            for d in '0123456789':
                if d != s[i]:
                    t = s[:i] + d + s[i + 1:]
                    subs += 1
                    subs_caught += E.damm(t[:-1]) != int(t[-1])
            if i + 1 < len(s) and s[i] != s[i + 1]:
                t = s[:i] + s[i + 1] + s[i] + s[i + 2:]
                trans += 1
                trans_caught += E.damm(t[:-1]) != int(t[-1])
    # plates
    live = [r for r in ar if int(r['compounds']) > 0]
    chars = collections.Counter(len(unicodedata.normalize('NFC', r['plate_name'])) for r in live)
    words = collections.Counter(len(r['plate_name'].split()) for r in live)
    # the alternative: every area numbered on its own from 10^(d-1)
    fams = collections.defaultdict(list)
    for r in live:
        fams[r['name_id']].append(int(r['compounds']))
    amb = 0
    for cs in fams.values():
        if len(cs) < 2:
            continue
        seen = collections.Counter()
        for c in cs:
            B = E.block_size(c)
            d = next(d for d in (3, 4, 5, 6) if B <= int(0.9 * 9 * 10 ** (d - 1)))
            main = B * 2 // 3
            st = max(1, main // max(1, int(c * 1.5)))
            for i in range(c):
                seen[10 ** (d - 1) + i * st] += 1
        amb += sum(v for v in seen.values() if v > 1)
    med = lambda v: sorted(v)[len(v) // 2]
    return {
        'codes': n, 'manifest': manifest['codes'], 'uniqueWritten': len(seen_home), 'duplicateWritten': dup_home,
        'digits': dict(sorted(digits.items())), 'badCheck': bad_check, 'outOfBlock': out_of_block,
        'officialFirst': official, 'alertZoneCodes': alert_codes,
        'decodeSample': K, 'decode': {f'{f}:{ok}': v for (f, ok), v in sorted(dec.items())},
        'spotMaxErrorM': round(spot_max, 2),
        'damm': {'substitutions': subs, 'caught': subs_caught, 'transpositions': trans, 'transCaught': trans_caught},
        'plateChars': dict(sorted(chars.items())), 'plateWords': dict(sorted(words.items())),
        'perAreaNumberingAmbiguous': amb, 'perAreaShare': round(amb / n, 4),
        'locality': {'pairs': len(step_d), 'medianNextM': round(med(step_d), 1),
                     'medianRandomM': round(med(rand_d), 1)},
    }


def main():
    os.makedirs(FIG, exist_ok=True)
    manifest = json.load(open(os.path.join(REG, 'MANIFEST.json'), encoding='utf-8'))
    ar = areas()
    info = {'zones': fig_zones(manifest), 'sources': fig_sources(), 'areaSizes': fig_area_sizes(ar),
            'nameTotals': fig_name_totals(ar), 'adjap': fig_adjap(ar), 'bonapriso': fig_bonapriso(ar),
            'spot': fig_spot()}
    print(json.dumps(info, ensure_ascii=False, indent=1, default=str))
    if sys.argv[1:] != ['figures']:
        ev = evaluate(ar, manifest)
        ev['registryExported'] = manifest['exported']
        json.dump(ev, open(os.path.join(REPO, 'model', 'stats', 'evaluation.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print(json.dumps(ev, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
