# The N-Ways Cameroon model / Le modèle N-Ways Cameroun

Design notes: why each choice fits Cameroon. The rules themselves are in [engine/SPEC.md](../engine/SPEC.md) (normative) and, with every formula worked through on real codes, in the research paper ([paper.md](paper.md), [paper.fr.md](paper.fr.md)), whose evaluation measures the result on the full registry.

## 0. The rule above all: official addresses first

Where the State, a council or Campost gives an address, N-Ways shows it first, exactly as written. Every compound also has its N-Ways code, which never changes. Today that means the coded streets of Yaoundé and Douala (207,707 compounds within 30 m of one); council door numbers and Campost's commune codes and PLP addresses fill reserved fields as soon as they are shared or published ([integration-campost.md](integration-campost.md)).

## 1. Easy to remember, effortless to get

- **What people already say** is a quarter or village name and a landmark, and phone numbers in pairs. So a code is a **plate name and a number of three to five digits**, said in pairs: Bonapriso 14 01.
- **No context needed.** Every area with the same plate name shares one national range, cut into frozen blocks of twice its compounds; "name number" is unique in Cameroon with no town after it (30 Adjaps, 27 Melens, one range each).
- **At most five digits**, the most people say and remember as a pair and a hundred: every name's blocks fit 81,000 numbers with a tenth spare; the fullest, the 27 areas named Yaoundé, uses 49,000.
- **No check digit for people**: a digit nobody can check by eye is one more to get wrong; the Damm check lives in the machine form (`CM-DLA1-015-1401-6`), for systems.
- **Getting it** is one tap in the app ("Get my code"), at home or by tapping the compound on the map.

## 2. Plate names in the language of the place

At most 12 characters and 2 words, no digit; French in French-speaking arrondissements, English in the North-West and South-West. Cameroon's names often pair a landmark word with the place's own name ("Carrefour Laboratoire Meka", "Mission Catholique Mokolo"), so a list of 186 ordinary French and English words keeps the proper name (Meka, Mokolo) and never the landmark word. Local-language parts of names (Ouro, Mayo, Hosséré, Djaouro, Nkol, Mvog, Elig) and names of peoples (Haoussa, Foulbé) are names. Where nothing fits, the area carries its arrondissement's name until the council chooses (1,236 areas). The full official name is always an alias.

## 3. Zones: the 360 arrondissements

The arrondissement is the territory of one council, the level at which Campost assigns its commune codes, and it is stable: it is the machine form's zone (`DLA1`, `YDE6`, `BDA2`) and the frame of the spot grid. Regions and divisions are looked up from a compound's position and are never part of a code.

## 4. Spot codes: a 10 m numeric grid

Any point has a spot code on a 10 m grid over its arrondissement's frozen frame: `CM-DLA1 E0449 N0268`, digits only (no letters to learn), four per axis (five in arrondissements wider than 99.99 km), decoding to within 7.1 m.

The arrondissement outlines are generalised, so 240 issued compounds lie in no outline: 67 in slivers between arrondissements, 172 just over an outline at the shoreline or the national border (all within 62 m of one), and one industrial structure at sea 10.9 km off Kribi. A point in no outline takes, among the arrondissements whose outline lies within 12 km, the one with the nearest outline whose frame holds the point (ties to the lower key); if no such frame holds it, the nearest cell of a frame at most 5,000 m away. Every issued compound therefore has a spot code, and the registry keeps its exact entrance point. Frames never move, because moving one would change spot codes already published; a point farther from Cameroon is refused.

## 5. Compounds, not footprints

A code belongs to a compound and leads to its gate. Footprints are grouped before numbering: a mapped wall, fence or hedge makes one compound; an annex under 25 m² joins the nearest house within 8 m; outside Yaoundé and Douala, round huts under 40 m² at most 3 m apart form one compound of up to 25. Nothing else is merged: merging two codes later costs nothing, splitting a wrong merge gives a household a new code. Residents' answers in the app ("one home", "the gate is here") do the rest.

## 6. Building profile

Every structure carries a use class with its confidence and source (OpenStreetMap type, tags, N-Ways places inside, size, else residential by default), its size, floors where known, and a status. Homes never carry names.

## 7. Numbering

Inside an area, compounds are numbered along a Hilbert curve over the area's frozen frame, so neighbours have neighbouring numbers, with gaps for new homes and a tail reserve of a third of the block. Blocks never move, shrink or renumber; a full block takes an extension block of its name.

## 8. Safety

The registry publishes every code of every arrondissement: an address helps most where help is hardest to bring. The 187 arrondissements of the North-West, South-West, Far North, North, Adamawa and East regions, to which the UK FCDO advises against all or all but essential travel (9 February 2026), are flagged in the area table, and a code names a place, never a person.

## 9. Stability and hand-over

One issuer gives codes for the whole country (N-Ways today, or the body the State designates); codes are never reused; a council may rename an area once (the old name stays an alias). The repository can be handed to the State or a body it names under its open licences.
