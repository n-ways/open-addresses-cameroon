# N-Ways Addressing for Cameroon

**Status: issued on 21 October 2026.** Every compound in Cameroon has an N-Ways code: 7,243,272 of them, provisional until residents confirm them in the N-Ways app. Where a council gives an address (the coded streets of Yaoundé and Douala today, their door numbers once shared), that address is the official one and is shown first, exactly as the council writes it, with the N-Ways code beside it. Campost's commune codes and PLP addresses fill reserved fields the day they are published.

A home's code is **the name of a quarter or village people already say plus a number of three to five digits**:

| Code | Machine form | What it is |
|---|---|---|
| `Bonapriso 14 01` | `CM-DLA1-015-1401-6` | a compound in Douala I |
| `Intendance 137` | `CM-YDE1-011-137-5` | by Yaoundé's Marché Central, on Rue 1.014 (shown first) |
| `Mokolo 18 834` | `CM-YDE2-012-18834-7` | five digits, said as a pair and a hundred: by the Marché Mokolo |
| `Adjap 10 50`, `Adjap 48 50` | | two of 30 places of one name, in different arrondissements: one national range, a block each |
| `CM-DLA1 E0449 N0268` | | any point: its spot code, a 10 m cell of its arrondissement's grid (a point in no outline takes the nearest arrondissement within 12 km, [SPEC §5](engine/SPEC.md#5-spot-codes)) |

The code is unique in the whole country on its own: every area with the same plate name shares one national range of numbers, cut into frozen blocks of twice its compounds, so "Name number" never needs a town after it. No number has more than five digits. People never see or type a check digit: a Damm check over the name's national index, the arrondissement, the area and the number lives in the machine form, for systems. The name is a **plate name** of at most 12 characters and 2 words, with no digit, in French or in English by arrondissement; the official name still finds it. 1,236 areas carry a provisional short name their council may change once; their codes are issued, and the number never changes.

**Complete and open.** The registry in [`registry/`](registry/) holds every issued code of all 360 arrondissements, 7,243,272 rows with their entrance points and building profiles, and anyone can serve it with the ready-made server in [`server/`](server/README.md). The area table flags the arrondissements of the North-West, South-West, Far North, North, Adamawa and East regions, to which the UK FCDO advises against all or all but essential travel (9 February 2026), as context for relief and emergency planning. A code names a place, never a person.

## What is where

| Path | Contents |
|---|---|
| [docs/paper.md](docs/paper.md), [paper.fr.md](docs/paper.fr.md) | the research paper in English and French, also as PDF ([en](docs/n-ways-addressing-cameroon-en.pdf), [fr](docs/n-ways-addressing-cameroon-fr.pdf)): existing systems, data, the model with every formula and worked examples, implementation, evaluation, the designs considered and rejected, and the benefits for citizens, logistics, emergencies and government |
| [docs/paper/](docs/paper/), [docs/figures/](docs/figures/) | the paper's typesetting (pandoc template, style, verified references in `references.bib`, build script) and its figures as TikZ/pgfplots sources with their data, compiled to PDF and SVG |
| [docs/existing-systems.md](docs/existing-systems.md) | verification: Campost and the announced postcodes, the councils' street codes and door numbers, land, data protection; verdict and sources |
| [docs/integration-campost.md](docs/integration-campost.md) | how Campost's and the councils' addresses are shown first when they are shared |
| [docs/model.md](docs/model.md) | the design notes behind every choice |
| [engine/SPEC.md](engine/SPEC.md) | the engine specification (normative) |
| [engine/reference/cm_engine.py](engine/reference/cm_engine.py), [cm_border.py](engine/reference/cm_border.py), [plate_names.py](engine/reference/plate_names.py), [test_cm.py](engine/reference/test_cm.py), [vectors.json](engine/reference/vectors.json) | the reference engine (standard library only), its tests and the conformance vectors every implementation must reproduce |
| [engine/data/register.json](engine/data/register.json), [units.json](engine/data/units.json) | what a decoder ships: arrondissements with their spot frames, every area with its plate and official names, name index, blocks and frame; the aliases; the outlines. [border.geojson](engine/data/border.geojson): the national border (OpenStreetMap, admin_level 2) simplified to about 50 m, which an issuer checks every new code against: none is issued more than 300 m outside it |
| [registry/](registry/) | the frozen area table `areas.csv.gz` (every area, its blocks and its count of compounds), one `<arrondissement>.csv.gz` with every code of each arrondissement, and `MANIFEST.json` (the counts and the SHA-256 of each file uncompressed) |
| [server/](server/README.md) | the registry server: import, JSON API, issuing by the issuer's rules, export, Docker; its OpenAPI contract ([openapi.yaml](server/openapi.yaml)) and the API reference with real responses ([docs/api.md](docs/api.md)) |
| [model/](model/) | `areas/` (the code areas, the national name ranges, renames), `units/` (arrondissement outlines, spot frames), `zones.json`, `stats/` (`register.json`, `building-stats.json`, `name-stats.json`, `evaluation.json`: the figures and measured properties of the paper), `design.json` |
| [tools/](tools/) | the scripts that built the inputs, the areas, the compounds, the names and the registry ([tools/README.md](tools/README.md)) |
| [GOVERNANCE.md](GOVERNANCE.md), [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) | who decides what, the one-issuer rule, how to propose a change, how to report a problem |
| [SOURCES.md](SOURCES.md), [LICENSING.md](LICENSING.md), [NOTICE](NOTICE), [CITATION.cff](CITATION.cff) | sources, licences, how to credit and how to cite |

## Run the reference engine

```sh
cd engine/reference
python3 test_cm.py                                   # tests
python3 cm_engine.py resolve Bonapriso 14 01         # remembered form: one area in the whole country
python3 cm_engine.py resolve Adjap 48 50
python3 cm_engine.py verify CM-DLA1-015-1401-6       # validate a machine code
python3 cm_engine.py spot 4.0243022 9.6904852        # spot code: CM-DLA1 E0449 N0268
python3 cm_engine.py unspot "CM-DLA1 E0449 N0268"
```

Python 3.9 or newer, no packages (see [requirements.txt](requirements.txt)).

## Run the server

```sh
cd server && docker compose up -d                     # imports the registry on first start, then serves :8080
curl -s 'http://localhost:8080/v1/find?q=Bonapriso%2014%2001'
```

Or without Docker, from the repository root:

```sh
python3 -m server import --registry registry --db data/addresses.sqlite
python3 -m server serve --db data/addresses.sqlite --port 8080
python3 -m unittest discover -s server/tests -t .     # the server's tests
```

A deployment is read-only unless the State of Cameroon or N-WAYS LIMITED has designated it as the issuer: codes come from one issuer only ([server/README.md](server/README.md), "One issuer"). Every endpoint, with real requests and responses: [docs/api.md](docs/api.md).

## Build the paper

```sh
python3 tools/paper-figures.py   # figure data (docs/figures/*.dat) and model/stats/evaluation.json, from registry/
sh docs/paper/build.sh           # pandoc 3, tectonic and pdftocairo; writes docs/n-ways-addressing-cameroon-en.pdf and -fr.pdf
```

## How the registry was made

```sh
python3 tools/prepare-inputs.py <work>              # enclosures, estates, gates, places, arrondissements, the two cities' streets
python3 tools/build-areas.py <work> <CM.txt>        # the code areas, from OpenStreetMap and GeoNames
python3 tools/extract-buildings.py <work>           # every footprint inside Cameroon (DuckDB, 3 GB cap), with its arrondissement and street
python3 tools/assign-areas.py <work>                # each footprint's code area and every area's frame
python3 tools/sort-buildings.py <work>              # sorted by area
python3 tools/issue_registry.py group <work>        # compounds and profiles, one area at a time
python3 tools/build-register.py <work> --freeze     # plate names, national ranges and blocks on the real compounds
python3 tools/issue_registry.py number <work> <work>/lotes.jsonl.gz
python3 tools/vectors.py                            # engine/reference/vectors.json
python3 tools/paper-stats.py <work> <work>/lotes.jsonl.gz
```

The N-Ways issuer then issues the codes, checking every number against the reference's, and exports `registry/`. The register is frozen since first issue: a new run adds codes for new compounds and never renumbers an issued one.

## Licence and credit

Code (engine, server, tools): Apache License 2.0, with [NOTICE](NOTICE). Data (registry, model, engine data): ODbL 1.0. Documents: CC BY 4.0. Credit every use: **"N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)"**, with a link to this repository ([LICENSING.md](LICENSING.md)). Derived from OpenStreetMap (© OpenStreetMap contributors, ODbL), GeoNames (CC BY 4.0), Google Open Buildings (CC BY 4.0) and Microsoft building footprints (ODbL).
