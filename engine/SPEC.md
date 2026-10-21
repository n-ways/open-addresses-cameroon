# N-Ways address engine for Cameroon — specification / Spécification du moteur N-Ways Cameroun

One code for every compound in Cameroon, frozen in `engine/data/register.json` at first issue and published in `registry/`.
Reference implementation: [`reference/cm_engine.py`](reference/cm_engine.py) (Python standard library only). Tests: [`reference/test_cm.py`](reference/test_cm.py); conformance vectors from the frozen register: [`reference/vectors.json`](reference/vectors.json) (`tools/vectors.py`).

"MUST", "SHOULD", "MAY" as in RFC 2119. A ready-made server that serves the registry and issues codes by these rules is in [`../server/`](../server/README.md).

## 1. Objects

| Object | What it is | Identifier |
|---|---|---|
| Zone | one of the 360 arrondissements, the territory of one commune (OpenStreetMap boundaries, `model/units/zones.geojson`) | 4-character key (`YDE6`, `DLA5`, `BDA1`) and a frozen index 0–359 (`model/zones.json`) |
| Code area | a named place of a zone: quarter, village, hamlet, locality (OpenStreetMap and GeoNames names, `tools/build-areas.py`); a home takes the nearest one of its zone | area index `001`–`999` within its zone |
| Plate name | the short name of a code area used in the code (≤ 12 characters, ≤ 2 words, no digit, §2.5); the official name is kept beside it | area |
| Name range | the national number range of one normalised plate name, cut into one frozen block per area (§2.4) | name key + frozen name id (5 digits) |
| Compound | concession / parcelle / compound, walled or not, with a primary gate | area + number |
| Structure | one footprint inside a compound | compound + `.n` |
| Entrance | a gate or door of a compound; `/1` is the primary gate | compound + `/n` |
| Spot | any point, 10 m cell of the zone frame | zone + `E…` `N…` |

## 2. Forms

### 2.1 Machine form

```
CM-<zone>-<area>-<number>-<check>
zone   : the zone key, 3 letters and a letter or digit (model/zones.json)
area   : the area index in its zone, 3 digits
number : 3, 4 or 5 digits, first digit 1-9; length fixed per name
check  : Damm check digit over nameId(5 digits) + zoneIndex(3 digits) + area + number
regex  : ^CM-([A-Z]{3}[A-Z0-9])-(\d{3})-([1-9]\d{2,4})-(\d)$
```

Parsers MUST accept the form without the check digit (then report it unchecked), MUST treat a wrong check digit as invalid, and MUST treat a code whose number lies in none of that area's blocks (§2.4) as invalid.

### 2.2 Remembered form

- `<plate name> <number grouped>`, e.g. `Etetak 23 67`.
- Implementations MUST NOT produce a remembered form whose plate name breaks the plate limit (§2.5), except a provisional name the commune may still shorten.
- Grouping: 4 digits `AB CD`; 5 digits `AB CDE`; 3 digits `ABC`.
- No letters to learn. No check digit is ever shown to people or asked of them: a digit people cannot check for themselves only adds a place to make mistakes. A decoder accepts one after a hyphen from systems that send it and verifies it.

Resolving a remembered form uses **no context**: not the user's position, not the zone of the phone, not a town said after a comma. Implementations MUST NOT complete a code from context.

`<name> <number>` → name key (§2.4) → the plate name's range, or, if the key is an alias (an official name, §2.5), the plate name it maps to; a number of the wrong length MUST be refused → the block that holds the number → (zone, area) → machine form. A number in no block (spare or free space) MUST be refused as not issued. One remembered form maps to exactly one machine form in the whole country. Reference: `resolve_remembered`.

### 2.3 Spoken form

French or English by the person's language, digits in groups from the left as phone numbers are read: 23 67 → "vingt-trois soixante-sept" / "twenty-three sixty-seven"; 48 217 → "quarante-huit deux cent dix-sept" / "forty-eight two seventeen".

### 2.4 National name ranges

**Name key** (`name_key`): NFKD, combining marks removed, upper case; `ST`/`ST.` and `STE` as whole words expanded to `SAINT`/`SAINTE`; leading `Q`, `QUARTIER`, `QUARTER`, `HAMEAU`, `VILLAGE DE`, `VILLAGE` followed by a space, hyphen or dot removed; leading `LES `, `LE `, `LA `, `THE `, `L'` removed; every character outside A–Z, 0–9 removed; then, in this order, `TCH→C`, `CH→C`, `DJ→J`, `GH→G`, `PH→F`, `CK→K`, `OU→U`, `W→U`, `GU→G` before I or E; runs of one letter collapsed to one (digits are never collapsed). So Ngoa-Ekellé = Ngoa Ekele, Douala = Duala, Djoungolo = Joungolo, Tchinga = Chinga.

**Generic labels** (`is_generic`: exactly *village*, *quarter*, *campement*, *camp*, *site*, *ferme*, *farm*, *chantier*, *zone*) are not names and MUST NOT receive a block.

**Blocks.** For every plate-name key, the areas carrying it (at first issue, ordered by zone then index) each get a block of `max(20, ceil(2 × compounds / 10) × 10)` numbers, laid end to end from `10^(d−1)`. `d` is the smallest of 3, 4, 5 with `Σ blocks ≤ floor(0.9 × 9 × 10^(d−1))` (`NAME_SPARE = 0.1`). No number has more than 5 digits. Areas with no compound yet get no block until their first compound. The name id is the 1-based rank of the key in the sorted list at first issue, then append-only. Published in `model/areas/name-ranges.json`; built by `tools/name-ranges.py`.

**Too large.** An area whose own block exceeds `0.9 × 90,000` MUST be split by named quarters before issue. If the blocks of one name together exceed 5 digits, the name keeps its bare form for the blocks that fit in register order and every other area takes the qualified name `<name>-<zone town>`, decided once and listed (`qualified` in `model/stats/name-stats.json`).

**Frozen.** Blocks are frozen at issue and never renumbered. A new area with an existing name, or a full block, takes the next block from `spareFrom` upward (`spare_block`). After first issue an area is renamed only through `model/areas/renames.json` and `tools/rename-areas.py` (new name ids appended, every other name untouched, the old numbers retired); `tools/build-register.py --freeze` is for first issue only.

### 2.5 Plate names

Every code area has an **official name** (shown in small print, never required) and a **plate name** (in the code). A plate name MUST have at most 12 characters (NFC; every letter, space, hyphen and apostrophe counts one), at most 2 words (not counting linking words: French `de du des d la le les l et sur en au aux à`, English `of the and on at`) and no digit. Rules: French in French-speaking zones, English in the North-West and South-West (`model/zones.json` `language`). Reference: `plate_names.fits`.

Derivation (`plate_names.derive`, Cameroon lists in `tools/name-ranges.py`): documented short form with a source; else clean (brackets, after a slash, generic words `Q`, `Quartier`, `Quarter`, `Lieu-dit`, `Village de`, `Cité`, `Lotissement`, `Zone`, `Secteur`, `Hameau`); if it fits, done; else `Saint` → `St`; else the most distinctive run of whole words that fits, never a word cut, never only weak words (Peulh, Foulbé, Haoussa, Bororo, Arabe Choa, Nouveau, Village, New, Old, Chefferie, Carrefour, Mission...). The area is flagged `needsCouncilChoice` (≤ 3 `plateCandidates`, first one provisional) when there is no clear best candidate, the short form drops a qualifier or a number, it equals a big city elsewhere, another place of the same zone has it, or a hyphenated name is too long. **The zone's name instead** (provisionally): when the short form would hold a digit, be a bare generic word, be a derived form of under 3 letters, or be a big city's name elsewhere. Codes are issued under the provisional name, so no household waits for the choice; the commune may choose once, and the old name stays an alias.

Aliases: an official name whose key differs from its plate name's key decodes to that plate name when it maps to one plate name only; an alias claimed by two plate names, or equal to another plate name, is dropped and listed (`droppedAliases`).

## 3. Check digit: Damm

The Damm table (order-10 weakly totally anti-symmetric quasigroup) is in `cm_engine.DAMM`. `check = fold(DAMM, 0, digits)`. The digits start with the frozen 5-digit name id, then the zone's frozen 3-digit index, so the check binds name, zone, area and number. It detects every single-digit error and every transposition of two adjacent different digits. It lives in the machine form only.

## 4. Zones and frames

- Zone lookup: point-in-polygon (even–odd rule) over `model/units/zones.geojson`; near a boundary the registry decides, not the polygon. A point in no outline takes the zone of its spot code (§5); a point is in Cameroon when an outline holds it or §5 gives it a zone.
- Frame (one per zone, frozen in `model/units/frames.json`): `lon0 = floor(minLon × 100) / 100`, `lat0 = floor(minLat × 100) / 100`, `latc = round((minLat + maxLat) / 2, 2)`, `kx = 111320 × cos(latc)` m per degree of longitude, `ky = 110574` m per degree of latitude; digits per axis = 4 if the frame spans less than 99,990 m on that axis, else 5.

## 5. Spot codes

```
encode(lat, lon): E = floor((lon − lon0) × kx / 10), N = floor((lat − lat0) × ky / 10)
                  → "CM-<zone> E<E padded> N<N padded>"
decode:           lon = lon0 + (E + 0.5) × 10 / kx, lat = lat0 + (N + 0.5) × 10 / ky   (cell centre)
```

The zone of a point for the spot grid is the zone whose outline holds it (§4). The outlines are generalised, so a few points in Cameroon lie in no outline: in slivers between arrondissements, just over an outline at the shoreline or the national border, and at sea. Such a point takes its zone as follows, so that every issued compound has a spot code:

1. Candidates are the zones whose outline lies within 12 km of the point (`SPOT_OUTLINE_M`), the farthest issued compound in no outline being 10.9 km from one. A point farther from every outline is outside Cameroon.
2. Among the candidates whose frame holds the point (0 ≤ E < 10^dx and 0 ≤ N < 10^dy), the zone with the nearest outline: the least distance from the point to an edge of any ring of the zone's outline, with longitude differences multiplied by cos(latitude of the point) (`cm_engine.edge_d2`). Ties go to the lower zone key.
3. If no candidate's frame holds the point, the candidate with the nearest outline among those whose frame the point lies at most 500 cells (5,000 m) beyond on each axis (E and N each between −500 and 10^d + 499, `SPOT_NEAR_CELLS`), ties to the lower key; the point takes that frame's nearest cell (E and N clamped to 0 … 10^d − 1). One issued compound needs this step, an industrial structure at sea 10.9 km off Kribi and 4.49 km beyond the frame of Kribi I; the registry keeps its exact entrance point.
4. Otherwise the point MUST be refused.

Frames never move and never gain digits, because either would change spot codes already published. Decoding needs no lookup: a spot code names its zone, and its cell centre is decoded in that zone's frame. Example: Marché Central, Yaoundé (3.866511 N, 11.517935 E) → `CM-YDE1 E0532 N0071`; a compound of Yoyo Bar (Yaoundé II) in a sliver between outlines (3.8751747 N, 11.4844409 E) takes the nearest outline, Yaoundé VII's, 5.6 m away → `CM-YDE7 E0826 N0499`.

## 6. Official addresses first, then registry generation

### 6.0 Official addresses

Where the government or a council gives an address, it is shown first, exactly as written, and every compound keeps its N-Ways code beside it:

- Yaoundé and Douala: the named street within 30 m of the compound (OpenStreetMap names and Yaoundé's street codes, `Rue 1.055, Yaoundé`, `coverage = official-street`); a door number from the councils' numbering, once shared or confirmed by residents, replaces it.
- Campost: a PLP or FindMe certified address, once Campost publishes its format or a resident provides theirs; Campost's commune postal code, once published, sits beside every address of its zone (`model/zones.json` `campostCode`).
- Official changes always win; N-Ways reports suspected errors to the holder and never edits official records.

### 6.1 Inputs

OpenStreetMap buildings (ODbL) and the Google Open Buildings / Microsoft footprints that no OpenStreetMap building overlaps (via Overture Maps; CC BY 4.0 / ODbL); OSM walls, fences, hedges, gates and entrances; N-Ways gated compounds and gates; N-Ways places.

**The border decides.** A code MUST only be issued for a compound whose entrance lies inside Cameroon's national border (OpenStreetMap, the admin_level 2 boundary) or within 300 m of it (`cm_border.BORDER_M`). Zone outlines from other sources may spill over the border; they never decide. The build drops every footprint whose centre lies outside the border (`tools/extract-buildings.py`) and, before numbering, every compound more than 300 m outside it (`tools/issue_registry.py number`). An issuer refuses a new code, or an entrance moved, more than 300 m outside the border, even where the spot-code rule (§5) gives the point a zone. `engine/data/border.geojson` is the border simplified to about 50 m, with `errorM`, the largest distance between the simplified line and OpenStreetMap's; a point more than `300 − errorM` m outside the simplified border is refused, so that no point more than 300 m outside the true border is accepted (`cm_border.Border.abroad`). Reference: `engine/reference/cm_border.py`; check a registry with `tools/check-border.py`.

### 6.2 Group structures into compounds (before any numbering)

`cm_engine.group_footprints`, one code area at a time, footprints in stable-id order, true outline gaps:

1. **enclosure** (0.85): structures whose centre lies in the same smallest closed barrier polygon of ≤ 6,000 m².
2. **annex** (0.60): a structure < 25 m² joins the nearest structure ≥ 25 m² within 8 m.
3. **hut cluster** (0.50; not in Yaoundé and Douala): huts < 40 m² that belong to no house, with gaps ≤ 3 m, at most 25 per compound: a cluster never joins two houses.
4. **single** (0.40).

### 6.3 Code areas

Each footprint is assigned to the nearest named place of its zone (local metres, ties to the lower index; `tools/assign-areas.py`). Area indices are alphabetical at first issue, then append-only. The area's frame is the box of its footprints' centres widened by 0.0005° on every side, frozen.

### 6.4 Numbers

```
range    = the area's block [lo, hi] in its name's national range (§2.4)
main     = first two thirds of the block; tail reserve = last third
order    = compounds sorted by Hilbert index (order 16) of their ordering point in the area's frame, ties by id
step     = max(1, floor(|main| / floor(N × 1.5)))
number_i = lo + i × step
```

### 6.5 New compound (provisional number)

**Area.** A new compound takes the area of the nearest issued code within 250 m, so a new house joins its neighbours; else the code area of its point (§6.3); else the nearest area that gives numbers. Another door of an issued compound takes that compound's area and lies within 80 m of its entrance.

**Number.** The free number strictly between the new point's curve neighbours closest to their midpoint, below the tail reserve (the lower one on a tie); if none, the lowest free number of the tail reserve; if none, the lowest free number of the area's later blocks; if none, an extension block of `max(20, ceil(2 × (N + 1) / 10) × 10)` numbers from the name's spare, above every block already given (`spare_block`). Every number ever issued in the area counts as taken, retired ones included.

**One issuer.** Numbers MUST be issued by one issuer for the country: two issuers working from the same registry would give the same free number to two compounds.

## 7. Stability

A number is never reused or moved. Demolished: retired. Split: the part with the larger floor area keeps the code. Merge: the oldest code survives, the other stays an alias. Renames change only the alias table or follow §2.4 "Frozen".

## 8. Profiles

Every structure carries a use class with its confidence and source, footprint, perimeter, floors (OpenStreetMap `building:levels`, else `height` / 3; the Google/Microsoft height is a rendering filler and never gives floors) and a status. A home never carries a name.

## 9. Confirmation

Arrivals at the gate, residents' answers ("these buildings are one home", "this is the gate"), businesses claiming their shop and partners' cross-references confirm a grouping, a gate or a provisional code without anyone queuing it for review.

## 10. Privacy and safety

Published registry rows carry no person data: a code names a place, never who lives there. Every issued code is published, in every zone. The area table flags (`alert_zone`) the arrondissements of the North-West, South-West, Far North, North, Adamawa and East regions, to which the UK FCDO advised against all or all but essential travel (9 February 2026), so that relief and emergency services can plan around the advice.

## 11. Conformance

An implementation conforms when it reproduces every vector in `reference/vectors.json` (name keys, machine, remembered and written forms, decodings with and without check digits, refusals, spot codes (also of points in no outline: every issued compound among them, slivers, the sea, the frames' nearest cells and refusals), the Hilbert curve and the numbering of a real area with new homes).
