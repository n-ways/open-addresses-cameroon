#!/usr/bin/env python3
"""Tests of the Cameroon reference engine (cm_engine.py) on the frozen register.

  python3 engine/reference/test_cm.py
"""
import json, math, os, random, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cm_border as B  # noqa: E402
import cm_engine as e  # noqa: E402
import plate_names as P  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
VECTORS = os.path.join(HERE, 'vectors.json')


class Damm(unittest.TestCase):
    def test_published_vector(self):
        self.assertEqual(e.damm('572'), 4)

    def test_every_single_error_and_swap(self):
        rnd = random.Random(7)
        for _ in range(300):
            s = ''.join(rnd.choice('0123456789') for _ in range(14))
            c = e.damm(s)
            for i in range(len(s)):
                for d in '0123456789':
                    if d != s[i]:
                        self.assertNotEqual(e.damm(s[:i] + d + s[i + 1:]), c)
                if i + 1 < len(s) and s[i] != s[i + 1]:
                    self.assertNotEqual(e.damm(s[:i] + s[i + 1] + s[i] + s[i + 2:]), c)


class NameKeys(unittest.TestCase):
    def test_equal(self):
        for group in (('Ngoa-Ekellé', 'Ngoa Ekele', 'NGOA EKELLE'), ('Douala', 'Duala'), ('Djoungolo', 'Joungolo'),
                      ('Tchinga', 'Chinga'), ('Quartier Mvog-Mbi', 'Mvog Mbi'), ('St Michel', 'Saint-Michel')):
            self.assertEqual(len({e.name_key(x) for x in group}), 1, group)

    def test_digits_never_squeezed(self):
        self.assertNotEqual(e.name_key('Mile 22'), e.name_key('Mile 2'))

    def test_generic(self):
        self.assertTrue(e.is_generic('Village') and e.is_generic('quarter') and e.is_generic('Campement'))
        self.assertFalse(e.is_generic('Villa Rosa'))


class Plates(unittest.TestCase):
    def test_limits(self):
        self.assertTrue(P.fits('Etetak', 'fr'))
        self.assertFalse(P.fits('Ngoa-Ekellé Centre Ville', 'fr'))
        self.assertFalse(P.fits('Mile 4', 'en'))  # no digit in a plate name


class Register(unittest.TestCase):
    def test_one_area_per_number(self):
        for k, v in e.names()['names'].items():
            last = v['range'][0] - 1
            for zk, ix, c, lo, hi in v['blocks']:
                self.assertEqual(lo, last + 1, k)  # blocks follow each other, never overlap
                self.assertGreaterEqual(hi - lo + 1, 2 * c)  # room to grow inside the block
                self.assertEqual(len(str(lo)), v['digits'])
                self.assertLessEqual(v['digits'], 5)  # never more than five digits
                last = hi
            self.assertLessEqual(last, v['range'][0] - 1 + int(9 * 10 ** (v['digits'] - 1) * (1 - e.NAME_SPARE)))

    def test_machine_round_trip(self):
        rnd = random.Random(11)
        reg = json.load(open(os.path.join(e.REPO, 'engine', 'data', 'register.json'), encoding='utf-8'))
        for a in rnd.sample([a for a in reg['areas'] if a['blocks']], 300):
            lo, hi = a['blocks'][0]
            n = rnd.randint(lo, hi)
            m = e.machine(a['zone'], a['index'], n, a['nameId'])
            p = e.parse_machine(m)
            self.assertTrue(p['valid'], m)
            r = e.resolve_remembered(f"{a['name']} {e.group_number(n)}")
            self.assertEqual(r['code'], m)
            bad = m[:-1] + str((int(m[-1]) + 1) % 10)
            self.assertFalse(e.parse_machine(bad)['valid'])

    def test_refusals(self):
        with self.assertRaises(ValueError):
            e.resolve_remembered('Nulle Part 1234')


class Spots(unittest.TestCase):
    def test_round_trip(self):
        rnd = random.Random(3)
        done = 0
        while done < 200:
            lat, lon = rnd.uniform(1.7, 13.0), rnd.uniform(8.5, 16.1)
            if e.zone_at(lat, lon) is None:
                continue
            code = e.spot_encode(lat, lon)
            la, lo = e.spot_decode(code)
            self.assertLess(abs(la - lat) * 110574, 6)
            self.assertLess(abs(lo - lon) * 111320, 6.5)
            self.assertEqual(e.spot_encode(la, lo), code)
            done += 1

    def test_example(self):
        self.assertEqual(e.spot_encode(3.866511, 11.517935), 'CM-YDE1 E0532 N0071')

    def test_outside_every_outline(self):
        # Yoyo Bar, Yaounde II: a compound in a sliver between outlines takes the nearest one, Yaounde VII
        lat, lon = 3.8751747, 11.4844409
        self.assertIsNone(e.zone_at(lat, lon))
        self.assertEqual(e.spot_zone(lat, lon), 'YDE7')
        code = e.spot_encode(lat, lon)
        self.assertEqual(code, 'CM-YDE7 E0826 N0499')
        la, lo = e.spot_decode(code)
        self.assertLess(abs(la - lat) * 110574, 6)
        self.assertLess(abs(lo - lon) * 111320, 6.5)
        # Nangadjango, Kribi I: a structure at sea 10.9 km from the outline, beyond the frame: its nearest cell
        self.assertEqual(e.spot_encode(2.9204201, 9.7996603), 'CM-KRI1 E0000 N3321')
        with self.assertRaises(ValueError):
            e.spot_encode(2.0, 7.0)  # the open sea: no outline within 12 km


class Numbering(unittest.TestCase):
    def test_hilbert(self):
        self.assertEqual([e.hilbert_index(1, x, y) for x, y in ((0, 0), (0, 1), (1, 1), (1, 0))], [0, 1, 2, 3])

    def test_block_and_infill(self):
        pts = {f'c{i}': (11.5 + i * 0.0001, 3.86 + (i % 5) * 0.0001) for i in range(40)}
        box = (11.4999, 3.8599, 11.5041, 3.8606)
        nums = e.issue_numbers(pts, box, (1000, 1199))
        self.assertEqual(len(set(nums.values())), 40)
        self.assertTrue(all(1000 <= n <= 1132 for n in nums.values()))  # the tail reserve stays free
        n = e.provisional_number((11.50005, 3.86), nums, pts, box, (1000, 1199))
        self.assertNotIn(n, nums.values())


class Border(unittest.TestCase):
    """The national border (engine/data/border.geojson) and the 300 m rule."""

    @classmethod
    def setUpClass(cls):
        cls.b = B.Border()

    def test_file_is_small_and_its_error_bounded(self):
        self.assertLess(os.path.getsize(B.BORDER_JSON), 1 << 20)
        self.assertLessEqual(self.b.error_m, 60)
        self.assertEqual(self.b.limit_m, B.BORDER_M - self.b.error_m)

    def test_points(self):
        for lat, lng in ((3.8480, 11.5021), (4.0511, 9.7679), (10.5956, 14.3247), (2.2075747, 9.9006782)):
            self.assertTrue(self.b.inside(lat, lng), (lat, lng))
            self.assertFalse(self.b.abroad(lat, lng), (lat, lng))
        # across the border, in a neighbouring country: about 3 km, about 380 m
        for lat, lng in ((12.2598052, 14.518541), (2.2082029, 9.8957734)):
            self.assertFalse(self.b.inside(lat, lng), (lat, lng))
            self.assertTrue(self.b.abroad(lat, lng), (lat, lng))
        self.assertTrue(self.b.abroad(0.0, 0.0))
        self.assertGreater(self.b.outside_m(0.0, 0.0), 1e6)

    def test_distance_is_measured_in_metres(self):
        # a point 100 m east of a vertical segment, at the equator and at 10 degrees north
        for lat in (0.0, 10.0):
            k = 111320 * math.cos(math.radians(lat))
            self.assertAlmostEqual(B.seg_m(lat, 100 / k, (0.0, lat - 1), (0.0, lat + 1)), 100.0, places=6)


class Vectors(unittest.TestCase):
    @unittest.skipUnless(os.path.exists(VECTORS), 'run tools/vectors.py first')
    def test_vectors(self):
        v = json.load(open(VECTORS, encoding='utf-8'))
        for w, k in v['nameKeys']:
            self.assertEqual(e.name_key(w), k)
        for s in v['spots']:
            self.assertEqual(e.spot_encode(s['lat'], s['lon']), s['code'])
        issued = 0
        for s in v['spotsOutside']:
            self.assertIsNone(e.zone_at(s['lat'], s['lon']))
            if 'error' in s:
                with self.assertRaises(ValueError):
                    e.spot_encode(s['lat'], s['lon'])
                continue
            issued += 'machine' in s
            self.assertEqual(e.spot_zone(s['lat'], s['lon']), s['zone'])
            self.assertEqual(e.spot_encode(s['lat'], s['lon']), s['code'])
            self.assertEqual(list(e.spot_decode(s['code'])), s['decoded'])
        self.assertEqual(issued, 240)


if __name__ == '__main__':
    unittest.main()
