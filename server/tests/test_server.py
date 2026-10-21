"""Tests of the registry server on the fixture registry (server/testdata).

  python3 -m unittest discover -s server/tests -t .     (from the repository root)
"""
import gzip
import json
import os
import shutil
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from server import register as R
from server import store as S
from server.api import make_server
from server.service import Service

HERE = os.path.dirname(os.path.abspath(__file__))
TESTDATA = os.path.join(os.path.dirname(HERE), 'testdata')
FIXTURE = os.path.join(TESTDATA, 'registry')
# 24 real compounds, one per arrondissement, whose entrance lies in no arrondissement outline
GAPS = os.path.join(TESTDATA, 'gaps')
KEY = 'test-issuing-key'


def quiet(*_a, **_k):
    pass


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f)


def read_bytes(path):
    with (gzip.open(path) if path.endswith('.gz') else open(path, 'rb')) as f:
        return f.read()


class Running:
    """A server on a fresh copy of the fixture database, on a free port."""

    def __init__(self, keys=(KEY,), per_day=1000, registry=FIXTURE):
        self.dir = tempfile.mkdtemp(prefix='nways-cm-')
        self.db = os.path.join(self.dir, 'addresses.sqlite')
        S.import_registry(registry, self.db, log=quiet)
        self.svc = Service(S.Store(self.db), keys, per_day)
        self.srv = make_server(self.svc, '127.0.0.1', 0, ['*'])
        self.url = 'http://127.0.0.1:%d' % self.srv.server_address[1]
        self.thread = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.thread.start()

    def call(self, method, path, body=None, key=KEY, headers=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(self.url + path, data=data, method=method)
        if body is not None:
            req.add_header('Content-Type', 'application/json')
        if key:
            req.add_header('Authorization', 'Bearer ' + key)
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read() or b'null'), r.headers
        except urllib.error.HTTPError as e:
            with e:
                return e.code, json.loads(e.read() or b'null'), e.headers

    def get(self, path):
        return self.call('GET', path, key=None)

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()
        self.svc.st.close()
        shutil.rmtree(self.dir)


def uncompressed(folder):
    out = {}
    for f in sorted(os.listdir(folder)):
        p = os.path.join(folder, f)
        out[f] = read_bytes(p)
    return out


class ImportExport(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix='nways-cm-')
        self.db = os.path.join(self.dir, 'a.sqlite')

    def tearDown(self):
        shutil.rmtree(self.dir)

    def copy_fixture(self):
        d = os.path.join(self.dir, 'registry')
        shutil.copytree(FIXTURE, d)
        return d

    def test_round_trip_is_byte_identical(self):
        n = S.import_registry(FIXTURE, self.db, log=quiet)
        self.assertEqual(n, load(os.path.join(FIXTURE, 'MANIFEST.json'))['codes'])
        out = os.path.join(self.dir, 'out')
        S.export_registry(self.db, out, log=quiet)
        self.assertEqual(uncompressed(out), uncompressed(FIXTURE))

    def test_reimport_is_a_no_op(self):
        S.import_registry(FIXTURE, self.db, log=quiet)
        said = []
        S.import_registry(FIXTURE, self.db, log=said.append)
        self.assertIn('nothing to do', said[0])

    def test_tampered_file_is_refused(self):
        d = self.copy_fixture()
        p = os.path.join(d, 'DLA1.csv.gz')
        raw = read_bytes(p).replace(b'Bonapriso 1401', b'Bonapriso 1402', 1)
        with gzip.open(p, 'wb') as f:
            f.write(raw)
        with self.assertRaisesRegex(S.RegistryError, 'SHA-256'):
            S.import_registry(d, self.db, log=quiet)
        self.assertFalse(os.path.exists(self.db))

    def test_wrong_totals_are_refused(self):
        d = self.copy_fixture()
        p = os.path.join(d, 'MANIFEST.json')
        m = load(p)
        m['codes'] += 1
        save(p, m)
        with self.assertRaisesRegex(S.RegistryError, 'MANIFEST'):
            S.import_registry(d, self.db, log=quiet)

    def test_missing_file_is_refused(self):
        d = self.copy_fixture()
        os.remove(os.path.join(d, 'DLA1.csv.gz'))
        with self.assertRaises(S.RegistryError):
            S.import_registry(d, self.db, log=quiet)

    def test_other_country_is_refused(self):
        d = self.copy_fixture()
        p = os.path.join(d, 'MANIFEST.json')
        m = load(p)
        m['country'] = 'XX'
        save(p, m)
        with self.assertRaisesRegex(S.RegistryError, 'XX'):
            S.import_registry(d, self.db, log=quiet)

    def test_local_codes_are_kept_unless_replace(self):
        S.import_registry(FIXTURE, self.db, log=quiet)
        svc = Service(S.Store(self.db), [KEY], 10)
        svc.issue({'lat': 4.0700, 'lng': 9.7350}, 'key:test')
        svc.st.close()
        with self.assertRaisesRegex(S.RegistryError, 'Export it first'):
            S.import_registry(FIXTURE, self.db, log=quiet)
        S.import_registry(FIXTURE, self.db, replace=True, log=quiet)
        self.assertEqual(S.local_changes(self.db), 0)

    def test_grid_index_without_rtree(self):
        """Where SQLite has no R*Tree, the integer grid answers the same radius searches."""
        S.import_registry(FIXTURE, self.db, log=quiet)
        rtree = S.Store(self.db)
        real = S.has_rtree
        S.has_rtree = lambda con: False
        try:
            db2 = os.path.join(self.dir, 'grid.sqlite')
            S.import_registry(FIXTURE, db2, log=quiet)
        finally:
            S.has_rtree = real
        grid = S.Store(db2)
        self.assertEqual(grid.spatial, 'grid')
        for lat, lng, m in ((4.0243022, 9.6904852, 300), (4.0384314, 9.6990288, 120), (4.045, 9.70, 500)):
            a = [(round(d, 6), r['machine']) for d, r in rtree.near(lat, lng, m)]
            b = [(round(d, 6), r['machine']) for d, r in grid.near(lat, lng, m)]
            self.assertEqual(a, b)
        self.assertTrue(rtree.near(4.0243022, 9.6904852, 300))
        rtree.close()
        grid.close()

    def test_csv_quoting_matches_the_issuer(self):
        self.assertEqual(S.csv_line(['a', 'b,c', 'say "x"', '', ' lead', '\\.']), 'a,"b,c","say ""x""",," lead","\\."\n')


class Endpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Running()
        cls.code = 'CM-DLA1-015-1401-6'

    @classmethod
    def tearDownClass(cls):
        cls.s.close()

    def ok(self, path):
        st, body, _h = self.s.get(path)
        self.assertEqual(st, 200, body)
        return body

    def err(self, path, status, code):
        st, body, _h = self.s.get(path)
        self.assertEqual(st, status, body)
        self.assertEqual(body['error']['code'], code)
        self.assertTrue(body['error']['message'])
        return body

    def test_health_and_info(self):
        h = self.ok('/v1/health')
        self.assertEqual((h['status'], h['country'], h['codes']), ('ok', 'CM', 26154))
        i = self.ok('/v1/info')
        self.assertEqual(i['codes'], 26154)
        self.assertEqual(len(i['zones']), 360)
        self.assertEqual(i['credit'], R.CREDIT)
        self.assertIn('data', i['licences'])

    def test_card_has_every_registry_column(self):
        c = self.ok('/v1/codes/' + self.code)
        self.assertEqual(list(c['record']), S.CODE_COLS)
        self.assertEqual(c['home'], 'Bonapriso 1401')
        self.assertEqual(c['written'], 'Bonapriso 14 01')
        self.assertEqual(c['spoken'], 'Bonapriso, 14 01')
        self.assertEqual(c['zone']['key'], 'DLA1')
        self.assertEqual(c['area']['key'], 'DLA1-015')
        self.assertEqual(c['area']['zoneName'], 'Douala I')
        self.assertEqual(c['spotCode'], 'CM-DLA1 E0449 N0268')
        self.assertEqual(c['plusCode'], '6FPF2MFR+P5H')
        self.assertNotIn('6', c['written'].split()[-1])  # people never see the check digit

    def test_card_errors(self):
        self.err('/v1/codes/CM-DLA1-015-1401-5', 422, 'check_digit')
        self.err('/v1/codes/CM-DLA1-015-1401', 400, 'bad_code')
        self.err('/v1/codes/hello', 400, 'bad_code')
        self.err('/v1/codes/CM-DLA1-999-1401-1', 404, 'unknown_area')
        self.err('/v1/codes/CM-DLA1-015-9401-1', 404, 'not_in_area')
        reg = R.Register()
        free = reg.forms(reg.by_key['DLA1-015'], 2929)['machine']
        self.err('/v1/codes/' + free, 404, 'not_issued')

    def test_find_remembered_any_spelling(self):
        for q in ('Bonapriso 14 01', 'bonapriso 1401', 'BONAPRISO1401', '  Bonapriso   14 01 ', 'Bonapriso 14 01-6', 'Bonapriso · 14 01'):
            b = self.ok('/v1/find?q=' + urllib.request.quote(q))
            self.assertEqual(b['matches'][0]['machine'], self.code, q)
            self.assertEqual(b['kind'], 'remembered')

    def test_find_accents_and_official_alias(self):
        b = self.ok('/v1/find?q=' + urllib.request.quote('BESSENGUE 10 001'))
        self.assertEqual(b['matches'][0]['home'], 'Bessengué 10001')
        b = self.ok('/v1/find?q=' + urllib.request.quote('Mboussa Sengué 1001'))
        self.assertEqual(b['matches'][0]['machine'], 'CM-DLA1-029-1001-5')

    def test_find_official_address(self):
        b = self.ok('/v1/find?limit=3&q=' + urllib.request.quote('rue richard bell (n° 1.139), douala'))
        self.assertEqual(b['kind'], 'officialAddress')
        self.assertGreater(b['total'], 3)
        self.assertEqual(len(b['matches']), 3)
        self.assertTrue(all(m['officialAddress'] == 'Rue Richard Bell(N°1.139), Douala' for m in b['matches']))

    def test_find_machine_and_spot(self):
        b = self.ok('/v1/find?q=' + self.code.lower())
        self.assertEqual((b['kind'], b['matches'][0]['machine'], b['checked']), ('machine', self.code, True))
        spot = b['matches'][0]['spotCode']
        b = self.ok('/v1/find?q=' + urllib.request.quote(spot))
        self.assertEqual(b['kind'], 'spot')

    def test_find_errors(self):
        self.err('/v1/find?q=', 400, 'missing_q')
        self.err('/v1/find?q=CM-DLA1-015-1401-5', 422, 'check_digit')
        self.err('/v1/find?q=Bonapriso%201401-5', 422, 'check_digit')
        self.err('/v1/find?q=Bonapriso%20140', 404, 'wrong_length')
        self.err('/v1/find?q=Bonapriso%202929', 404, 'not_issued')
        self.err('/v1/find?q=Bonapriso%209999', 404, 'not_issued')
        self.err('/v1/find?q=Qwertyville%20123', 404, 'unknown_name')
        self.err('/v1/find?q=hello', 404, 'not_found')

    def test_at(self):
        c = self.ok('/v1/codes/' + self.code)
        e = c['entrance']
        b = self.ok('/v1/at?lat=%s&lng=%s' % (e['lat'], e['lng'] + 0.00005))
        self.assertEqual((b['status'], b['code']['machine']), ('found', self.code))
        b = self.ok('/v1/at?lat=4.07&lng=9.735')
        self.assertEqual(b['status'], 'none')
        self.assertTrue(b['area']['key'].startswith('DLA'))
        self.err('/v1/at?lat=6.455&lng=3.394', 404, 'outside')
        self.err('/v1/at?lat=x&lng=9', 400, 'bad_lat')
        self.err('/v1/at?lat=1', 400, 'missing_lng')

    def test_near(self):
        e = self.ok('/v1/codes/' + self.code)['entrance']
        b = self.ok('/v1/near?lat=%s&lng=%s&radius=200' % (e['lat'], e['lng']))
        self.assertEqual(b['codes'][0]['machine'], self.code)
        d = [x['distanceM'] for x in b['codes']]
        self.assertEqual(d, sorted(d))
        self.assertTrue(all(x <= 200 for x in d))
        self.assertLessEqual(len(self.ok('/v1/near?lat=%s&lng=%s&radius=500&limit=3' % (e['lat'], e['lng']))['codes']), 3)
        self.err('/v1/near?lat=%s&lng=%s&radius=501' % (e['lat'], e['lng']), 400, 'bad_radius')
        self.err('/v1/near?lat=%s&lng=%s&limit=101' % (e['lat'], e['lng']), 400, 'bad_limit')

    def test_verify(self):
        b = self.ok('/v1/verify?code=' + self.code)
        self.assertEqual((b['valid'], b['issued'], b['checkDigit']), (True, True, 'ok'))
        b = self.ok('/v1/verify?code=CM-DLA1-015-1401-5')
        self.assertEqual((b['valid'], b['checkDigit']), (False, 'wrong'))
        self.assertNotIn('machine', b)  # a wrong check digit is never corrected
        b = self.ok('/v1/verify?code=CM-DLA1-015-1401')
        self.assertEqual((b['valid'], b['checkDigit']), (False, 'absent'))
        b = self.ok('/v1/verify?code=nonsense')
        self.assertFalse(b['syntax'])
        self.err('/v1/verify', 400, 'missing_code')

    def test_spot(self):
        b = self.ok('/v1/spot?lat=4.0243022&lng=9.6904852')
        self.assertEqual((b['spot'], b['zone']['key']), ('CM-DLA1 E0449 N0268', 'DLA1'))
        d = self.ok('/v1/spot/decode?code=' + urllib.request.quote(b['spot']))
        self.assertEqual(d['code']['machine'], self.code)
        self.err('/v1/spot?lat=6.455&lng=3.394', 404, 'outside')
        # in no arrondissement outline: the nearest outline within 12 km whose frame holds the point
        b = self.ok('/v1/spot?lat=3.8751747&lng=11.4844409')
        self.assertEqual((b['spot'], b['zone']['key']), ('CM-YDE7 E0826 N0499', 'YDE7'))
        self.err('/v1/spot/decode?code=hello', 400, 'bad_spot')
        self.err('/v1/spot/decode?code=CM-DLA1%20E123%20N1234', 400, 'bad_spot')
        self.err('/v1/spot/decode?code=CM-DLA1%20E01234%20N1234', 422, 'bad_spot')
        self.err('/v1/spot/decode?code=CM-ZZZ9%20E0123%20N1234', 422, 'bad_spot')

    def test_zones_and_areas(self):
        z = self.ok('/v1/zones')
        self.assertEqual(z['total'], 360)
        one = self.ok('/v1/zones/dla1')
        self.assertEqual((one['key'], one['codes'], len(one['areas'])), ('DLA1', 26154, 37))
        self.err('/v1/zones/XYZ', 404, 'unknown_zone')
        a = self.ok('/v1/areas/DLA1-015')
        self.assertEqual((a['plateName'], a['codes'], a['blocks']), ('Bonapriso', 962, [[1000, 2929]]))
        self.assertEqual(self.ok('/v1/areas/%d' % a['id'])['key'], 'DLA1-015')
        self.err('/v1/areas/99999', 404, 'unknown_area')
        m = self.ok('/v1/areas?name=' + urllib.request.quote('Place du Défilé'))
        self.assertEqual([x['key'] for x in m['areas']], ['DLA1-031'])
        m = self.ok('/v1/areas?name=douala')
        self.assertTrue({'DLA1-031', 'DLA1-033', 'DLA1-035'} <= {x['key'] for x in m['areas']})
        self.err('/v1/areas?name=Qwertyville', 404, 'unknown_name')
        self.err('/v1/areas', 400, 'missing_name')

    def test_paging(self):
        seen, after = [], ''
        while True:
            b = self.ok('/v1/zones/DLA1/codes?limit=1000&after=' + after)
            seen += [c['machine'] for c in b['codes']]
            if not b['next']:
                break
            after = b['next']
        self.assertEqual(len(seen), 26154)
        self.assertEqual(seen, sorted(seen))
        self.err('/v1/zones/DLA1/codes?limit=0', 400, 'bad_limit')
        self.err('/v1/zones/QQQQ/codes', 404, 'unknown_zone')

    def test_routing_errors(self):
        self.err('/v1/nothing', 404, 'not_found')
        st, body, _h = self.s.call('DELETE', '/v1/codes/' + self.code)
        self.assertEqual((st, body['error']['code']), (405, 'method_not_allowed'))

    def test_cors(self):
        st, _b, h = self.s.call('GET', '/v1/health', key=None, headers={'Origin': 'https://example.org'})
        self.assertEqual(h['Access-Control-Allow-Origin'], '*')


class Issue(unittest.TestCase):
    def setUp(self):
        self.s = Running(per_day=1000)

    def tearDown(self):
        self.s.close()

    def post(self, body, key=KEY):
        return self.s.call('POST', '/v1/codes', body, key=key)

    def test_parity_with_the_issuer(self):
        """Every point of server/testdata/parity.json, posted in order, gets the number,
        forms and blocks the N-Ways issuer gives it."""
        cases = load(os.path.join(TESTDATA, 'parity.json'))
        status = {'exists': 409, 'outside': 422, 'too_far': 422, 'full': 409}
        codes = {'too_far': 'too_far', 'exists': 'exists', 'outside': 'outside', 'full': 'full'}
        for c in cases['issue']:
            body = {k: v for k, v in c['input'].items() if k != 'note'}
            st, out, _h = self.post(body)
            want = c['expected']
            if 'error' in want:
                self.assertEqual(st, status[want['error']], (c, out))
                self.assertEqual(out['error']['code'], codes[want['error']], c)
                if 'existing' in want:
                    self.assertEqual(out['existing']['machine'], want['existing'])
                continue
            self.assertEqual(st, 201, (c, out))
            got = {'machine': out['machine'], 'home': out['home'], 'written': out['written'], 'number': out['number'],
                   'area': out['area']['key']}
            self.assertEqual(got, {k: want[k] for k in got}, c['input'].get('note'))
            self.assertEqual(out.get('newBlocks'), want.get('newBlocks'), c['input'].get('note'))
            self.assertEqual((out['status'], out['issued']), ('provisional', 'on-demand'))
        # the extension block and every new code are in the export
        out = os.path.join(self.s.dir, 'export')
        S.export_registry(self.s.db, out, log=quiet)
        areas = read_bytes(os.path.join(out, 'areas.csv.gz')).decode()
        self.assertIn('DLA1-025,', areas)
        self.assertIn(',1000-1409|2390-3149,', areas)
        for unit in ('DLA1', 'DLA5', 'YDE1'):
            rows = read_bytes(os.path.join(out, unit + '.csv.gz')).decode()
            self.assertEqual(rows.count(',on-demand,'), sum(1 for c in cases['issue']
                                                             if 'error' not in c['expected'] and c['expected']['area'].startswith(unit + '-')))
        # and a re-import of that export serves the same codes
        db2 = os.path.join(self.s.dir, 'again.sqlite')
        S.import_registry(out, db2, log=quiet)
        again = os.path.join(self.s.dir, 'again')
        S.export_registry(db2, again, log=quiet)
        self.assertEqual(uncompressed(out), uncompressed(again))

    def test_insert_and_places_parity(self):
        cases = load(os.path.join(TESTDATA, 'parity.json'))
        reg = R.Register()
        st = self.s.svc.st
        for c in cases['insert']:
            a = reg.by_key[c['input']['area']].copy()
            nb = len(a.blocks)
            n = R.insert(reg, a, st.area_numbers(a.key), c['input']['lat'], c['input']['lng'])
            want = c['expected']
            self.assertEqual((n, [list(b) for b in a.blocks], len(a.blocks) - nb), (want['number'], want['blocks'], want['newBlocks']))
        from server import geo
        for c in cases['places']:
            lat, lng = c['input']['lat'], c['input']['lng']
            want = c['expected']
            z = reg.zone_at(lat, lng)
            self.assertEqual(z['key'] if z else None, want.get('zone'))
            if z:
                self.assertEqual(reg.area_at(lat, lng).key, want['area'])
            if 'spot' in want:
                self.assertEqual(reg.spot(lat, lng), want['spot'])
            else:
                self.assertIsNone(z)
                with self.assertRaises(ValueError):
                    reg.spot(lat, lng)
            self.assertEqual(reg.nearest_area(lat, lng).key, want['nearestArea'])
            self.assertEqual(geo.plus_code(lat, lng), want['plusCode'])

    def test_outline_rules(self):
        lat, lng = 4.07, 9.735
        d = 0.00004
        small = [[lng, lat], [lng + d / 4, lat], [lng + d / 4, lat + d / 4], [lng, lat + d / 4]]
        st, out, _h = self.post({'lat': lat, 'lng': lng, 'outline': small})
        self.assertEqual((st, out['error']['code']), (422, 'bad_outline'))
        huge = [[lng, lat], [lng + 0.003, lat], [lng + 0.003, lat + 0.003], [lng, lat + 0.003]]
        st, out, _h = self.post({'lat': lat, 'lng': lng, 'outline': huge})
        self.assertEqual((st, out['error']['code']), (422, 'bad_outline'))
        ring = [[lng, lat], [lng + 0.0001, lat], [lng + 0.0001, lat + 0.0001], [lng, lat + 0.0001], [lng, lat]]
        st, out, _h = self.post({'lat': lat + 0.00005, 'lng': lng + 0.00005, 'outline': ring})
        self.assertEqual(st, 201, out)
        self.assertEqual((out['profile']['class'], out['profile']['structures']), ('residential', 1))
        self.assertGreater(out['profile']['floorAreaM2'], 100)
        # the same building again: inside its outline, then an overlapping outline
        st, again, _h = self.post({'lat': lat + 0.00009, 'lng': lng + 0.00002})
        self.assertEqual((st, again['error']['code'], again['existing']['machine']), (409, 'exists', out['machine']))
        shifted = [[x + 0.00002, y + 0.00002] for x, y in ring]
        st, again, _h = self.post({'lat': lat + 0.00030, 'lng': lng + 0.00030, 'outline': shifted})
        self.assertEqual((st, again['error']['code']), (409, 'exists'))
        # as the issuer: fewer than three points is no outline at all
        st, again, _h = self.post({'lat': lat - 0.01, 'lng': lng, 'outline': [[1, 2]]})
        self.assertEqual((st, again['profile']['structures']), (201, 0))
        st, again, _h = self.post({'lat': lat - 0.02, 'lng': lng, 'outline': 'square'})
        self.assertEqual((st, again['error']['code']), (400, 'bad_outline'))

    def test_auth_and_body_errors(self):
        st, out, _h = self.post({'lat': 4.07, 'lng': 9.735}, key=None)
        self.assertEqual((st, out['error']['code']), (401, 'unauthorised'))
        st, out, _h = self.post({'lat': 4.07, 'lng': 9.735}, key='wrong')
        self.assertEqual((st, out['error']['code']), (401, 'unauthorised'))
        st, out, _h = self.post({'lat': 'x'})
        self.assertEqual((st, out['error']['code']), (400, 'bad_point'))
        st, out, _h = self.post({'lat': 4.07, 'lng': 9.735, 'of': 'CM-DLA1-015-2929-9'})
        self.assertEqual((st, out['error']['code']), (404, 'unknown_code'))
        req = urllib.request.Request(self.s.url + '/v1/codes', data=b'{oops', method='POST',
                                     headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + KEY})
        with self.assertRaises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(req)
        with e.exception:
            self.assertEqual(json.loads(e.exception.read())['error']['code'], 'bad_json')

    def test_key_is_checked_before_the_body(self):
        for key in (None, 'wrong'):
            headers = {'Content-Type': 'text/plain'}
            if key:
                headers['Authorization'] = 'Bearer ' + key
            req = urllib.request.Request(self.s.url + '/v1/codes', data=b'{oops', method='POST', headers=headers)
            with self.assertRaises(urllib.error.HTTPError) as e:
                urllib.request.urlopen(req)
            with e.exception:
                self.assertEqual((e.exception.code, json.loads(e.exception.read())['error']['code']), (401, 'unauthorised'))

    def test_values_that_are_not_numbers(self):
        st, out, _h = self.post({'lat': True, 'lng': 9.735})
        self.assertEqual((st, out['error']['code']), (400, 'bad_point'))
        nan_ring = [[9.735, 4.07], [9.7351, 4.07], [float('nan'), 4.0701]]
        req = urllib.request.Request(self.s.url + '/v1/codes', method='POST',
                                     data=json.dumps({'lat': 4.07, 'lng': 9.735, 'outline': nan_ring}).encode(),
                                     headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + KEY})
        with self.assertRaises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(req)
        with e.exception:
            self.assertEqual((e.exception.code, json.loads(e.exception.read())['error']['code']), (400, 'bad_json'))
        st, out, _h = self.post({'lat': 4.07, 'lng': 9.735, 'outline': [[9.735, 4.07], [9.7351, 4.07], [400, 4.0701]]})
        self.assertEqual((st, out['error']['code']), (400, 'bad_outline'))
        st, out, _h = self.s.get('/v1/areas/%C2%B2')
        self.assertEqual((st, out['error']['code']), (404, 'unknown_area'))
        st, out, _h = self.s.get('/v1/zones/DLA1/codes?limit=%C2%B2')
        self.assertEqual((st, out['error']['code']), (400, 'bad_limit'))
        st, out, _h = self.s.get('/v1/spot/decode?code=CM-ZZZZ%20E0001%20N0001')
        self.assertEqual((st, out['error']['message']), (422, 'Unknown zone ZZZZ.'))

    def test_change_status_and_entrance(self):
        code = 'CM-DLA1-015-1401-6'
        st, out, _h = self.s.call('PATCH', '/v1/codes/' + code, {'status': 'confirmed'})
        self.assertEqual((st, out['status']), (200, 'confirmed'))
        e = out['entrance']
        st, out, _h = self.s.call('PATCH', '/v1/codes/' + code, {'entrance': {'lat': e['lat'] + 0.0002, 'lng': e['lng']}})
        self.assertEqual((st, out['entrance']['kind']), (200, 'gate'))
        self.assertAlmostEqual(out['entrance']['lat'], e['lat'] + 0.0002, places=7)
        st, out, _h = self.s.call('PATCH', '/v1/codes/' + code, {'entrance': {'lat': e['lat'] + 0.002, 'lng': e['lng']}})
        self.assertEqual((st, out['error']['code']), (422, 'too_far'))
        st, out, _h = self.s.call('PATCH', '/v1/codes/' + code, {'status': 'gone'})
        self.assertEqual((st, out['error']['code']), (400, 'bad_status'))
        st, out, _h = self.s.call('PATCH', '/v1/codes/' + code, {'status': 'retired'})
        self.assertEqual((st, out['status']), (200, 'retired'))
        st, out, _h = self.s.call('PATCH', '/v1/codes/' + code, {'status': 'confirmed'})
        self.assertEqual((st, out['error']['code']), (409, 'retired'))
        # a retired code is never found by point, and its number is never given again
        st, at, _h = self.s.get('/v1/at?lat=%s&lng=%s' % (e['lat'], e['lng']))
        self.assertNotEqual((at.get('code') or {}).get('machine'), code)
        st, out, _h = self.s.call('PATCH', '/v1/codes/CM-DLA1-015-2929-9', {'status': 'confirmed'})
        self.assertEqual((st, out['error']['code']), (404, 'unknown_code'))


class Gaps(unittest.TestCase):
    """A point in no arrondissement outline is in Cameroon when the spot-code rule (SPEC 5) gives it
    a zone, as the N-Ways issuer decides: the compounds in the slivers between outlines, along the
    shoreline and the border are found by location, and a new home there can have its code."""
    # a free point 20 m from CM-NDIB-021-100-8, in no outline; its area as the N-Ways service answers
    FREE = (4.4368874, 8.8831956)
    # across the border: in no outline, and no outline within 12 km
    FAR = (11.267793870267274, 11.96458203764192)

    @classmethod
    def setUpClass(cls):
        cls.s = Running(registry=GAPS)
        cls.codes = [r['machine'] for r in cls.s.svc.st.con().execute('SELECT machine FROM codes ORDER BY machine')]

    @classmethod
    def tearDownClass(cls):
        cls.s.close()

    def entrance(self, machine):
        st, c, _h = self.s.get('/v1/codes/' + machine)
        self.assertEqual(st, 200, c)
        return c['entrance']['lat'], c['entrance']['lng']

    def test_fixture_lies_in_no_outline(self):
        self.assertEqual(len(self.codes), 24)
        for m in self.codes:
            lat, lng = self.entrance(m)
            self.assertIsNone(self.s.svc.reg.zone_at(lat, lng), m)
            self.assertTrue(self.s.svc.reg.in_country(lat, lng), m)
        self.assertIsNone(self.s.svc.reg.zone_at(*self.FREE))

    def test_at_finds_each_compound(self):
        for m in self.codes:
            lat, lng = self.entrance(m)
            st, b, _h = self.s.get('/v1/at?lat=%s&lng=%s' % (lat, lng))
            self.assertEqual(st, 200, b)
            self.assertEqual((b['status'], b['code']['machine'], b['distanceM']), ('found', m, 0), m)
            self.assertEqual(b['area']['zone'], m.split('-')[1], m)

    def test_near_and_at_a_free_point(self):
        st, b, _h = self.s.get('/v1/at?lat=%s&lng=%s' % self.FREE)
        self.assertEqual(st, 200, b)
        self.assertEqual((b['status'], b['canIssue'], b['area']['key']), ('none', True, 'NDIB-021'))
        self.assertEqual(b['nearest']['machine'], 'CM-NDIB-021-100-8')
        st, b, _h = self.s.get('/v1/near?lat=%s&lng=%s&radius=50' % self.FREE)
        self.assertEqual((st, [c['machine'] for c in b['codes']]), (200, ['CM-NDIB-021-100-8']))

    def test_far_outside_is_refused(self):
        for path in ('/v1/at', '/v1/near'):
            st, b, _h = self.s.get('%s?lat=%s&lng=%s' % ((path,) + self.FAR))
            self.assertEqual((st, b['error']['code']), (404, 'outside'))
        st, b, _h = self.s.call('POST', '/v1/codes', {'lat': self.FAR[0], 'lng': self.FAR[1]})
        self.assertEqual((st, b['error']['code']), (422, 'outside'))

    def test_issue_door_and_move_in_a_gap(self):
        s = Running(registry=GAPS)
        try:
            lat, lng = self.FREE
            st, c, _h = s.call('POST', '/v1/codes', {'lat': lat, 'lng': lng})
            self.assertEqual(st, 201, c)
            # the number the N-Ways issuer gives here, with CM-NDIB-021-100-8 the area's only code
            self.assertEqual((c['machine'], c['home'], c['area']['key']), ('CM-NDIB-021-240-9', 'Inodo 240', 'NDIB-021'))
            self.assertEqual((c['status'], c['issued']), ('provisional', 'on-demand'))
            self.assertTrue(c['spotCode'].startswith('CM-NDIB '), c['spotCode'])
            st, b, _h = s.get('/v1/at?lat=%s&lng=%s' % self.FREE)
            self.assertEqual((b['status'], b['code']['machine']), ('found', c['machine']))
            st, again, _h = s.call('POST', '/v1/codes', {'lat': lat, 'lng': lng + 0.00001})
            self.assertEqual((st, again['error']['code']), (409, 'exists'))
            st, door, _h = s.call('POST', '/v1/codes', {'lat': lat + 0.0001, 'lng': lng, 'of': c['machine']})
            self.assertEqual((st, door['area']['key']), (201, 'NDIB-021'), door)
            st, moved, _h = s.call('PATCH', '/v1/codes/' + c['machine'],
                                   {'entrance': {'lat': lat - 0.0001, 'lng': lng, 'kind': 'gate'}})
            self.assertEqual(st, 200, moved)
            self.assertEqual(moved['entrance']['kind'], 'gate')
            self.assertTrue(moved['spotCode'].startswith('CM-NDIB '))
        finally:
            s.close()


class Border(unittest.TestCase):
    """The border decides: a point more than 300 m outside Cameroon's national border
    (OpenStreetMap, admin_level 2) is refused with 422 outside, even where the spot-code
    rule gives it a zone; a point inside the border is issued."""
    # 3 km across the border, in a neighbouring country; the spot-code rule gives it zone LOGM
    FAR = (12.2598052, 14.518541)
    # about 380 m across the border, in a neighbouring country; the spot-code rule gives it zone OCEC
    NEAR = (2.2082029, 9.8957734)
    # about 150 m inside the border, in the outline of OCEC
    INSIDE = (2.2075747, 9.9006782)

    def setUp(self):
        self.s = Running(per_day=1000)

    def tearDown(self):
        self.s.close()

    def test_across_the_border_is_refused(self):
        for lat, lng in (self.FAR, self.NEAR):
            # the zone outlines and the spot-code rule alone would accept the point
            self.assertTrue(self.s.svc.reg.in_country(lat, lng))
            self.assertTrue(R.border().abroad(lat, lng))
            st, b, _h = self.s.call('POST', '/v1/codes', {'lat': lat, 'lng': lng})
            self.assertEqual((st, b['error']['code']), (422, 'outside'), b)
            self.assertIn('neighbouring country', b['error']['message'])
        self.assertEqual(self.s.svc.st.con().execute("SELECT count(*) FROM codes WHERE issued = 'on-demand'").fetchone()[0], 0)

    def test_inside_the_border_is_issued(self):
        st, c, _h = self.s.call('POST', '/v1/codes', {'lat': self.INSIDE[0], 'lng': self.INSIDE[1]})
        self.assertEqual(st, 201, c)
        self.assertEqual(c['area']['zone'], 'OCEC')

    def test_entrance_may_not_move_across(self):
        lat, lng = self.INSIDE
        st, c, _h = self.s.call('POST', '/v1/codes', {'lat': lat, 'lng': lng})
        self.assertEqual(st, 201, c)
        b = R.border()
        # walk the entrance west, towards the border, 50 m at a time (each move is within 80 m);
        # the first move that would take it across is refused
        for _ in range(20):
            lng -= 50 / 111320
            st, out, _h = self.s.call('PATCH', '/v1/codes/' + c['machine'], {'entrance': {'lat': lat, 'lng': lng, 'kind': 'gate'}})
            if b.abroad(lat, lng):
                self.assertEqual((st, out['error']['code']), (422, 'outside'), out)
                break
            self.assertEqual(st, 200, out)
        else:
            self.fail('the walk never reached the border')


class Limits(unittest.TestCase):
    def test_daily_limit_per_key(self):
        s = Running(per_day=2)
        try:
            for i in range(2):
                st, out, _h = s.call('POST', '/v1/codes', {'lat': 4.07 + i * 0.001, 'lng': 9.735})
                self.assertEqual(st, 201, out)
            st, out, _h = s.call('POST', '/v1/codes', {'lat': 4.075, 'lng': 9.735})
            self.assertEqual((st, out['error']['code']), (429, 'limit'))
        finally:
            s.close()

    def test_read_only_deployment(self):
        s = Running(keys=())
        try:
            st, out, _h = s.call('POST', '/v1/codes', {'lat': 4.07, 'lng': 9.735})
            self.assertEqual((st, out['error']['code']), (403, 'read_only'))
            self.assertFalse(s.get('/v1/health')[1]['issuing'])
        finally:
            s.close()


if __name__ == '__main__':
    unittest.main()
