#!/usr/bin/env python3
"""Cameroon's national border for the issuing server: engine/data/border.geojson.

Reads <work>/country.geojson (tools/prepare-inputs.py: OpenStreetMap's admin_level 2
boundary of Cameroon) and simplifies every ring with Douglas-Peucker at 50 m, in local metres
(110,574 m per degree of latitude, 111,320 x cos(lat) per degree of longitude). Then measures
the largest distance from any OpenStreetMap vertex to the chord that replaces it, which bounds how far
the two lines are apart: every point of the original line between two kept vertices lies within
the tolerance of the chord between them, and every chord point within it of the original line.
That distance, rounded up to the metre, is written as ``errorM``; engine/reference/cm_border.py
refuses a point more than 300 m - errorM outside the simplified border, so that no point more
than 300 m outside the true border is ever accepted.

  python3 tools/build-border.py <work folder>

Standard library only.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, 'engine', 'reference'))
import cm_border as B  # noqa: E402

TOLERANCE_M = 50.0
OUT = os.path.join(REPO, 'engine', 'data', 'border.geojson')


def simplify(pts, tol):
    """Douglas-Peucker on a closed ring (first point repeated last), iterative: the indices kept."""
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    # split a closed ring at its farthest point from the start, so both halves have a chord
    far = max(range(len(pts)), key=lambda i: B.seg_m(pts[i][1], pts[i][0], pts[0], pts[0]))
    keep[far] = True
    stack = [(0, far), (far, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        best, bi = -1.0, -1
        for k in range(i + 1, j):
            d = B.seg_m(pts[k][1], pts[k][0], pts[i], pts[j])
            if d > best:
                best, bi = d, k
        if best > tol:
            keep[bi] = True
            stack += [(i, bi), (bi, j)]
    return [i for i, k in enumerate(keep) if k]


def main(work):
    src = json.load(open(os.path.join(work, 'country.geojson'), encoding='utf-8'))
    g = src['features'][0]['geometry'] if src.get('type') == 'FeatureCollection' else src.get('geometry', src)
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    out, err, n_in, n_out = [], 0.0, 0, 0
    for poly in polys:
        rings = []
        for ring in poly:
            pts = [(round(p[0], 7), round(p[1], 7)) for p in ring]
            if pts[0] != pts[-1]:
                pts.append(pts[0])
            ks = simplify(pts, TOLERANCE_M)
            if len(ks) < 4:
                continue  # an islet or hole smaller than the tolerance
            # every original vertex against the chord that replaces it: an upper bound of its
            # distance to the simplified ring
            for i, j in zip(ks, ks[1:]):
                for k in range(i + 1, j):
                    err = max(err, B.seg_m(pts[k][1], pts[k][0], pts[i], pts[j]))
            s = [pts[i] for i in ks]
            rings.append([[round(x, 6), round(y, 6)] for x, y in s])
            n_in += len(pts)
            n_out += len(s)
        if rings:
            out.append(rings)
    err_m = math.ceil(err + 1)  # one metre for the six-decimal rounding of the kept points
    feat = {'type': 'Feature',
            'properties': {'country': 'CM', 'source': 'OpenStreetMap, admin_level 2 (ODbL 1.0)',
                           'toleranceM': TOLERANCE_M, 'errorM': err_m, 'borderM': B.BORDER_M,
                           'rule': 'a code is issued only for an entrance inside the national border or within 300 m '
                                   'of it; refuse a point more than borderM - errorM outside this outline'},
            'geometry': {'type': 'MultiPolygon', 'coordinates': out}}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(feat, f, separators=(',', ':'))
        f.write('\n')
    print(f'{n_in} vertices -> {n_out}, largest deviation {err:.1f} m (errorM {err_m}), {os.path.getsize(OUT):,} bytes')


if __name__ == '__main__':
    main(os.path.abspath(sys.argv[1]))
