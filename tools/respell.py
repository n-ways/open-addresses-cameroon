#!/usr/bin/env python3
"""Respelling plate names after issue, without touching a code.

  python3 tools/respell.py <spelled repo copy>

The issued register keeps every name id, key, range and block. From a copy of this repository in
which tools/name-ranges.py and tools/build-register.py ran with the current rules, it takes only
how each plate name is written: its accents, hyphens and apostrophes. A name key never changes
(cm_engine.name_key folds all of those), so no number, range or check digit moves.

The spelling rule: variants of a name take the spelling with its
accents ("Bessengué", not "Bessengue"), then the one more people live under; and a name given in
two scripts is written on its plate in the Latin one. The one key that changes is Blangoua's
(LOGB-012), whose plate had been its Arabic name ("بلانقوا", an empty key): it keeps its name id 1,
its range and its blocks, so its codes keep their machine form. Every change is recorded in
model/areas/respell.json.
"""
import json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'engine', 'reference'))
import cm_engine as E  # noqa: E402

KEY_CHANGES = {'LOGB-012'}  # Blangoua: its Arabic plate had an empty key
DISPLAY = ('name', 'officialName', 'aliases', 'plateCandidates')


def load(*p):
    return json.load(open(os.path.join(*p), encoding='utf-8'))


def save(obj, *p, indent=None):
    json.dump(obj, open(os.path.join(*p), 'w', encoding='utf-8'), ensure_ascii=False, indent=indent)


def main(spelled):
    reg = load(REPO, 'engine', 'data', 'register.json')
    new = {a['key']: a for a in load(spelled, 'engine', 'data', 'register.json')['areas']}
    changes, key_of = [], {}
    for a in reg['areas']:
        b = new[a['key']]
        # everything but the spelling (the copy's name ids are its own numbering: the issued ones stay)
        rest = lambda x: {k: v for k, v in x.items() if k not in DISPLAY and k not in ('nameKey', 'nameId')}
        if rest(a) != rest(b):
            sys.exit(f"{a['key']}: more than its spelling differs")
        if a['name'] == b['name']:
            for f in DISPLAY:
                a[f] = b.get(f, a.get(f))
            continue
        if E.name_key(a['name']) != E.name_key(b['name']) and a['key'] not in KEY_CHANGES:
            sys.exit(f"{a['key']}: {a['name']} -> {b['name']} is not a respelling")
        changes.append({'area': a['key'], 'was': a['name'], 'now': b['name']})
        key_of[E.name_key(a['name'])] = E.name_key(b['name'])
        for f in DISPLAY:
            if f in b:
                a[f] = b[f]  # nameId is never copied
        if 'nameKey' in a:
            a['nameKey'] = E.name_key(b['name'])
    # the national names: each key's plate as the areas now write it (most areas', then accents)
    spelled_names = {n['key']: n['plateName'] for n in load(spelled, 'engine', 'data', 'register.json')['names']}
    for n in reg['names']:
        k = key_of.get(n['key'], n['key']) if n['key'] == '' else n['key']
        n['key'], n['plateName'] = k, spelled_names.get(k, n['plateName'])
    save(reg, REPO, 'engine', 'data', 'register.json')

    # model/areas: the same spellings, ids and blocks kept
    nr = load(REPO, 'model', 'areas', 'name-ranges.json')
    snr = load(spelled, 'model', 'areas', 'name-ranges.json')['names']
    out = {}
    for k, v in nr['names'].items():
        nk = key_of.get(k, k) if k == '' else k
        if nk in snr:
            for f in ('plateName', 'officialNames', 'aliases'):
                if f in snr[nk]:
                    v[f] = snr[nk][f]
        out[nk] = v
    nr['names'] = out
    save(nr, REPO, 'model', 'areas', 'name-ranges.json', indent=0)
    areg = load(REPO, 'model', 'areas', 'register.json')
    sreg = load(spelled, 'model', 'areas', 'register.json')
    for zk, z in areg.items():
        sv = {v['index']: v for v in sreg[zk]['villages']}
        for v in z['villages']:
            for f in ('plateName', 'plateCandidates'):
                if f in sv[v['index']]:
                    v[f] = sv[v['index']][f]
    save(areg, REPO, 'model', 'areas', 'register.json', indent=0)
    save({'note': __doc__.split('\n\n', 2)[2].strip(), 'changes': changes}, REPO, 'model', 'areas', 'respell.json', indent=1)
    print(len(changes), 'areas respelled;', sum(1 for c in changes if E.name_key(c['was']) != E.name_key(c['now'])), 'key changed')


if __name__ == '__main__':
    main(sys.argv[1])
