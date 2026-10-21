# Cameroon: existing postal and address systems / Systèmes postaux et d'adressage existants

Checked 17–18 October 2026. **Fetched** means the page was opened and read on that date. **Search only** means it was seen in search results but not opened.

**Re-checked 21 October 2026,** before the first issue. Campost and FindMe have still published no list, format or example of the commune postal codes announced in November 2024; each zone keeps its reserved `campostCode`. No council has published open street or door data. Emergency numbers: police 117, sapeurs-pompiers 118, medical assistance (SAMU) 119 (Government of Canada travel advice, https://travel.gc.ca/destinations/cameroon, fetched 21 October 2026); gendarmerie 113 (MTN Cameroon emergency page, search only). Data protection: Loi n° 2024/017, in force since 23 June 2026, with the APDP as authority. The UK FCDO advises against all travel to the North-West, the South-West (outside Limbé), most of the Far North and the border bands with Nigeria, Chad and the Central African Republic, and against all but essential travel to the North and parts of the Far North and Adamawa (advice of 9 February 2026).

**Design consequences of this check:** every compound gets an N-Ways code, with the official address first wherever one exists; at most five digits follow the name; no check digit is ever shown to people. Point references use a 10 m numeric spot code (`engine/SPEC.md` §5).

## Verdict

**Postcodes: in name only, not in real use.**
- The UPU addressing sheet for Cameroon (dated 07/2002) has no postcode line. Its example is "BP 6000 YAOUNDÉ CAMEROUN".
- In November 2024 the press reported that the government had "created postal codes covering the entire national territory". These codes are assigned per commune and issued through the Campost–FindMe digital addressing app.
- No code list, format or single example of these codes has been published. Campost's homepage does not mention them. In practice, mail goes to a post-office box (BP).

**Street addresses: partial.**
- Douala (since 1992) and Yaoundé have street-naming and numbering programmes. Yaoundé uses numbered streets ("Rue 1794"). Douala uses metric door numbers.
- Coverage is thin. In 2019, under 15% of Douala's roads had a name.
- People still give directions by quartier and landmark ("Akwa, derrière l'immeuble X").
- We found no national address register and no national addressing law.

**Consequence for N-Ways.** The N-Ways Cameroon home code sits beside these systems and never competes with them:
- Each zone of the model is an arrondissement, which is the area of one commune. That is the level at which Campost says it assigns postal codes, so every zone has a reserved `campostCode` field.
- Every compound has reserved `campostPLP` and `findMeAddress` fields, to be filled when Campost publishes its format or a resident provides theirs.
- Municipal street names and door numbers are stored on the entrance they belong to.

## Postal: Campost and the UPU

| Finding | Source | Status |
|---|---|---|
| Example "Monsieur Pierre Marie / BP 6000 / YAOUNDÉ / CAMEROUN". No postcode line. Contact: Direction des postes. Sheet dated 07/2002. | UPU, https://www.upu.int/UPU/media/upu/PostalEntitiesFiles/addressingUnit/cmrFr.pdf | Fetched |
| English sheet, same format: "M. Pierre Marie / BP 6000 / YAOUNDE / CAMEROON". | https://www.upu.int/UPU/media/upu/PostalEntitiesFiles/addressingUnit/cmrEn.pdf | Fetched |
| Campost and FindMe signed a partnership on 1 Nov 2024. FindMe has been live in Cameroon since July 2024. The free app's address is "occupancy number, street name, postal code, city". The government "created postal codes covering the entire national territory". | WeAreTech Africa, https://www.wearetech.africa/en/fils-uk/news/tech/cameroun-campost-s-associe-a-findme-pour-numeriser-l-adressage-postal | Fetched |
| Cameroon "had no postal codes for its communes"; codes are now assigned per commune. Campost quote: "une carte d'identité postale qui permettra de géolocaliser tout bâtiment". | Ecomatin, https://ecomatin.net/cameroun-confrontee-a-des-difficultes-operationnelles-campost-lance-un-systeme-dadressage-numerique | Fetched |
| A certified address (Plan de Localisation Postale, PLP) costs 2,000 FCFA. "La boîte postale n'étant pas considérée comme une adresse réelle." No example code is given. | Cameroon Tribune, https://cameroon-tribune.cm/article.html/67781/fr.html/details_2 | Fetched (paywalled; free part only) |
| June 2025: CCA Bank joins Campost and FindMe. PLP addresses work with Google Maps and Waze. | Ecomatin, https://ecomatin.net/finance-week-2025-cca-bank-campost-et-findme-sassocient-pour-optimiser-le-systeme-dadressage-au-cameroun | Search only |
| Cameroon has no standardised postcode; mail is routed by locality name. | geopostcodes.com | Search only |
| The Campost homepage has no "code postal", "adresse" or "FindMe" text. | https://campost.cm/ | Fetched |

## Street addressing

| Finding | Source | Status |
|---|---|---|
| Yaoundé and Douala addressing projects were launched in 1992 under the World Bank's second Urban Development Project (UDP 2), extended in Douala in 1994–95 with French bilateral aid. Each city is divided into 6 major zones; a street is coded by two figures, zone and sequence ("street 4.15 is the 15th street in zone 4"); door numbering is metric and alternating; the survey recorded the occupant's name, plot use and cadastral references. A 1971 presidential circular gave instructions on street names. | Farvacque-Vitkovic et al., *Street Addressing and the Management of Cities*, World Bank (2005), Cameroon case study and table 3.1, https://documents1.worldbank.org/curated/en/573071468142795481/pdf/329230Street0Addressing01not0external1.pdf | Fetched |
| Interview with the government delegate to the CUD: "C'est en 1992 que la ville de Douala a engagé son opération d'adressage." | E. Batamag, Afrik.com, 8 Nov 2017, https://www.afrik.com/cameroun-une-ville-sans-systeme-d-orientation-est-une-ville-muette | Fetched |
| Even numbers on the right, odd on the left, by distance from the start of the street; a claim of 200 bn FCFA spent, with World Bank, AIMF and EU support. | camer.be (articles 67504, 67511) | Search only (camer.be gave 404 when fetched) |
| 2019: Douala has more than 250 km of roads, and under 15% of them have names (the government delegate to the CUD). | G. E. Tsayid, Cameroon Tribune, 24 Dec 2019, "Dénomination des rues : l'orientation des populations en question", https://www.cameroon-tribune.cm/article.html/29929/fr.html/ | Fetched (free part only) |
| Real Yaoundé addresses use "Rue NNNN": "No 1232 Immeuble Mellopolis, Rue 1794, Ekoudou, Bastos"; "Rue 1705, Numéro 606"; "335 Rue 1810". They are usually given with a BP and a landmark. | United Nations in Cameroon, contact page, https://cameroon.un.org/fr/contact-us | Fetched |
| A Yaoundé project planned to number about 100,000 doors and name 5,100 streets; at the time only 140 streets had names. | AFP via capitalfm.africa, "Streets with no names…" (undated, about 2016) | Search only |
| Decree no. 68/DF/314 of 9 Aug 1968 created the Commission nationale de toponymie. Municipal councils name the streets. | UN digital library, E/CONF.105/9/CRP.9 | Search only |
| Addressing efforts are confined to Douala and Yaoundé and deal with naming streets and places, not physical addresses. | Njoh, A. J. (2010), "Toponymic inscription, physical addressing and the challenge of urban management in an era of globalization in Cameroon", *Habitat International* 34(4), 427–435, doi:10.1016/j.habitatint.2009.12.002 | Fetched (abstract) |
| The World Bank approved a US$200M "Sustainable Cities and Land" project on 30 May 2025. It covers land administration, not street addressing. | https://www.worldbank.org/en/news/press-release/2025/05/30/new-project-boosts-infrastructure-and-land-services-in-cameroon | Search only |
| Example of an OSM coded street: addr:street "Rue 1.055" (central Yaoundé). | https://www.openstreetmap.org/node/4338286745 | Fetched 17 October 2026 |

**Not found:**
- a national street-naming decree of the 2010s;
- a MINHDU national addressing policy;
- an addressing component in a World Bank project;
- any 2024–2026 news on Douala or Yaoundé street addressing.

## Administrative structure (used by the model)

| Level | Count | Notes |
|---|---|---|
| Région / Region | 10 | ISO 3166-2 CM-AD, CE, EN, ES, LT, NO, NW, OU, SU, SW (https://en.wikipedia.org/wiki/ISO_3166-2:CM, fetched) |
| Département / Division | 58 | Standard count (not independently confirmed); OpenStreetMap has 58 inside Cameroon |
| Arrondissement / Subdivision (= commune area) | 360 | Standard count (not confirmed); OpenStreetMap has about 360 level-8 polygons inside Cameroon |
| Communauté urbaine / City council | 14 | Group the numbered communes d'arrondissement (Douala I–VI, Yaoundé I–VII, …); OSM level 7 |

**Special status of the North-West and South-West regions.** Source: Law no. 2019/024 of 24 Dec 2019, the General Code of Regional and Local Authorities (search only: Cameroon Tribune, https://leap.unep.org/en/countries/cm/national-legislation/loi-ndeg-2019024-du-24-decembre-2019-portant-code-general-des).
- Section 327(2) gives the two regions a specific regime "based on their historical, social and cultural values".
- Section 328 gives them a say in the Anglophone education subsystem and the common-law justice system.
- Section 329 sets up a Regional Assembly of 90 councillors in two houses: a House of Divisional Representatives (70) and a House of Chiefs. There is also a Regional Executive Council.
- Each region has a Public Independent Conciliator.
- These bodies were installed in December 2020. The legal basis is Article 62(2) of the 1996 Constitution.
- Official languages: French and English.

## Mapping agency

- **INC** (Institut National de Cartographie), Yaoundé, was created by decree 92/049 of 24 Mar 1992. Its listed site, http://www.inc-cameroun.cm/, did not respond on 18 Oct 2026.
- The UNGEGN 2025 Cameroon report (M. Simeu Kamdem, GEGN.2/2025/39/CRP.39, 9 March 2025; fetched) says toponymic activities in 2023–24 "restent contrariées" by the cost of living and insecurity in the North-West and South-West, and that the INC is the main national map producer: https://unstats.un.org/unsd/ungegn/sessions/4th_session_2025/documents/GEGN.2_2025_39_CRP39_item4b.pdf
- There is no national address geoportal. "GeoCameroun" exists only as an aspiration on the OSM wiki (fetched).

## Data protection

- **Loi n° 2024/017 du 23 décembre 2024 relative à la protection des données à caractère personnel.** After an 18-month grace period it took effect on **23 June 2026**.
- The law creates the Autorité de protection des données à caractère personnel (APDP).
- It restricts transfers abroad, which need the Authority's prior authorisation, and requires explicit consent. N-Ways' servers are outside Cameroon, so its processing counts as such a transfer.
- Sources: droitmediasfinance.com, cio-mag.com, digitalbusiness.africa (search only); DLA Piper, *Data Protection Laws of the World: Cameroon* (search only).
- **Unverified:** whether APDP members have been appointed and whether the implementing decrees have been issued.

## Land and cadastre (for importing plot outlines)

- **MINDCAF** (Ministère des Domaines, du Cadastre et des Affaires foncières) is responsible for "l'élaboration et la tenue des plans cadastraux" (https://fr.wikipedia.org/wiki/Ministère_des_Domaines,_du_Cadastre_et_des_Affaires_foncières, fetched). mindcaf.cm refused the connection.
- **Datum, fetched:** Douala 1948 / AEF west (EPSG:3119) has been "replaced by Manoca 1962 / UTM zone 32N (EPSG:2215)" (https://epsg.io/3119, https://epsg.io/2215).
- **Unverified (no source):**
  - Land law rests on ordonnances 74-1 and 74-2 of 6 July 1974, with titres fonciers issued under décret 76/165 as amended by décret 2005/481.
  - Modern survey plans use WGS 84 / UTM 32N or 33N.
  - Bornage is done by sworn géomètres registered with the Ordre National des Géomètres du Cameroun (ONGC).
  - No open parcel data exists.

## Population and census

- The last published census is the 3rd RGPH (2005).
- The 4th RGPH, run jointly with the agriculture census (RGAE), began on 24 Apr 2026 and ended fieldwork on 15 Sep 2026. No results have been published. The 2005 count was 17,463,836; the census bureau's projection before enumeration exceeded 28.8 million. Source: H. Kimeng, Cameroon Tribune, 16 Sep 2026, https://www.cameroon-tribune.cm/article.html/80700/en.html/details_2 (fetched).
- UN 2025 urban-area projections: Yaoundé about 5.1 M, Douala about 4.1 M (worldometers, search only).

## Languages

More than 250 languages are spoken (https://en.wikipedia.org/wiki/Languages_of_Cameroon; Echu, "The Language Question in Cameroon"; search only):
- Cameroonian Pidgin English (Kamtok) is the lingua franca of the NW and SW and is spreading into Littoral and West.
- Fulfulde is the northern lingua franca.
- Ewondo is a lingua franca in the Centre, South and East.
- Duala is used around Douala.

## OpenStreetMap and open alternatives

- OSM has some street names, e.g. "Rue 1.055" in Yaoundé and "Boulevard du Président Ahmadou Ahidjo" in Douala. Address tags are sparse.
- Open Location Code (Plus Codes, Apache-2.0, https://github.com/google/open-location-code) is open and works offline. N-Ways spot codes convert to Plus Codes.
- what3words is proprietary.

## Short forms of area names (plate names)

The plate-name rule (`docs/model.md` §2, `engine/SPEC.md` §2.5) takes a short form people already say only when a source documents it. At first issue no such source had been checked, so the table of documented short forms (`tools/name-ranges.py → KNOWN`) is empty and every short form is either derived by the rule or left to the commune (`needsCouncilChoice`). The commune quartier lists and the Commission nationale de toponymie (decree no. 68/DF/314, above) are where documented short forms should come from. Each one added must cite its source here and in `KNOWN`.
