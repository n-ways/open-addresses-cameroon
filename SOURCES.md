# Sources

Accessed 17–21 October 2026.
- **Fetched**: the page was opened and read.
- **Search only**: seen in search results, not opened.
- **Downloaded**: the dataset was downloaded and processed.

## Postal and addressing

| # | Source | Status |
|---|---|---|
| 1 | UPU, addressing sheet Cameroon (FR), 07/2002: https://www.upu.int/UPU/media/upu/PostalEntitiesFiles/addressingUnit/cmrFr.pdf | Fetched |
| 2 | UPU, addressing sheet Cameroon (EN): https://www.upu.int/UPU/media/upu/PostalEntitiesFiles/addressingUnit/cmrEn.pdf | Fetched |
| 3 | WeAreTech Africa, "Campost s'associe à FindMe pour numériser l'adressage postal" (Nov 2024): https://www.wearetech.africa/en/fils-uk/news/tech/cameroun-campost-s-associe-a-findme-pour-numeriser-l-adressage-postal | Fetched |
| 4 | Ecomatin, Campost digital addressing: https://ecomatin.net/cameroun-confrontee-a-des-difficultes-operationnelles-campost-lance-un-systeme-dadressage-numerique | Fetched |
| 5 | Cameroon Tribune, article 67781 (PLP, 2,000 FCFA): https://cameroon-tribune.cm/article.html/67781/fr.html/details_2 | Fetched (free part) |
| 6 | Ecomatin, Finance Week 2025, CCA Bank–Campost–FindMe: https://ecomatin.net/finance-week-2025-cca-bank-campost-et-findme-sassocient-pour-optimiser-le-systeme-dadressage-au-cameroun | Search only |
| 7 | Campost homepage: https://campost.cm/ | Fetched |
| 8 | Wikidata, CAMPOST: https://www.wikidata.org/wiki/Q2935563 | Fetched |
| 9 | geopostcodes.com, Cameroon postal-code format | Search only |
| 10 | camer.be (articles 67504, 67511) and afrik.com, Douala addressing since 1992 | Search only (camer.be 404) |
| 11 | Cameroon Tribune, "Dénomination des rues : l'orientation des populations en question" (art. 29929, 2019) | Search only |
| 12 | United Nations Cameroon, contact page (Yaoundé "Rue 1794"): https://cameroon.un.org/fr/contact-us | Fetched |
| 13 | AFP via capitalfm.africa, "Streets with no names…" (Yaoundé, about 2016) | Search only |
| 14 | UN, E/CONF.105/9/CRP.9 (Commission nationale de toponymie, décret 68/DF/314) | Search only |
| 15 | Njoh, A. J. (2010), addressing in Cameroon, *Habitat International*: https://digitalcommons.usf.edu/geo_facpub/1966 | Search only |
| 16 | World Bank, Sustainable Cities and Land project, 30 May 2025: https://www.worldbank.org/en/news/press-release/2025/05/30/new-project-boosts-infrastructure-and-land-services-in-cameroon | Search only |
| 17 | OpenStreetMap node 4338286745 ("Rue 1.055", Yaoundé): https://www.openstreetmap.org/node/4338286745 | Fetched |

## Administration, law, mapping

| # | Source | Status |
|---|---|---|
| 18 | ISO 3166-2:CM: https://en.wikipedia.org/wiki/ISO_3166-2:CM | Fetched |
| 19 | Law no. 2019/024 of 24 Dec 2019, General Code of Regional and Local Authorities: https://leap.unep.org/en/countries/cm/national-legislation/loi-ndeg-2019024-du-24-decembre-2019-portant-code-general-des ; Cameroon Tribune arts. 29740, 35343, 37384; thevoicenews.net | Search only |
| 20 | Loi n° 2024/017 du 23 décembre 2024 (personal data): droitmediasfinance.com, cio-mag.com, digitalbusiness.africa; DLA Piper, *Data Protection Laws of the World: Cameroon* | Search only |
| 21 | INC, decree 92/049 of 24 Mar 1992; http://www.inc-cameroun.cm/ (no response) | Search only |
| 22 | UNGEGN 2025, Cameroon report: https://unstats.un.org/unsd/ungegn/sessions/4th_session_2025/documents/GEGN.2_2025_39_CRP39_item4b.pdf | Fetched |
| 23 | MINDCAF: https://fr.wikipedia.org/wiki/Ministère_des_Domaines,_du_Cadastre_et_des_Affaires_foncières | Fetched |
| 24 | EPSG:3119 Douala 1948 / AEF west: https://epsg.io/3119 ; EPSG:2215 Manoca 1962 / UTM 32N: https://epsg.io/2215 | Fetched |
| 25 | RGPH-4, Cameroon Tribune: https://www.cameroon-tribune.cm/article.html/80700/en.html/details_2 | Search only |
| 26 | Languages of Cameroon: https://en.wikipedia.org/wiki/Languages_of_Cameroon ; Echu, "The Language Question in Cameroon" | Search only |
| 27 | OSM wiki, GeoCameroun | Fetched |

## Plate names

Documented short forms of area names: none asserted yet (`docs/existing-systems.md`, "Short forms of area names"). Every short form in `model/areas/name-ranges.json` is derived by the rule in `engine/reference/plate_names.py` or flagged for the commune.

## Data used to build the registry and the statistics

| Data | Licence |
|---|---|
| OpenStreetMap: buildings, barriers, place nodes, administrative boundaries; Geofabrik extract `cameroon-latest.osm.pbf` of 17 Oct 2026 | ODbL 1.0, © OpenStreetMap contributors |
| Google Open Buildings and Microsoft footprints, via Overture (`data/detail/ml/CM.parquet`, with ML height `h`) | CC BY 4.0 / ODbL |
| N-Ways places: OSM, Overture, Foursquare OS Places, AllThePlaces, healthsites (`places` table) | Per source (`data/places/LICENCES.json`) |
| N-Ways gated compounds and gates (`data/valhalla/compounds.geojsonseq`, `gates.geojsonseq`) | Derived from OSM, ODbL |
| GeoNames populated places (`data/places/geonames/CM.txt`) | CC BY 4.0 |
| Open Location Code: https://github.com/google/open-location-code | Apache-2.0 |

## Further sources

| # | Source | Status |
|---|---|---|
| 40 | GeoNames, CM dump (populated places, feature class P), https://download.geonames.org/export/dump/ — 11,078 of the code areas are seeded from it (CC BY 4.0) | Downloaded |
| 41 | Overture Maps buildings release 2026-09-23.1: Google Open Buildings (CC BY 4.0) and Microsoft footprints (ODbL) that no OpenStreetMap building overlaps | Downloaded |
| 42 | UK FCDO, travel advice for Cameroon (9 February 2026): https://www.gov.uk/foreign-travel-advice/cameroon | Fetched |
| 43 | MTN Cameroon, emergency contacts (police 117, gendarmerie 113, fire 118, ambulance 119): https://mtn.com/emergency-contacts ; Government of Canada, Cameroon: https://travel.gc.ca/assistance/embassies-consulates/cameroon | Search only |
| 44 | Loi n° 2024/017 du 23 décembre 2024, APDP (art. 53); compliance by 23 June 2026: cio-mag.com, digitalbusiness.africa | Search only |

