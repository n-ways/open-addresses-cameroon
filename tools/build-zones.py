#!/usr/bin/env python3
"""Build Cameroon's code zones (model/zones.json, model/zones.geojson).

A zone is an arrondissement (OpenStreetMap admin_level 8): the territory of
one commune, the level at which Campost says it assigns commune postal codes
(Nov 2024). Keys have four characters:

  * arrondissements of the 14 communautés urbaines with numbered communes:
    city key + arabic numeral (YDE1-YDE7, DLA1-DLA6, BDA1-BDA3, LIM1-LIM3 ...),
    what people already say ("Yaoundé 6", "Douala 5e", "Bamenda Two");
  * every other arrondissement: its département's 3-letter key + one letter
    (the name's initial, else its next letter not yet used in that département).

The spot grid has fixed 3 m cells; the number of grid characters (6, 7 or 8)
is the smallest that covers the zone's frame. Index, key, frame and length
are frozen once a code is issued.

  tools/build-zones.py STAGED.duckdb ZONE_STATS.json
"""
import json, math, os, re, subprocess, sys, unicodedata

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CELL = 3.0

CITY = {'Yaoundé': 'YDE', 'Douala': 'DLA', 'Bafoussam': 'BAF', 'Bamenda': 'BDA', 'Garoua': 'GAR', 'Maroua': 'MAR',
        'Ngaoundéré': 'NGA', 'Bertoua': 'BER', 'Ebolowa': 'EBO', 'Édéa': 'EDE', 'Kribi': 'KRI', 'Kumba': 'KUM',
        'Limbé': 'LIM', 'Nkongsamba': 'NKS'}
CITY_EN = {'Yaoundé': 'Yaounde', 'Douala': 'Douala', 'Limbé': 'Limbe', 'Édéa': 'Edea', 'Ngaoundéré': 'Ngaoundere'}
ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}

# département (OSM name) -> 3-letter key
DEPT = {
    'Djérem': 'DJE', 'Faro-et-Déo': 'FAD', 'Mayo-Banyo': 'BAN', 'Mbéré': 'MBE', 'Vina': 'VIN',
    'Haute-Sanaga': 'HSA', 'Lekié': 'LEK', 'Mbam-et-Inoubou': 'MBI', 'Mbam-et-Kim': 'MBK', 'Méfou-et-Afamba': 'MAF',
    'Méfou-et-Akono': 'MAK', 'Mfoundi': 'MFO', 'Nyong-et-Kéllé': 'NYK', 'Nyong-et-Foumou': 'NYM', "Nyong-et-So'o": 'NYS',
    'Boumba-et-Ngoko': 'BNG', 'Haut-Nyong': 'HNY', 'Kadey': 'KAD', 'Lom-et-Djérem': 'LOM',
    'Diamaré': 'DIA', 'Logone-et-Chari': 'LOG', 'Mayo-Danay': 'MDA', 'Mayo-Kani': 'MKA', 'Mayo-Sava': 'MSA', 'Mayo-Tsanaga': 'MTS',
    'Moungo': 'MOU', 'Nkam': 'NKA', 'Sanaga-Maritime': 'SAM', 'Wouri': 'WOU',
    'Bénoué': 'BEN', 'Faro': 'FAR', 'Mayo-Louti': 'MLO', 'Mayo-Rey': 'MRE',
    'Boyo': 'BOY', 'Bui': 'BUI', 'Donga-Mantung': 'DOM', 'Menchum': 'MEN', 'Mezam': 'MEZ', 'Momo': 'MOM', 'Ngoketunjia': 'NGK',
    'Bamboutos': 'BAM', 'Haut-Nkam': 'HNK', 'Hauts-Plateaux': 'HPL', 'Nkoung-Khi': 'KKH', 'Menoua': 'MNO', 'Mifi': 'MIF',
    'Ndé': 'NDE', 'Noun': 'NOU',
    'Dja-et-Lobo': 'DJL', 'Mvila': 'MVI', 'Océan': 'OCE', 'Vallée-du-Ntem': 'VNT',
    'Fako': 'FAK', 'Kupe-Muanenguba': 'KMA', 'Lebialem': 'LEB', 'Manyu': 'MAN', 'Meme': 'MEM', 'Ndian': 'NDI',
}
REGION = {'CM-AD': ('Adamaoua', 'Adamawa'), 'CM-CE': ('Centre', 'Centre'), 'CM-ES': ('Est', 'East'),
          'CM-EN': ('Extrême-Nord', 'Far North'), 'CM-LT': ('Littoral', 'Littoral'), 'CM-NO': ('Nord', 'North'),
          'CM-NW': ('Nord-Ouest', 'North-West'), 'CM-OU': ('Ouest', 'West'), 'CM-SU': ('Sud', 'South'),
          'CM-SW': ('Sud-Ouest', 'South-West')}
ANGLO = {'CM-NW', 'CM-SW'}


def plain(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).upper()


def length_for(w_m, h_m):
    if max(w_m, h_m) <= 8000 * CELL:
        return 6, 'landscape' if w_m >= h_m else 'portrait'
    if w_m >= h_m and w_m <= 40000 * CELL and h_m <= 32000 * CELL:
        return 7, 'landscape'
    if h_m > w_m and h_m <= 40000 * CELL and w_m <= 32000 * CELL:
        return 7, 'portrait'
    assert max(w_m, h_m) <= 160000 * CELL
    return 8, 'landscape' if w_m >= h_m else 'portrait'


def m_lat(phi):
    p = math.radians(phi)
    return 111132.954 - 559.822 * math.cos(2 * p) + 1.175 * math.cos(4 * p)


def m_lon(phi):
    p = math.radians(phi)
    return 111412.84 * math.cos(p) - 93.5 * math.cos(3 * p) + 0.118 * math.cos(5 * p)


def main(db, stats_path):
    stats = {s['osm']: s for s in json.load(open(stats_path)) if s['level'] == 8}
    q = """LOAD spatial;
    SELECT a.osm, a."name",
      (SELECT d."name" FROM admin d WHERE d.level=6 AND ST_Intersects(d.g, ST_PointOnSurface(a.g)) LIMIT 1) dept,
      (SELECT c."name" FROM admin c WHERE c.level=7 AND ST_Intersects(c.g, ST_PointOnSurface(a.g)) LIMIT 1) cu,
      ST_AsGeoJSON(ST_SimplifyPreserveTopology(a.g, 0.0002)) gj
    FROM admin a WHERE a.level=8;"""
    rows = json.loads(subprocess.run(['duckdb', db, '-json'], input=q, capture_output=True, text=True, check=True).stdout)
    used, zones, feats = set(), [], []
    recs = []
    for r in rows:
        s = stats.get(r['osm'])
        if not s or not r['dept']:
            continue
        name = r['name']
        m = re.match(r'^(.*?)\s+([IVX]+|\d)$', name)
        key = None
        if m and m.group(1) in CITY:
            num = ROMAN.get(m.group(2)) or int(m.group(2))
            key = f'{CITY[m.group(1)]}{num}'
        recs.append((r, s, key))
    # numbered city communes first, then by région, département, name: a stable, readable order
    recs.sort(key=lambda t: (t[2] is None, t[1]['region'] or '', t[0]['dept'], plain(t[0]['name'])))
    for r, s, key in recs:
        if key is None:
            dk = DEPT[r['dept']]
            letters = [c for c in plain(r['name']) if c.isalpha()]
            key = next((dk + c for c in letters if dk + c not in used), None) or \
                next(dk + c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if dk + c not in used)
        assert key not in used, key
        used.add(key)
        west, south = math.floor(s['w'] * 1000) / 1000, math.floor(s['s'] * 1000) / 1000
        east, north = math.ceil(s['e'] * 1000) / 1000, math.ceil(s['n_'] * 1000) / 1000
        ref = round((south + north) / 2, 3)
        w_m, h_m = (east - west) * m_lon(ref), (north - south) * m_lat(ref)
        n, orient = length_for(w_m, h_m)
        reg = s['region']
        fr, en = REGION.get(reg, ('', ''))
        city = re.match(r'^(.*?)\s+([IVX]+|\d)$', r['name'])
        label_en = r['name']
        if city and city.group(1) in CITY:
            num = ROMAN.get(city.group(2)) or int(city.group(2))
            label_en = f"{CITY_EN.get(city.group(1), city.group(1))} {num}"
        zones.append({
            'index': len(zones), 'key': key, 'name': r['name'], 'nameEn': label_en,
            'departement': r['dept'], 'communauteUrbaine': r['cu'], 'region': reg, 'regionFr': fr, 'regionEn': en,
            'language': 'en' if reg in ANGLO else 'fr', 'osm': r['osm'], 'areaKm2': s['area_km2'],
            'box': [west, south, east, north],
            'grid': {'west': west, 'south': south, 'refLat': ref, 'orient': orient, 'length': n, 'cellMetres': CELL},
            'structures2026': s['buildings'],
            'campostCode': None,
        })
        g = r['gj'] if isinstance(r['gj'], dict) else json.loads(r['gj'])
        feats.append({'type': 'Feature', 'properties': {'key': key, 'name': r['name']}, 'geometry': g})
    out = {'country': 'CM', 'version': '2026-10-18', 'frozen': False,
           'note': 'Index, key, frame and length are frozen once the first code is issued; campostCode is filled when Campost publishes its commune postal codes.',
           'zones': zones}
    json.dump(out, open(os.path.join(REPO, 'model', 'zones.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(REPO, 'model', 'zones.geojson'), 'w'),
              ensure_ascii=False, separators=(',', ':'))
    from collections import Counter
    print(len(zones), 'zones; lengths', dict(Counter(z['grid']['length'] for z in zones)),
          '; city keys', sorted(z['key'] for z in zones if z['key'][3].isdigit()))


if __name__ == '__main__':
    main(*sys.argv[1:3])
