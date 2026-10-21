# Licensing

N-Ways Addressing for Cameroon is open. Build on it, and credit N-Ways.

| Part | Licence | File |
|---|---|---|
| Code: the engine, the registry server and the tools (`engine/reference/`, its test vectors, `server/`, `tools/`) | Apache License 2.0 | [LICENSE](LICENSE), [NOTICE](NOTICE) |
| Data: the registry, the areas, the arrondissement outlines and the model (`registry/`, `model/`, `engine/data/`, `server/testdata/`) | Open Database License (ODbL) 1.0 | [LICENSE-DATA](LICENSE-DATA) |
| Documents: the model, the research papers, the API reference and the verification of existing systems (`docs/`), and this repository's other Markdown files | Creative Commons Attribution 4.0 (CC BY 4.0) | [LICENSE-DOCS](LICENSE-DOCS) |

Licensor: **N-WAYS LIMITED** (nways.ng). Source: https://github.com/n-ways/open-addresses-cameroon

## How to credit N-Ways

Copy the line that fits. Link it to https://github.com/n-ways/open-addresses-cameroon where you can.

**An app, a website or an API that shows, decodes or issues these addresses:**

> Codes by N-Ways Addressing · © N-WAYS LIMITED (nways.ng)

Put it next to the address, or on the screen that shows it, and in your about or licences screen. If you ship or change the engine, also keep [NOTICE](NOTICE) (Apache 2.0, section 4(d)).

**A map, a dataset or a database built from the data:**

> © N-WAYS LIMITED, N-Ways Addressing; contains OpenStreetMap data © OpenStreetMap contributors (ODbL) and the other sources in SOURCES.md

A database you make from it and share is shared under ODbL 1.0 too (share-alike). A map image or a printed plate made from it is a "produced work": it carries the line above, and needs no share-alike.

**A paper, an article, a slide or a translation that uses the documents:**

> N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng), CC BY 4.0. https://github.com/n-ways/open-addresses-cameroon

Say what you changed, if you changed anything.

## Sources inside the data

The data is built from open sources (full list in [SOURCES.md](SOURCES.md)). Their own terms travel with it, and the data credit above names them:

| Source | Licence | What you owe it |
|---|---|---|
| OpenStreetMap (buildings, places, gates and enclosures derived from it) | ODbL 1.0 | "© OpenStreetMap contributors"; share-alike, which is why the data is ODbL |
| Microsoft building footprints, via Overture Maps | ODbL 1.0 | credit Microsoft and the Overture Maps Foundation |
| Google Open Buildings, via Overture Maps | CC BY 4.0 | credit Google and the Overture Maps Foundation; compatible with redistribution inside an ODbL database |
| OpenStreetMap: the 360 arrondissements, Yaoundé's and Douala's named and coded streets and the place nodes the code areas are named after | ODbL 1.0 | "© OpenStreetMap contributors" |
| GeoNames populated places (CM), the other seeds of the code areas | CC BY 4.0 | "contains GeoNames data (geonames.org), CC BY 4.0" |
| N-Ways places (used only to classify buildings: OSM, Overture, Foursquare OS Places, All The Places) | per source (ODbL, CDLA-Permissive-2.0, Apache-2.0, CC0) | only categories are used, no place records are redistributed |

**Postcodes.** Cameroon has no published postcode yet. Campost announced commune postal codes with FindMe in November 2024 but has published no list or format; each zone keeps a reserved field for its code, and no Campost data is in this repository.

**Official addresses.** Where Yaoundé's or Douala's council has named or coded a street, a compound on it shows the street first, and a door number of the councils' numbering, once known for a gate, replaces it (engine/SPEC.md §6.0). A Campost PLP or FindMe certified address, once provided, comes first too. The State's data keeps its own terms and is not redistributed here. Both licences above let the State relicense or republish the registry if it adopts it.

**What is published.** The registry lists every issued code of every arrondissement, with its entrance point and building profile; nothing is held back. The area table flags (`alert_zone`) the regions the UK FCDO advises against travelling to (North-West, South-West, Far North, North, Adamawa and East), as context for relief and emergency planning.

**Personal data.** The registry holds places, never people (docs/paper.md, Privacy).

## Trademarks

"N-Ways" and the N-Ways logo are trade marks of N-WAYS LIMITED. The licences above cover the code, data and documents, not the marks: you may say your product uses N-Ways Addressing, but not that it is N-Ways or is endorsed by N-Ways.
