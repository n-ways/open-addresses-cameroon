#!/usr/bin/env python3
"""Export every named area (locality) with its building count and zone, from
the staged DB (tables loc, ba from areas.py; admin level 8). Light query.

  tools/export-areas.py STAGED.duckdb OUT.json
"""
import json, subprocess, sys
db, out = sys.argv[1:3]
sql = """LOAD spatial; SET memory_limit='3GB'; SET threads=4;
WITH c AS (SELECT lid, count(*) n FROM ba GROUP BY lid),
z AS (SELECT l.lid, any_value(a.osm) osm FROM loc l JOIN admin a ON a.level=8 AND ST_Intersects(a.g, l.g) GROUP BY l.lid)
SELECT l.lid, l."name", l.kind, l.src, round(ST_X(l.g),6) lon, round(ST_Y(l.g),6) lat, c.n, z.osm
FROM c JOIN loc l USING (lid) LEFT JOIN z USING (lid) ORDER BY l.lid;"""
r = subprocess.run(['duckdb', db, '-json'], input=sql, capture_output=True, text=True)
if 'Error' in r.stderr:
    sys.exit(r.stderr[-2000:])
s = r.stdout.strip()
rows = json.loads(s[s.rindex('\n[') + 1:] if '\n[' in s else s[s.index('['):])
json.dump(rows, open(out, 'w'), ensure_ascii=False)
print(len(rows), 'areas')
