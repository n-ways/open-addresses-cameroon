#!/usr/bin/env python3
"""Count the codes of a registry whose entrance lies more than 300 m outside Cameroon's border.

  python3 tools/check-border.py [registry folder]      (default: registry/)

Reads every <zone>.csv.gz of the folder (columns machine, entrance_lat, entrance_lng) and
tests each entrance with engine/reference/cm_border.py against engine/data/border.geojson,
the rule the issuing server applies. Prints the number of codes, how many lie outside the
simplified border at all, and lists every code that may lie more than 300 m outside it
(more than 300 m - errorM outside the simplified line). Exits 1 if there is any.
Standard library only.
"""
import csv
import gzip
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, 'engine', 'reference'))
import cm_border as B  # noqa: E402


def main(folder):
    b = B.Border()
    total = outside = 0
    abroad = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith('.csv.gz') or name.startswith('areas'):
            continue
        with gzip.open(os.path.join(folder, name), 'rt', encoding='utf-8', newline='') as f:
            for r in csv.DictReader(f):
                if not r.get('entrance_lat'):
                    continue
                lat, lng = float(r['entrance_lat']), float(r['entrance_lng'])
                total += 1
                if b.inside(lat, lng):
                    continue
                outside += 1
                d = b.outside_m(lat, lng)
                if d > b.limit_m:
                    abroad.append((r['machine'], lat, lng, d))
    for m, lat, lng, d in abroad:
        print(f'{m}\t{lat:.7f},{lng:.7f}\t{d:.0f} m outside')
    print(f'{total:,} codes; {outside:,} outside the simplified border; '
          f'{len(abroad):,} more than {B.BORDER_M:.0f} m outside the national border')
    return 1 if abroad else 0


if __name__ == '__main__':
    sys.exit(main(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, 'registry'))))
