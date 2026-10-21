# Tools: Cameroon's registry

All inputs are read-only: the N-Ways data folder (`NWAYS_ROOT`), the N-Ways database (`NWAYS_DB`, tables `regions` and `places`) and the GeoNames dump `CM.txt` (https://download.geonames.org/export/dump/, CC BY 4.0). Run one heavy step at a time: DuckDB runs with `memory_limit='3GB'` and spills to the work folder; the grouping and the numbering read the footprints one code area at a time.

| Step | Script | Writes |
|---|---|---|
| 1 | osmium exports (below) | `admin`, `bar`, `place`, `hw` `.geojsonseq` in the work folder |
| 2 | `prepare-inputs.py <work>` | `units.geojson` (the 360 arrondissements, OpenStreetMap), `streets.csv` (the named streets of Yaoundé and Douala, with Yaoundé's street codes), `enclosures.geojson`, `estates.geojson`, `gates.csv`, `places.csv`, `country.geojson` (the national border: OpenStreetMap's admin_level 2 relation of Cameroon from the extract, else the database's copy of it, table `countries`) |
| 2b | `build-border.py <work>` | `engine/data/border.geojson`: the border simplified to 50 m (Douglas-Peucker, local metres), with `errorM`, the largest distance of an OpenStreetMap vertex from the simplified line, for the server and `issue_registry.py number` |
| 3 | `build-areas.py <work> <CM.txt>` | `model/areas/register.json`: the 24,213 code areas, from OpenStreetMap places and GeoNames populated places |
| 4 | `extract-buildings.py <work>` | `buildings-raw.csv` (every footprint whose centre lies inside the national border, with its enclosure, estate, zone and nearest official street within 30 m; specks under 1 m² dropped), `buildings-pts.csv`, `enclosure-gates.csv` |
| 5 | `assign-areas.py <work>` | `area-of.csv` (each footprint's code area: the nearest named place of its zone), `area-boxes.json` (each area's frame) |
| 6 | `sort-buildings.py <work>` | `buildings.csv`, sorted by area |
| 7 | `issue_registry.py group <work>` | `compounds.jsonl.gz` (compounds and profiles; city rules in Yaoundé and Douala, huts clustered elsewhere), `area-counts.json`, `group-stats.json` |
| 8 | `build-register.py <work> --freeze` | `area-compounds.py` and `name-ranges.py` on the real compounds: plate names, national ranges and blocks; `model/areas/name-ranges.json`, `engine/data/register.json`, `engine/data/units.json`, `model/stats/register.json` |
| 9 | `issue_registry.py number <work> <work>/lotes.jsonl.gz` | the issue batches (one line per compound), area by area, with the reference's numbers and the official street; a compound more than 300 m outside the border is dropped before numbering (counted as `abroad`, which should be 0) |
| 10 | the N-Ways backend: `homecodes issue -country CM -lotes <work>/lotes.jsonl.gz`, then `homecodes export -country CM -out <dir>` | the codes, after checking every number against the reference's; the registry, every code of every arrondissement, gzipped into `registry/` |
| 11 | `vectors.py`, `paper-stats.py <work> <work>/lotes.jsonl.gz` | `engine/reference/vectors.json`, `model/stats/building-stats.json` |
| 12 | `paper-figures.py` (reads `registry/` only) | the paper's figure data `docs/figures/*.dat` and `model/stats/evaluation.json` (uniqueness, digits, check digits, decoding, spot error, locality, the per-area alternative) |

**The border decides** ([SPEC §6.1](../engine/SPEC.md#61-inputs)). A code is only ever issued for a compound whose entrance lies inside Cameroon's national border (OpenStreetMap, admin_level 2) or within 300 m of it. The zone outlines may spill over the border and never decide: step 4 drops every footprint whose centre lies outside the border, step 9 drops every compound more than 300 m outside it, and the N-Ways issuer refuses a batch that holds one. `check-border.py [registry/]` counts the codes of a registry more than 300 m outside the border (exit 1 if any); on the published registry it finds none.

**After first issue** the register is frozen: never run `build-register.py --freeze` again. An area is renamed only through `model/areas/renames.json` and `rename-areas.py`, which appends new name ids, leaves every other name alone and prints each moved block (old start, new start) for the database. A spelling (accents, hyphens, script) is settled through `respell.py <a copy run with the current rules>`, which changes how plates are written and nothing else: re-freezing would renumber the name ids, and with them every check digit.

The exploratory statistics scripts (`stage.py`, `analyze.py`, `areas.py`, `export-areas.py`) measured zone and building profiles while the model was designed, and reproduce the design figures in `model/design.json`; `build-zones.py` built `model/zones.json` and `model/units/zones.geojson`.

### osmium exports

```
P=data/osm/cameroon-latest.osm.pbf
osmium tags-filter -o b.osm.pbf $P r/boundary=administrative
osmium export -a type,id -f geojsonseq --geometry-types=polygon -o admin.geojsonseq b.osm.pbf
osmium tags-filter -o bar.osm.pbf $P w/barrier=wall,fence,hedge,retaining_wall n/barrier=gate,entrance,lift_gate,sliding_gate,swing_gate n/entrance
osmium export -a type,id -f geojsonseq -o bar.geojsonseq bar.osm.pbf
osmium tags-filter -o place.osm.pbf $P n/place w/place r/place
osmium export -a type,id -f geojsonseq -o place.geojsonseq place.osm.pbf
osmium tags-filter -o hw.osm.pbf $P w/highway
osmium export -a type,id -f geojsonseq -o hw.geojsonseq hw.osm.pbf
```
