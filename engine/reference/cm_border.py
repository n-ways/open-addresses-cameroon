"""Cameroon's national border, for the rule that a code is only ever issued inside it.

A code is issued only for a compound whose entrance lies inside the national border
(OpenStreetMap, admin_level 2) or within ``BORDER_M`` (300 m) of it. Zone outlines from
other sources may spill over the border; they never decide (engine/SPEC.md 6.1).

``engine/data/border.geojson`` is the border simplified to about 50 m (tools/build-border.py).
Its property ``errorM`` is the largest distance between the simplified line and the
OpenStreetMap line, measured when it was built. A point more than ``BORDER_M`` outside the
true border is then more than ``BORDER_M - errorM`` outside the simplified one, so
``abroad`` refuses every such point; a point inside the border, or less than
``BORDER_M - 2 x errorM`` outside it, is always accepted.

Distances are in local metres: 110,574 m per degree of latitude, 111,320 x cos(lat) per
degree of longitude, the cosine of the point's own latitude. Standard library only.

  b = Border()                 # engine/data/border.geojson
  b.inside(lat, lng)           # inside the simplified border
  b.outside_m(lat, lng)        # metres outside it, 0 inside
  b.abroad(lat, lng)           # True: no Cameroon code may be issued here
"""
import json
import math
import os

BORDER_M = 300.0
BORDER_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'border.geojson')
M_LAT = 110574.0
M_LON_EQ = 111320.0
BAND = 0.02  # degrees of latitude per band of the edge index


def seg_m(lat, lng, a, b):
    """Metres from (lat, lng) to the segment a-b ([lng, lat] points), on the point's local plane."""
    k = M_LON_EQ * math.cos(math.radians(lat))
    ax, ay = (a[0] - lng) * k, (a[1] - lat) * M_LAT
    bx, by = (b[0] - lng) * k, (b[1] - lat) * M_LAT
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / L))
    return math.hypot(ax + t * dx, ay + t * dy)


class Border:
    def __init__(self, path=BORDER_JSON):
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        if d.get('type') == 'FeatureCollection':
            d = d['features'][0]
        self.props = d.get('properties') or {}
        self.error_m = float(self.props['errorM'])
        self.limit_m = BORDER_M - self.error_m
        g = d['geometry']
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        self.edges = []
        for poly in polys:
            for ring in poly:
                pts = [(float(p[0]), float(p[1])) for p in ring]
                if pts[0] != pts[-1]:
                    pts.append(pts[0])
                self.edges += list(zip(pts, pts[1:]))
        self.bands = {}
        for e in self.edges:
            lo, hi = sorted((e[0][1], e[1][1]))
            for i in range(math.floor(lo / BAND), math.floor(hi / BAND) + 1):
                self.bands.setdefault(i, []).append(e)
        self.box = (min(min(a[0], b[0]) for a, b in self.edges), min(min(a[1], b[1]) for a, b in self.edges),
                    max(max(a[0], b[0]) for a, b in self.edges), max(max(a[1], b[1]) for a, b in self.edges))

    def inside(self, lat, lng):
        """Even-odd rule over every ring (holes included)."""
        inside = False
        for (x0, y0), (x1, y1) in self.bands.get(math.floor(lat / BAND), ()):
            if (y0 > lat) != (y1 > lat) and lng < (x1 - x0) * (lat - y0) / (y1 - y0) + x0:
                inside = not inside
        return inside

    def outside_m(self, lat, lng):
        """Metres from the point to the simplified border when the point is outside it, else 0."""
        if self.inside(lat, lng):
            return 0.0
        # the edges of the nearby bands first (about 2 km either side), then, if none is that
        # close, every edge
        reach = 2200.0
        n = math.ceil(reach / M_LAT / BAND)
        i = math.floor(lat / BAND)
        best = math.inf
        for j in range(i - n, i + n + 1):
            for a, b in self.bands.get(j, ()):
                best = min(best, seg_m(lat, lng, a, b))
        if best <= reach:
            return best
        return min(seg_m(lat, lng, a, b) for a, b in self.edges)

    def abroad(self, lat, lng):
        """True when the point may lie more than BORDER_M outside the national border."""
        return self.outside_m(lat, lng) > self.limit_m
