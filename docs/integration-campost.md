# Using Cameroon's official addresses first / Intégrer d'abord les adresses officielles

How the State's, the councils' and Campost's addresses take precedence over N-Ways codes, and how they are imported when they are shared or published.

## The rule

**Every compound has an N-Ways code, and the official address comes first wherever one exists.** A rule that issued no N-Ways code where an official address exists was considered and set aside: official coverage is a few streets of two cities, households sharing one gate could not be told apart, and a compound would change identifier the day its council numbered it. A code beside the official address avoids all three.

1. **Wherever an official address exists, it is shown first, exactly as officially written**: in French or English as published, with the same spelling, numbers and punctuation. The government's data is imported, never edited.
2. **Every compound also has its N-Ways code** (issued 21 October 2026), to say on the phone and to tell apart the households of a compound that share one gate.
3. **When an official address later appears for a door, it becomes the primary address** shown on the card; the N-Ways code stays beside it and never changes, so plates and shared links keep working.
4. **A P.O. box (BP) is not an address.** It is stored as a mailbox of a person or organisation, never as the address of a place.

On current evidence, official addresses cover a small part of Douala and Yaoundé and an unknown number of Campost PLP holders. **Most of Cameroon (most compounds in every region) has nothing official**, so N-Ways codes are needed there.

## Official sources, by priority

| # | Source | What it gives | Where the data is | Terms | Coverage known? |
|---|---|---|---|---|---|
| 1 | **Campost–FindMe** (state postal operator + its digital-addressing partner, since Nov 2024) | Commune postal codes ("created … covering the entire national territory"); certified addresses, the Plan de Localisation Postale (PLP, 2,000 FCFA); FindMe address = occupancy number, street name, postal code, city | Campost head office (Yaoundé); FindMe app and back end; no public download found | Unknown; to negotiate | No list, format or example published |
| 2 | **Communauté urbaine de Douala (CUD)**: metric door numbering since 1992, numbered zones, street names | Street name + metric door number (even right, odd left) + zone | CUD technical services (Direction des études / urbanisme); no open register found | Unknown | Under 15% of roads named (2019) |
| 3 | **Communauté urbaine de Yaoundé (CUY, Mairie de la Ville)**: numbered streets | "Rue 1794", "No 1232" | CUY technical services; partly in OSM (`addr:street` "Rue 1.055") | Unknown; OSM part is ODbL | Partial; about 5,100 streets planned, few doors numbered |
| 4 | Other communautés urbaines and councils | Any street names and numbers they have produced | Council technical services | Unknown | Unknown; to survey |
| 5 | OpenStreetMap `addr:*` | Mapper-entered street names and numbers, copied from plates | OSM (ODbL) | ODbL, attribution | Sparse |

## Integration plan for Campost–FindMe

1. **Ask Campost** (Direction générale, the postal-services department) and FindMe in writing, through N-Ways partnerships, for:
   - the **commune postal-code list and format** (code ↔ commune, plus any sub-commune level);
   - the **PLP format** and any register or API of certified addresses, with geometry (point, entrance or plot);
   - the **terms of reuse**: display, storage, redistribution in an open registry, attribution;
   - how a PLP is **updated** (moves, splits, demolitions).
2. **Import** (when the terms allow):
   - commune codes go to `model/zones.json → campostCode`. Zones are arrondissements = communes, so each zone gets exactly one code, or the list of codes if Campost uses sub-commune codes;
   - PLP or FindMe addresses go to each compound's `official` block (see `design.json → precedence`), keyed to the compound whose plot or entrance holds the PLP point. The PLP point is checked against the compound's gate (within 15 m) before linking.
3. **Display exactly as published.**
   - The app shows the PLP or FindMe address and the Campost postal code verbatim, in the language Campost published it in, as the **first line**.
   - The N-Ways code shows below it as "N-Ways: …", or not at all if the household prefers.
4. **Coverage detection.** Coverage is tracked per zone: share of compounds with a PLP, share of entrances with a municipal number. It is published in `model/stats/official-coverage.json` once data arrives.
   - Where compounds are covered officially, the official address is first on every card; their N-Ways codes stay beside it and never change.
5. **If Campost–FindMe turns out to be working and national** (published codes, addresses available for most compounds, reusable terms):
   - the N-Ways app imports and shows Campost addresses first everywhere;
   - "Add my home" also points people to getting a PLP;
   - the N-Ways codes stay as the short spoken form beside the official address; no code is ever withdrawn or reused.
6. **Until then**, every compound keeps its N-Ways code, with reserved `campostPLP` and `findMeAddress` fields that the official address fills when it appears (it is then shown first).

## Douala and Yaoundé municipal addresses

- **Ask** the CUD and CUY technical services for their street registers: names, numbering zones, start points and directions of metric numbering, and any door register. Ask also for terms.
- **Import**:
  - streets go to the N-Ways street layer, with the official name exactly as written ("Rue 1.055", "Boulevard du Président Ahmadou Ahidjo");
  - door numbers go to the entrance of the matching compound (`official.street`, `official.number`, `official.source: CUD | CUY`).
  - Where only the street and its numbering rule are known, the engine can *compute* the expected metric number at a gate (distance from the street start, side), but it shows it **only as "expected"** until a plate or the council confirms it.
- **Coverage detection**: a compound counts as covered when its main entrance has an official number from the council, from OSM `addr:housenumber` tagged from a plate, or from a photo of the plate confirmed by two people.

## Registry precedence (summary)

| Situation | Shown first | N-Ways code |
|---|---|---|
| Official address for the door (PLP, FindMe, CUD/CUY number) | The official address, verbatim | Issued, shown beside it |
| Official area code only (Campost commune code), no door address | N-Ways home code, with the Campost code beside it | Issued, nested in the commune code |
| Nothing official | N-Ways home code | Issued |
| P.O. box only | N-Ways home code; the BP stays a mailbox | Issued |

## What N-Ways will not do

- Present an N-Ways code as a Campost code or an official address.
- Redistribute Campost or council data beyond what their terms allow.
- Charge households for an address. The Campost PLP fee is Campost's.
