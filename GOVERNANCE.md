# Governance / Gouvernance — N-Ways Addressing for Cameroon

Status: issued; the repository is public. This file sets out who decides what in this repository, how codes are issued and corrected, and how the whole can be handed to a Cameroonian authority.

## What these codes are

- They are **N-Ways addresses**, not official addresses or postcodes. This repository never calls them "official", "national" or "Campost" codes unless a Cameroonian authority adopts them in writing.
- **A code is an address, not a land title.** It is no evidence of ownership, occupation or boundaries. Only a titre foncier registered by MINDCAF is that.
- Every compound has a code. Where an official address exists, it is shown first, exactly as written, and the code sits beside it. Official addresses include:
  - Campost P.O. boxes;
  - Campost–FindMe commune postal codes and PLP certified addresses;
  - Douala's metric door numbers;
  - Yaoundé's numbered streets.

## Roles

| Role | Who | Decides |
|---|---|---|
| Maintainer | N-WAYS LIMITED, engineering | Engine, file formats, releases |
| Data steward | N-WAYS LIMITED, maps | Zones, area names, the registry, corrections |
| Privacy lead | N-WAYS LIMITED, privacy | What is published; requests to make a home private; APDP filings |
| Board | N-WAYS LIMITED | Partnerships, designation of an issuer, hand-over (licences: Apache 2.0, ODbL 1.0, CC BY 4.0, [LICENSING.md](LICENSING.md)) |

## One issuer

Codes are issued by **one issuer for the whole country**. Numbers come from blocks of one national range per plate name ([engine/SPEC.md](engine/SPEC.md) §2.4, §6.5): two issuers working from the same registry would each see the same free number for the next compound of an area and give it to two different homes, and nothing would reveal the clash until the two registries met.

The issuer today is N-WAYS LIMITED, through the N-Ways app and API. Anyone may run the registry server in [server/](server/) to answer look-ups; a deployment issues codes only when the State of Cameroon or N-WAYS LIMITED has designated it in writing as the issuer. Every other deployment runs read-only. When the State designates an office, N-Ways stops issuing for Cameroon on the day that office starts, from the registry as it stands that day ([server/README.md](server/README.md), "One issuer").

## Rules for changes

1. **Issued codes never change.** A change that moves, renumbers or reuses an issued code is rejected.
   - Merged compounds become aliases.
   - A split keeps the old code on one part and gives new numbers from the gap.
   - Demolished compounds are retired; a retired number is never given again.
2. **Zones and their indices are append-only.** If the State redraws an arrondissement, existing codes keep their zone. Only the place name shown beside the code changes.
3. **Area names** come from what people already say. They change only when the community asks, and the old name stays as an alias.
   The plate name in the code has at most 12 characters and 2 words, and no digit. Where the naming rule cannot choose one with confidence (`needsCouncilChoice`), codes are issued under a provisional name so that no household waits for a decision; the council may choose once, and the provisional name stays an alias. After issue an area is renamed only through `model/areas/renames.json` (`engine/SPEC.md` §2.4).
4. **Corrections settle by consensus**: confirmations from residents, arrivals and deliveries at the compound decide a gate, a merge or a retirement.
   - Corrections are applied automatically once the evidence threshold is reached; there is no manual review queue.
   - A dispute between neighbours over a gate or outline freezes that compound's outline until it is resolved. The code itself stays.
5. **Safety.** Every issued code is published, in every region. The travel advice of the UK FCDO for the North-West, South-West, Far North, North, Adamawa and East regions (9 February 2026) is recorded in the area table (`alert_zone`) so that emergency and relief services can plan around it.

## How to propose a change

See [CONTRIBUTING.md](CONTRIBUTING.md). Security and privacy problems go to hello@nways.ng ([SECURITY.md](SECURITY.md)).

## Partners

| Partner | Role |
|---|---|
| **Campost** (and FindMe, its digital-addressing partner) | National postal operator. Commune postal codes and PLP since November 2024. Their codes are stored and shown first; N-Ways does not compete with them. |
| **MINPOSTEL** and **ART** | Ministry and regulator for posts and telecommunications |
| **CUD** (Douala) and **CUY** (Yaoundé), then the other 12 communautés urbaines and the councils | Street naming and door numbering, area names, plates |
| **INC** (Institut National de Cartographie) | National mapping agency, base maps |
| **Commission nationale de toponymie** (décret 68/DF/314) | Spelling of place and area names |
| **MINDCAF** | Cadastre and titres fonciers (for plot outlines; a code is not a title) |
| **MINHDU** | Urban development |
| **NW and SW Regional Assemblies**, the House of Chiefs, the Public Independent Conciliators | Special status (Law 2019/024); English names; complaints |
| **APDP** (Loi 2024/017) | Data protection; authorisation for transfers abroad |
| **BUCREP** | Census (RGPH-4, 2026); locality names |
| Emergency services, couriers, banks, utilities | Users of the codes |

## Hand-over

The repository is built so that it can move to a Cameroonian body (Campost, INC or a city council) without forking the engine:
- the zone list, area names, registry, rules and the registry server are all in this repository;
- the maintainers' list and these rules transfer with it;
- the server's `export` writes the registry in its published format, so the designated issuer can start from the registry exactly as it stands on the day of transfer.

N-Ways would then keep a mirror, and the N-Ways app would follow the national body's decisions.
