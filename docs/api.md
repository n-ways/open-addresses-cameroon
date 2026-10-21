# The registry API

Every endpoint of the server in [`server/`](../server/README.md), with a real request and the real response, errors included. The responses below were produced by the server running on the complete published registry (7,243,272 codes, exported 2026-10-21T14:51:04Z); the issue and change examples ran on that same database, so the codes they create are not in the published registry. The machine-readable contract is [server/openapi.yaml](../server/openapi.yaml) (OpenAPI 3.1).

Conventions:

- Every response is JSON (`application/json; charset=utf-8`) with stable field names.
- Every error has the shape `{"error": {"code": "...", "message": "..."}}` and the matching HTTP status; `code` is stable, `message` is a sentence for people. A refused issue for a building that already has a code also carries `existing`, its card.
- Coordinates are WGS 84 degrees, `lat` then `lng`; outlines are lists of `[lng, lat]` points.
- A machine form is refused, never corrected, when its check digit is wrong. People's forms (`Bonapriso 14 01`) carry no check digit; a system may send one after a hyphen (`Bonapriso 14 01-6`) and it is verified.
- Reading needs no key. `POST /v1/codes` and `PATCH /v1/codes/{machine}` need `Authorization: Bearer <key>` and exist only on the designated issuer's deployment; elsewhere they answer `403 read_only`.
- Long lists are cut in the examples below, marked `... N more`.

| Endpoint | What it answers |
|---|---|
| [`GET /v1/health`](#get-v1health) | liveness, codes served, registry date |
| [`GET /v1/info`](#get-v1info) | the country, arrondissements, counts, licences, credit line, engine |
| [`GET /v1/codes/{machine}`](#get-v1codesmachine) | the full card of a code |
| [`GET /v1/find?q=`](#get-v1findq) | a code from a remembered form, machine form, official address or spot code |
| [`GET /v1/at?lat=&lng=`](#get-v1atlatlng) | the code of the compound at a point |
| [`GET /v1/near?lat=&lng=&radius=`](#get-v1nearlatlngradius) | the codes within a radius |
| [`GET /v1/verify?code=`](#get-v1verifycode) | whether a machine code is valid and issued |
| [`GET /v1/spot?lat=&lng=`](#get-v1spotlatlng) | the spot code of a point |
| [`GET /v1/spot/decode?code=`](#get-v1spotdecodecode) | the point of a spot code |
| [`GET /v1/zones`](#get-v1zones) | the 360 arrondissements |
| [`GET /v1/zones/{key}`](#get-v1zoneskey) | one arrondissement with its areas |
| [`GET /v1/zones/{key}/codes?after=&limit=`](#get-v1zoneskeycodesafterlimit) | its codes, page by page |
| [`GET /v1/areas/{id}`](#get-v1areasid) | an area |
| [`GET /v1/areas?name=`](#get-v1areasname) | the areas of a name |
| [`POST /v1/codes`](#post-v1codes) | issue a code (issuer only) |
| [`PATCH /v1/codes/{machine}`](#patch-v1codesmachine) | confirm, retire, move the entrance (issuer only) |

## GET /v1/health

Liveness and the registry served.

```sh
curl -s 'http://localhost:8080/v1/health'
```

Response `200`:

```json
{
  "status": "ok",
  "country": "CM",
  "codes": 7243272,
  "registryExported": "2026-10-21T14:51:04Z",
  "issuing": true
}
```

An endpoint that does not exist:

```sh
curl -s 'http://localhost:8080/v1/codez'
```

Response `404`:

```json
{
  "error": {
    "code": "not_found",
    "message": "There is no endpoint /v1/codez; see /v1/info and docs/api.md."
  }
}
```

A method an endpoint does not allow:

```sh
curl -s -X DELETE 'http://localhost:8080/v1/health'
```

Response `405`:

```json
{
  "error": {
    "code": "method_not_allowed",
    "message": "DELETE is not allowed here; use GET."
  }
}
```

## GET /v1/info

The country, its arrondissements and counts, licences, credit line and engine.

```sh
curl -s 'http://localhost:8080/v1/info'
```

Response `200`:

```json
{
  "country": "CM",
  "name": "Cameroon",
  "codes": 7243272,
  "byStatus": {
    "provisional": 7243272
  },
  "byIssue": {
    "bulk": 7243272
  },
  "zones": [
    {
      "key": "BAF1",
      "name": "Bafoussam I",
      "nameEn": "Bafoussam 1",
      "region": "CM-OU",
      "codes": 48996,
      "areas": 48
    },
    {
      "key": "BAF2",
      "name": "Bafoussam II",
      "nameEn": "Bafoussam 2",
      "region": "CM-OU",
      "codes": 52427,
      "areas": 51
    },
    {
      "key": "BAF3",
      "name": "Bafoussam III",
      "nameEn": "Bafoussam 3",
      "region": "CM-OU",
      "codes": 48900,
      "areas": 51
    },
    "... 357 more"
  ],
  "areas": 24213,
  "areasWithCodes": 23208,
  "names": 17240,
  "registryExported": "2026-10-21T14:51:04Z",
  "importedAt": "2026-10-21T14:59:35Z",
  "engine": "internal/addressing/cm (SPEC v1.0)",
  "spec": "engine/SPEC.md",
  "licences": {
    "data": "ODbL 1.0 (LICENSE-DATA)",
    "code": "Apache-2.0 (LICENSE)",
    "documents": "CC BY 4.0 (LICENSE-DOCS)"
  },
  "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-cameroon",
  "issuing": true,
  "issuePerDay": 50,
  "example": {
    "remembered": "Bonapriso 14 01",
    "machine": "CM-DLA1-015-1401-6",
    "spot": "CM-DLA1 E0449 N0268"
  }
}
```

## GET /v1/codes/{machine}

The full card of an issued code: every registry column under `record`, named, with the spot code, Plus Code, area, arrondissement, and the remembered, written and spoken forms. People see the remembered or written form, never the check digit.

```sh
curl -s 'http://localhost:8080/v1/codes/CM-DLA1-015-1401-6'
```

Response `200`:

```json
{
  "country": "CM",
  "machine": "CM-DLA1-015-1401-6",
  "home": "Bonapriso 1401",
  "written": "Bonapriso 14 01",
  "spoken": "Bonapriso, 14 01",
  "number": 1401,
  "check": 6,
  "status": "provisional",
  "issued": "bulk",
  "issuedAt": "2026-10-21T06:05:31Z",
  "area": {
    "key": "DLA1-015",
    "id": 4368,
    "plateName": "Bonapriso",
    "officialName": "Bonapriso",
    "provisionalName": false,
    "zone": "DLA1",
    "zoneName": "Douala I"
  },
  "zone": {
    "key": "DLA1",
    "name": "Douala I",
    "nameEn": "Douala 1",
    "region": "CM-LT",
    "language": "fr",
    "index": 20
  },
  "officialAddress": null,
  "entrance": {
    "lat": 4.0243022,
    "lng": 9.6904852,
    "kind": "centre"
  },
  "spotCode": "CM-DLA1 E0449 N0268",
  "plusCode": "6FPF2MFR+P5H",
  "profile": {
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": 1,
    "floorAreaM2": 852.7,
    "rule": "single",
    "estate": null
  },
  "record": {
    "machine": "CM-DLA1-015-1401-6",
    "home": "Bonapriso 1401",
    "written": "Bonapriso 14 01",
    "zone": "DLA1-015",
    "official_name": "Bonapriso",
    "number": "1401",
    "check": "6",
    "status": "provisional",
    "issued": "bulk",
    "issued_at": "2026-10-21T06:05:31Z",
    "entrance_lat": "4.0243022",
    "entrance_lng": "9.6904852",
    "entrance_kind": "centre",
    "spot_code": "CM-DLA1 E0449 N0268",
    "official_address": "",
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": "1",
    "floor_area_m2": "852.7",
    "rule": "single",
    "estate": ""
  },
  "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
}
```

A code in the English-speaking North-West: the arrondissement is shown by its English name:

```sh
curl -s 'http://localhost:8080/v1/codes/CM-BDA1-001-1000-1'
```

Response `200`:

```json
{
  "country": "CM",
  "machine": "CM-BDA1-001-1000-1",
  "home": "Bamendankwe 1000",
  "written": "Bamendankwe 10 00",
  "spoken": "Bamendankwe, 10 00",
  "number": 1000,
  "check": 1,
  "status": "provisional",
  "issued": "bulk",
  "issuedAt": "2026-10-21T05:57:16Z",
  "area": {
    "key": "BDA1-001",
    "id": 766,
    "plateName": "Bamendankwe",
    "officialName": "Bamendankwe",
    "provisionalName": false,
    "zone": "BDA1",
    "zoneName": "Bamenda 1"
  },
  "zone": {
    "key": "BDA1",
    "name": "Bamenda I",
    "nameEn": "Bamenda 1",
    "region": "CM-NW",
    "language": "en",
    "index": 31
  },
  "officialAddress": null,
  "entrance": {
    "lat": 5.8885963,
    "lng": 10.2257039,
    "kind": "centre"
  },
  "spotCode": "CM-BDA1 E0948 N0426",
  "plusCode": "6FQGV6QG+C7P",
  "profile": {
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": 1,
    "floorAreaM2": 42.6,
    "rule": "single",
    "estate": null
  },
  "record": {
    "machine": "CM-BDA1-001-1000-1",
    "home": "Bamendankwe 1000",
    "written": "Bamendankwe 10 00",
    "zone": "BDA1-001",
    "official_name": "Bamendankwe",
    "number": "1000",
    "check": "1",
    "status": "provisional",
    "issued": "bulk",
    "issued_at": "2026-10-21T05:57:16Z",
    "entrance_lat": "5.8885963",
    "entrance_lng": "10.2257039",
    "entrance_kind": "centre",
    "spot_code": "CM-BDA1 E0948 N0426",
    "official_address": "",
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": "1",
    "floor_area_m2": "42.6",
    "rule": "single",
    "estate": ""
  },
  "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
}
```

A wrong check digit is refused, not corrected:

```sh
curl -s 'http://localhost:8080/v1/codes/CM-DLA1-015-1401-5'
```

Response `422`:

```json
{
  "error": {
    "code": "check_digit",
    "message": "The check digit does not match: a digit is wrong or two are swapped."
  }
}
```

Without its check digit:

```sh
curl -s 'http://localhost:8080/v1/codes/CM-DLA1-015-1401'
```

Response `400`:

```json
{
  "error": {
    "code": "bad_code",
    "message": "A machine code ends with its check digit; use /v1/find to look up a code without it."
  }
}
```

An area that does not exist:

```sh
curl -s 'http://localhost:8080/v1/codes/CM-DLA1-999-1401-1'
```

Response `404`:

```json
{
  "error": {
    "code": "unknown_area",
    "message": "There is no area 999 in zone DLA1."
  }
}
```

A number outside the area's blocks:

```sh
curl -s 'http://localhost:8080/v1/codes/CM-DLA1-015-9401-1'
```

Response `404`:

```json
{
  "error": {
    "code": "not_in_area",
    "message": "9401 is in none of the blocks of Bonapriso (DLA1-015): a digit is wrong."
  }
}
```

A valid code that no compound holds yet:

```sh
curl -s 'http://localhost:8080/v1/codes/CM-DLA1-015-2929-9'
```

Response `404`:

```json
{
  "error": {
    "code": "not_issued",
    "message": "CM-DLA1-015-2929-9 is a valid code but no compound has it."
  }
}
```

## GET /v1/find?q=

Finds a code from what a person says or types: a remembered or written form in any spacing, case or accents (`Bonapriso 14 01`, `bonapriso1401`), an official name in place of the plate name, a machine form, an official address, or a spot code. A check digit sent by a system after a hyphen is verified; a wrong one is refused, never guessed. `limit` (1-100, default 20) caps the matches of an official address.

A remembered form, typed loosely:

```sh
curl -s 'http://localhost:8080/v1/find?q=bonapriso%201401'
```

Response `200`:

```json
{
  "query": "bonapriso 1401",
  "kind": "remembered",
  "matches": [
    {
      "country": "CM",
      "machine": "CM-DLA1-015-1401-6",
      "home": "Bonapriso 1401",
      "written": "Bonapriso 14 01",
      "spoken": "Bonapriso, 14 01",
      "number": 1401,
      "check": 6,
      "status": "provisional",
      "issued": "bulk",
      "issuedAt": "2026-10-21T06:05:31Z",
      "area": {
        "key": "DLA1-015",
        "id": 4368,
        "plateName": "Bonapriso",
        "officialName": "Bonapriso",
        "provisionalName": false,
        "zone": "DLA1",
        "zoneName": "Douala I"
      },
      "zone": {
        "key": "DLA1",
        "name": "Douala I",
        "nameEn": "Douala 1",
        "region": "CM-LT",
        "language": "fr",
        "index": 20
      },
      "officialAddress": null,
      "entrance": {
        "lat": 4.0243022,
        "lng": 9.6904852,
        "kind": "centre"
      },
      "spotCode": "CM-DLA1 E0449 N0268",
      "plusCode": "6FPF2MFR+P5H",
      "profile": {
        "class": "residential",
        "use": "residential",
        "kind": "building",
        "structures": 1,
        "floorAreaM2": 852.7,
        "rule": "single",
        "estate": null
      },
      "record": {
        "machine": "CM-DLA1-015-1401-6",
        "home": "Bonapriso 1401",
        "written": "Bonapriso 14 01",
        "zone": "DLA1-015",
        "official_name": "Bonapriso",
        "number": "1401",
        "check": "6",
        "status": "provisional",
        "issued": "bulk",
        "issued_at": "2026-10-21T06:05:31Z",
        "entrance_lat": "4.0243022",
        "entrance_lng": "9.6904852",
        "entrance_kind": "centre",
        "spot_code": "CM-DLA1 E0449 N0268",
        "official_address": "",
        "class": "residential",
        "use": "residential",
        "kind": "building",
        "structures": "1",
        "floor_area_m2": "852.7",
        "rule": "single",
        "estate": ""
      },
      "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
      "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
    }
  ],
  "total": 1
}
```

A machine form:

```sh
curl -s 'http://localhost:8080/v1/find?q=cm-dla1-015-1401-6'
```

Response `200`:

```json
{
  "query": "cm-dla1-015-1401-6",
  "kind": "machine",
  "checked": true,
  "matches": [
    {
      "country": "CM",
      "machine": "CM-DLA1-015-1401-6",
      "home": "Bonapriso 1401",
      "written": "Bonapriso 14 01",
      "spoken": "Bonapriso, 14 01",
      "number": 1401,
      "check": 6,
      "status": "provisional",
      "issued": "bulk",
      "issuedAt": "2026-10-21T06:05:31Z",
      "area": {
        "key": "DLA1-015",
        "id": 4368,
        "plateName": "Bonapriso",
        "officialName": "Bonapriso",
        "provisionalName": false,
        "zone": "DLA1",
        "zoneName": "Douala I"
      },
      "zone": {
        "key": "DLA1",
        "name": "Douala I",
        "nameEn": "Douala 1",
        "region": "CM-LT",
        "language": "fr",
        "index": 20
      },
      "officialAddress": null,
      "entrance": {
        "lat": 4.0243022,
        "lng": 9.6904852,
        "kind": "centre"
      },
      "spotCode": "CM-DLA1 E0449 N0268",
      "plusCode": "6FPF2MFR+P5H",
      "profile": {
        "class": "residential",
        "use": "residential",
        "kind": "building",
        "structures": 1,
        "floorAreaM2": 852.7,
        "rule": "single",
        "estate": null
      },
      "record": {
        "machine": "CM-DLA1-015-1401-6",
        "home": "Bonapriso 1401",
        "written": "Bonapriso 14 01",
        "zone": "DLA1-015",
        "official_name": "Bonapriso",
        "number": "1401",
        "check": "6",
        "status": "provisional",
        "issued": "bulk",
        "issued_at": "2026-10-21T06:05:31Z",
        "entrance_lat": "4.0243022",
        "entrance_lng": "9.6904852",
        "entrance_kind": "centre",
        "spot_code": "CM-DLA1 E0449 N0268",
        "official_address": "",
        "class": "residential",
        "use": "residential",
        "kind": "building",
        "structures": "1",
        "floor_area_m2": "852.7",
        "rule": "single",
        "estate": ""
      },
      "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
      "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
    }
  ],
  "total": 1
}
```

An official address (Yaoundé and Douala streets come first on the card):

```sh
curl -s 'http://localhost:8080/v1/find?limit=2&q=Rue%201.074%2C%20Yaound%C3%A9'
```

Response `200`:

```json
{
  "query": "Rue 1.074, Yaoundé",
  "kind": "officialAddress",
  "matches": [
    {
      "country": "CM",
      "machine": "CM-YDE1-004-1247-8",
      "home": "Nlongkak 1247",
      "written": "Nlongkak 12 47",
      "spoken": "Nlongkak, 12 47",
      "number": 1247,
      "check": 8,
      "status": "provisional",
      "issued": "bulk",
      "issuedAt": "2026-10-21T06:26:12Z",
      "area": {
        "key": "YDE1-004",
        "id": 23910,
        "plateName": "Nlongkak",
        "officialName": "Carrefour Bata Nlongkak",
        "provisionalName": true,
        "zone": "YDE1",
        "zoneName": "Yaoundé I"
      },
      "zone": {
        "key": "YDE1",
        "name": "Yaoundé I",
        "nameEn": "Yaounde 1",
        "region": "CM-CE",
        "language": "fr",
        "index": 3
      },
      "officialAddress": "Rue 1.074, Yaoundé",
      "entrance": {
        "lat": 3.8891889,
        "lng": 11.5227859,
        "kind": "centre"
      },
      "spotCode": "CM-YDE1 E0586 N0322",
      "plusCode": "6FMHVGQF+M4F",
      "profile": {
        "class": "government",
        "use": "government",
        "kind": "building",
        "structures": 1,
        "floorAreaM2": 155.7,
        "rule": "single",
        "estate": "nways:w193961654"
      },
      "record": {
        "machine": "CM-YDE1-004-1247-8",
        "home": "Nlongkak 1247",
        "written": "Nlongkak 12 47",
        "zone": "YDE1-004",
        "official_name": "Carrefour Bata Nlongkak",
        "number": "1247",
        "check": "8",
        "status": "provisional",
        "issued": "bulk",
        "issued_at": "2026-10-21T06:26:12Z",
        "entrance_lat": "3.8891889",
        "entrance_lng": "11.5227859",
        "entrance_kind": "centre",
        "spot_code": "CM-YDE1 E0586 N0322",
        "official_address": "Rue 1.074, Yaoundé",
        "class": "government",
        "use": "government",
        "kind": "building",
        "structures": "1",
        "floor_area_m2": "155.7",
        "rule": "single",
        "estate": "nways:w193961654"
      },
      "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
      "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
    },
    {
      "country": "CM",
      "machine": "CM-YDE1-004-1248-6",
      "home": "Nlongkak 1248",
      "written": "Nlongkak 12 48",
      "spoken": "Nlongkak, 12 48",
      "number": 1248,
      "check": 6,
      "status": "provisional",
      "issued": "bulk",
      "issuedAt": "2026-10-21T06:26:12Z",
      "area": {
        "key": "YDE1-004",
        "id": 23910,
        "plateName": "Nlongkak",
        "officialName": "Carrefour Bata Nlongkak",
        "provisionalName": true,
        "zone": "YDE1",
        "zoneName": "Yaoundé I"
      },
      "zone": {
        "key": "YDE1",
        "name": "Yaoundé I",
        "nameEn": "Yaounde 1",
        "region": "CM-CE",
        "language": "fr",
        "index": 3
      },
      "officialAddress": "Rue 1.074, Yaoundé",
      "entrance": {
        "lat": 3.8892019,
        "lng": 11.522701,
        "kind": "centre"
      },
      "spotCode": "CM-YDE1 E0585 N0322",
      "plusCode": "6FMHVGQF+M3P",
      "profile": {
        "class": "government",
        "use": "government",
        "kind": "building",
        "structures": 1,
        "floorAreaM2": 33.2,
        "rule": "single",
        "estate": null
      },
      "record": {
        "machine": "CM-YDE1-004-1248-6",
        "home": "Nlongkak 1248",
        "written": "Nlongkak 12 48",
        "zone": "YDE1-004",
        "official_name": "Carrefour Bata Nlongkak",
        "number": "1248",
        "check": "6",
        "status": "provisional",
        "issued": "bulk",
        "issued_at": "2026-10-21T06:26:12Z",
        "entrance_lat": "3.8892019",
        "entrance_lng": "11.5227010",
        "entrance_kind": "centre",
        "spot_code": "CM-YDE1 E0585 N0322",
        "official_address": "Rue 1.074, Yaoundé",
        "class": "government",
        "use": "government",
        "kind": "building",
        "structures": "1",
        "floor_area_m2": "33.2",
        "rule": "single",
        "estate": ""
      },
      "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
      "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
    }
  ],
  "total": 108
}
```

A spot code:

```sh
curl -s 'http://localhost:8080/v1/find?q=CM-DLA1%20E0449%20N0268'
```

Response `200`:

```json
{
  "query": "CM-DLA1 E0449 N0268",
  "kind": "spot",
  "matches": [
    {
      "country": "CM",
      "machine": "CM-DLA1-015-1401-6",
      "home": "Bonapriso 1401",
      "written": "Bonapriso 14 01",
      "spoken": "Bonapriso, 14 01",
      "number": 1401,
      "check": 6,
      "status": "provisional",
      "issued": "bulk",
      "issuedAt": "2026-10-21T06:05:31Z",
      "area": {
        "key": "DLA1-015",
        "id": 4368,
        "plateName": "Bonapriso",
        "officialName": "Bonapriso",
        "provisionalName": false,
        "zone": "DLA1",
        "zoneName": "Douala I"
      },
      "zone": {
        "key": "DLA1",
        "name": "Douala I",
        "nameEn": "Douala 1",
        "region": "CM-LT",
        "language": "fr",
        "index": 20
      },
      "officialAddress": null,
      "entrance": {
        "lat": 4.0243022,
        "lng": 9.6904852,
        "kind": "centre"
      },
      "spotCode": "CM-DLA1 E0449 N0268",
      "plusCode": "6FPF2MFR+P5H",
      "profile": {
        "class": "residential",
        "use": "residential",
        "kind": "building",
        "structures": 1,
        "floorAreaM2": 852.7,
        "rule": "single",
        "estate": null
      },
      "record": {
        "machine": "CM-DLA1-015-1401-6",
        "home": "Bonapriso 1401",
        "written": "Bonapriso 14 01",
        "zone": "DLA1-015",
        "official_name": "Bonapriso",
        "number": "1401",
        "check": "6",
        "status": "provisional",
        "issued": "bulk",
        "issued_at": "2026-10-21T06:05:31Z",
        "entrance_lat": "4.0243022",
        "entrance_lng": "9.6904852",
        "entrance_kind": "centre",
        "spot_code": "CM-DLA1 E0449 N0268",
        "official_address": "",
        "class": "residential",
        "use": "residential",
        "kind": "building",
        "structures": "1",
        "floor_area_m2": "852.7",
        "rule": "single",
        "estate": ""
      },
      "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
      "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
    }
  ],
  "total": 1
}
```

A wrong check digit after a remembered form:

```sh
curl -s 'http://localhost:8080/v1/find?q=Bonapriso%2014%2001-5'
```

Response `422`:

```json
{
  "error": {
    "code": "check_digit",
    "message": "The check digit does not match: a mistyped name or number."
  }
}
```

A number with the wrong count of digits:

```sh
curl -s 'http://localhost:8080/v1/find?q=Bonapriso%20140'
```

Response `404`:

```json
{
  "error": {
    "code": "wrong_length",
    "message": "Numbers of Bonapriso have 4 digits."
  }
}
```

A number no compound holds:

```sh
curl -s 'http://localhost:8080/v1/find?q=Bonapriso%209999'
```

Response `404`:

```json
{
  "error": {
    "code": "not_issued",
    "message": "Bonapriso 99 99 is not issued: no area holds this number."
  }
}
```

A name no area has:

```sh
curl -s 'http://localhost:8080/v1/find?q=Qwertyville%20123'
```

Response `404`:

```json
{
  "error": {
    "code": "unknown_name",
    "message": "No area of Cameroon is called “Qwertyville”."
  }
}
```

Nothing recognisable:

```sh
curl -s 'http://localhost:8080/v1/find?q=hello'
```

Response `404`:

```json
{
  "error": {
    "code": "not_found",
    "message": "Nothing matches: give a remembered code (\"Bonapriso 14 01\"), a machine code (\"CM-DLA1-015-1401-6\"), an official address or a spot code (\"CM-DLA1 E0449 N0268\")."
  }
}
```

No query:

```sh
curl -s 'http://localhost:8080/v1/find?q='
```

Response `400`:

```json
{
  "error": {
    "code": "missing_q",
    "message": "The query parameter q is required."
  }
}
```

## GET /v1/at?lat=&lng=

The code of the compound at a point: the nearest live entrance within 12 m (or an outline issued on this server that holds the point), as the N-Ways service decides "found". Otherwise `status: "none"`, the area a new compound there would join, and the nearest code within 100 m. A point is in Cameroon when an arrondissement outline holds it, or when the spot-code rule gives it a zone ([SPEC §5](../engine/SPEC.md#5-spot-codes)), as the compounds in the slivers between outlines and along the shoreline and the border are; a point the rule refuses (no outline within 12 km, or no frame within 5,000 m) is outside (`404 outside`).

```sh
curl -s 'http://localhost:8080/v1/at?lat=4.0243022&lng=9.6904852'
```

Response `200`:

```json
{
  "status": "found",
  "code": {
    "country": "CM",
    "machine": "CM-DLA1-015-1401-6",
    "home": "Bonapriso 1401",
    "written": "Bonapriso 14 01",
    "spoken": "Bonapriso, 14 01",
    "number": 1401,
    "check": 6,
    "status": "provisional",
    "issued": "bulk",
    "issuedAt": "2026-10-21T06:05:31Z",
    "area": {
      "key": "DLA1-015",
      "id": 4368,
      "plateName": "Bonapriso",
      "officialName": "Bonapriso",
      "provisionalName": false,
      "zone": "DLA1",
      "zoneName": "Douala I"
    },
    "zone": {
      "key": "DLA1",
      "name": "Douala I",
      "nameEn": "Douala 1",
      "region": "CM-LT",
      "language": "fr",
      "index": 20
    },
    "officialAddress": null,
    "entrance": {
      "lat": 4.0243022,
      "lng": 9.6904852,
      "kind": "centre"
    },
    "spotCode": "CM-DLA1 E0449 N0268",
    "plusCode": "6FPF2MFR+P5H",
    "profile": {
      "class": "residential",
      "use": "residential",
      "kind": "building",
      "structures": 1,
      "floorAreaM2": 852.7,
      "rule": "single",
      "estate": null
    },
    "record": {
      "machine": "CM-DLA1-015-1401-6",
      "home": "Bonapriso 1401",
      "written": "Bonapriso 14 01",
      "zone": "DLA1-015",
      "official_name": "Bonapriso",
      "number": "1401",
      "check": "6",
      "status": "provisional",
      "issued": "bulk",
      "issued_at": "2026-10-21T06:05:31Z",
      "entrance_lat": "4.0243022",
      "entrance_lng": "9.6904852",
      "entrance_kind": "centre",
      "spot_code": "CM-DLA1 E0449 N0268",
      "official_address": "",
      "class": "residential",
      "use": "residential",
      "kind": "building",
      "structures": "1",
      "floor_area_m2": "852.7",
      "rule": "single",
      "estate": ""
    },
    "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
    "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
  },
  "distanceM": 0,
  "area": {
    "key": "DLA1-015",
    "id": 4368,
    "plateName": "Bonapriso",
    "officialName": "Bonapriso",
    "provisionalName": false,
    "zone": "DLA1",
    "zoneName": "Douala I"
  }
}
```

No compound at the point:

```sh
curl -s 'http://localhost:8080/v1/at?lat=4.0700&lng=9.7350'
```

Response `200`:

```json
{
  "status": "none",
  "canIssue": true,
  "area": {
    "key": "DLA5-039",
    "id": 4556,
    "plateName": "II Yonyong",
    "officialName": "Makepe II Yonyong",
    "provisionalName": false,
    "zone": "DLA5",
    "zoneName": "Douala V"
  },
  "nearest": {
    "machine": "CM-DLA5-039-1606-6",
    "home": "II Yonyong 1606",
    "written": "II Yonyong 16 06",
    "status": "provisional",
    "area": "DLA5-039",
    "entrance": {
      "lat": 4.0700218,
      "lng": 9.7348832
    },
    "distanceM": 13.2
  }
}
```

Outside Cameroon:

```sh
curl -s 'http://localhost:8080/v1/at?lat=6.455&lng=3.394'
```

Response `404`:

```json
{
  "error": {
    "code": "outside",
    "message": "The point is outside Cameroon."
  }
}
```

A coordinate that is not a number:

```sh
curl -s 'http://localhost:8080/v1/at?lat=x&lng=9.69'
```

Response `400`:

```json
{
  "error": {
    "code": "bad_lat",
    "message": "lat is a number."
  }
}
```

## GET /v1/near?lat=&lng=&radius=

The codes whose entrance lies within `radius` metres (default 100, at most 500), nearest first, at most `limit` (default and maximum 100). `total` counts them all. The point must be in Cameroon, as for [`GET /v1/at`](#get-v1atlatlng) (`404 outside`).

```sh
curl -s 'http://localhost:8080/v1/near?lat=4.0243022&lng=9.6904852&radius=30&limit=3'
```

Response `200`:

```json
{
  "point": {
    "lat": 4.0243022,
    "lng": 9.6904852
  },
  "radiusM": 30.0,
  "total": 3,
  "codes": [
    {
      "machine": "CM-DLA1-015-1401-6",
      "home": "Bonapriso 1401",
      "written": "Bonapriso 14 01",
      "status": "provisional",
      "area": "DLA1-015",
      "entrance": {
        "lat": 4.0243022,
        "lng": 9.6904852
      },
      "distanceM": 0.0
    },
    {
      "machine": "CM-DLA1-015-1400-3",
      "home": "Bonapriso 1400",
      "written": "Bonapriso 14 00",
      "status": "provisional",
      "area": "DLA1-015",
      "entrance": {
        "lat": 4.0244512,
        "lng": 9.6903288
      },
      "distanceM": 23.9
    },
    {
      "machine": "CM-DLA1-015-1402-7",
      "home": "Bonapriso 1402",
      "written": "Bonapriso 14 02",
      "status": "provisional",
      "area": "DLA1-015",
      "entrance": {
        "lat": 4.0242791,
        "lng": 9.6907182
      },
      "distanceM": 26.0
    }
  ]
}
```

A radius over 500 m:

```sh
curl -s 'http://localhost:8080/v1/near?lat=4.0243022&lng=9.6904852&radius=800'
```

Response `400`:

```json
{
  "error": {
    "code": "bad_radius",
    "message": "radius is in metres, more than 0 and at most 500."
  }
}
```

## GET /v1/verify?code=

Checks a machine code: its syntax, its area, its blocks, its check digit and whether a compound holds it. A wrong check digit is reported, never corrected.

```sh
curl -s 'http://localhost:8080/v1/verify?code=CM-DLA1-015-1401-6'
```

Response `200`:

```json
{
  "code": "CM-DLA1-015-1401-6",
  "syntax": true,
  "checkDigit": "ok",
  "inBlocks": true,
  "valid": true,
  "issued": true,
  "area": "DLA1-015",
  "status": "provisional",
  "machine": "CM-DLA1-015-1401-6",
  "home": "Bonapriso 1401"
}
```

A wrong check digit:

```sh
curl -s 'http://localhost:8080/v1/verify?code=CM-DLA1-015-1401-5'
```

Response `200`:

```json
{
  "code": "CM-DLA1-015-1401-5",
  "syntax": true,
  "checkDigit": "wrong",
  "inBlocks": true,
  "valid": false,
  "issued": false,
  "area": "DLA1-015",
  "reason": "the check digit does not match: a digit is wrong or two are swapped"
}
```

No check digit:

```sh
curl -s 'http://localhost:8080/v1/verify?code=CM-DLA1-015-1401'
```

Response `200`:

```json
{
  "code": "CM-DLA1-015-1401",
  "syntax": true,
  "checkDigit": "absent",
  "inBlocks": true,
  "valid": false,
  "issued": true,
  "area": "DLA1-015",
  "reason": "no check digit: the code cannot be validated",
  "status": "provisional",
  "machine": "CM-DLA1-015-1401-6",
  "home": "Bonapriso 1401"
}
```

Not a machine code:

```sh
curl -s 'http://localhost:8080/v1/verify?code=Bonapriso'
```

Response `200`:

```json
{
  "code": "Bonapriso",
  "syntax": false,
  "checkDigit": null,
  "inBlocks": null,
  "valid": false,
  "issued": false,
  "reason": "not a machine code: CM-<zone>-<area>-<number>-<check>"
}
```

No code:

```sh
curl -s 'http://localhost:8080/v1/verify'
```

Response `400`:

```json
{
  "error": {
    "code": "missing_code",
    "message": "The query parameter code is required."
  }
}
```

## GET /v1/spot?lat=&lng=

The spot code of a point: its 10 m cell on the frozen frame of the arrondissement whose outline holds it, and the cell centre. A point in no outline (a sliver between arrondissements, the shoreline, the sea) takes the arrondissement with the nearest outline within 12 km whose frame holds it, ties to the lower key, or else the nearest cell of a frame at most 5,000 m away ([SPEC §5](../engine/SPEC.md#5-spot-codes)). A point farther away is outside Cameroon.

```sh
curl -s 'http://localhost:8080/v1/spot?lat=4.0243022&lng=9.6904852'
```

Response `200`:

```json
{
  "spot": "CM-DLA1 E0449 N0268",
  "zone": {
    "key": "DLA1",
    "name": "Douala I",
    "nameEn": "Douala 1",
    "region": "CM-LT",
    "language": "fr",
    "index": 20
  },
  "cellM": 10,
  "centre": {
    "lat": 4.0242824,
    "lng": 9.6904802
  }
}
```

A compound in a sliver between two outlines (Yoyo Bar, Yaoundé II): the nearest outline, Yaoundé VII's, is 5.6 m away.

```sh
curl -s 'http://localhost:8080/v1/spot?lat=3.8751747&lng=11.4844409'
```

Response `200`:

```json
{
  "spot": "CM-YDE7 E0826 N0499",
  "zone": {
    "key": "YDE7",
    "name": "Yaoundé VII",
    "nameEn": "Yaounde 7",
    "region": "CM-CE",
    "language": "fr",
    "index": 9
  },
  "cellM": 10,
  "centre": {
    "lat": 3.8751734,
    "lng": 11.4844151
  }
}
```

Outside Cameroon:

```sh
curl -s 'http://localhost:8080/v1/spot?lat=6.455&lng=3.394'
```

Response `404`:

```json
{
  "error": {
    "code": "outside",
    "message": "The point is outside Cameroon."
  }
}
```

## GET /v1/spot/decode?code=

The centre of a spot code's cell, and the code of the compound within 15 m of it, if any.

```sh
curl -s 'http://localhost:8080/v1/spot/decode?code=CM-DLA1%20E0449%20N0268'
```

Response `200`:

```json
{
  "spot": "CM-DLA1 E0449 N0268",
  "zone": {
    "key": "DLA1",
    "name": "Douala I",
    "nameEn": "Douala 1",
    "region": "CM-LT",
    "language": "fr",
    "index": 20
  },
  "centre": {
    "lat": 4.0242824,
    "lng": 9.6904802
  },
  "cellM": 10,
  "code": {
    "machine": "CM-DLA1-015-1401-6",
    "home": "Bonapriso 1401",
    "written": "Bonapriso 14 01",
    "status": "provisional",
    "area": "DLA1-015",
    "entrance": {
      "lat": 4.0243022,
      "lng": 9.6904852
    },
    "distanceM": 2.3
  }
}
```

Not a spot code:

```sh
curl -s 'http://localhost:8080/v1/spot/decode?code=hello'
```

Response `400`:

```json
{
  "error": {
    "code": "bad_spot",
    "message": "A spot code is CM-<zone> E<east> N<north>, e.g. CM-DLA1 E0449 N0268."
  }
}
```

The wrong count of digits for the arrondissement:

```sh
curl -s 'http://localhost:8080/v1/spot/decode?code=CM-DLA1%20E01234%20N1234'
```

Response `422`:

```json
{
  "error": {
    "code": "bad_spot",
    "message": "Wrong number of digits for this zone frame."
  }
}
```

## GET /v1/zones

The 360 arrondissements, with their codes and areas.

```sh
curl -s 'http://localhost:8080/v1/zones'
```

Response `200`:

```json
{
  "zones": [
    {
      "key": "BAF1",
      "index": 32,
      "name": "Bafoussam I",
      "nameEn": "Bafoussam 1",
      "region": "CM-OU",
      "language": "fr",
      "codes": 48996,
      "areas": 48
    },
    {
      "key": "BAF2",
      "index": 33,
      "name": "Bafoussam II",
      "nameEn": "Bafoussam 2",
      "region": "CM-OU",
      "language": "fr",
      "codes": 52427,
      "areas": 51
    },
    {
      "key": "BAF3",
      "index": 34,
      "name": "Bafoussam III",
      "nameEn": "Bafoussam 3",
      "region": "CM-OU",
      "language": "fr",
      "codes": 48900,
      "areas": 51
    },
    "... 357 more"
  ],
  "total": 360
}
```

## GET /v1/zones/{key}

One arrondissement: its frame and its areas with their blocks and codes.

```sh
curl -s 'http://localhost:8080/v1/zones/DLA1'
```

Response `200`:

```json
{
  "key": "DLA1",
  "name": "Douala I",
  "nameEn": "Douala 1",
  "region": "CM-LT",
  "language": "fr",
  "index": 20,
  "frame": {
    "lon0": 9.65,
    "lat0": 4.0,
    "latc": 4.05,
    "digitsE": 4,
    "digitsN": 4
  },
  "codes": 26154,
  "areas": [
    {
      "key": "DLA1-001",
      "id": 4354,
      "plateName": "Akwa",
      "officialName": "Akwa",
      "provisionalName": false,
      "zone": "DLA1",
      "zoneName": "Douala I",
      "codes": 463,
      "blocks": [
        [
          1000,
          1929
        ]
      ]
    },
    {
      "key": "DLA1-002",
      "id": 4355,
      "plateName": "Ancien Dalip",
      "officialName": "Ancien Dalip",
      "provisionalName": false,
      "zone": "DLA1",
      "zoneName": "Douala I",
      "codes": 153,
      "blocks": [
        [
          100,
          409
        ]
      ]
    },
    {
      "key": "DLA1-003",
      "id": 4356,
      "plateName": "Bali",
      "officialName": "Bali",
      "provisionalName": false,
      "zone": "DLA1",
      "zoneName": "Douala I",
      "codes": 747,
      "blocks": [
        [
          11150,
          12649
        ]
      ]
    },
    "... 34 more"
  ]
}
```

An unknown arrondissement:

```sh
curl -s 'http://localhost:8080/v1/zones/XYZ'
```

Response `404`:

```json
{
  "error": {
    "code": "unknown_zone",
    "message": "There is no zone “XYZ”; see /v1/zones."
  }
}
```

## GET /v1/zones/{key}/codes?after=&limit=

The codes of an arrondissement, page by page in machine-code order: pass the `next` of a page as `after` to get the next one. `limit` is 1-1000 (default 100).

```sh
curl -s 'http://localhost:8080/v1/zones/DLA1/codes?limit=3'
```

Response `200`:

```json
{
  "zone": "DLA1",
  "codes": [
    {
      "machine": "CM-DLA1-001-1000-1",
      "home": "Akwa 1000",
      "written": "Akwa 10 00",
      "status": "provisional",
      "area": "DLA1-001",
      "entrance": {
        "lat": 4.0502109,
        "lng": 9.6960003
      },
      "officialAddress": "Rue Castelnau (N°1.378), Douala"
    },
    {
      "machine": "CM-DLA1-001-1001-7",
      "home": "Akwa 1001",
      "written": "Akwa 10 01",
      "status": "provisional",
      "area": "DLA1-001",
      "entrance": {
        "lat": 4.0503681,
        "lng": 9.6958975
      },
      "officialAddress": "Rue Castelnau (N°1.378), Douala"
    },
    {
      "machine": "CM-DLA1-001-1002-5",
      "home": "Akwa 1002",
      "written": "Akwa 10 02",
      "status": "provisional",
      "area": "DLA1-001",
      "entrance": {
        "lat": 4.051761,
        "lng": 9.6958476
      },
      "officialAddress": "Rue Boué de Lapeyrère (N° 1.382), Douala"
    }
  ],
  "count": 3,
  "next": "CM-DLA1-001-1002-5"
}
```

The next page:

```sh
curl -s 'http://localhost:8080/v1/zones/DLA1/codes?limit=3&after=CM-DLA1-001-1002-2'
```

Response `200`:

```json
{
  "zone": "DLA1",
  "codes": [
    {
      "machine": "CM-DLA1-001-1002-5",
      "home": "Akwa 1002",
      "written": "Akwa 10 02",
      "status": "provisional",
      "area": "DLA1-001",
      "entrance": {
        "lat": 4.051761,
        "lng": 9.6958476
      },
      "officialAddress": "Rue Boué de Lapeyrère (N° 1.382), Douala"
    },
    {
      "machine": "CM-DLA1-001-1003-0",
      "home": "Akwa 1003",
      "written": "Akwa 10 03",
      "status": "provisional",
      "area": "DLA1-001",
      "entrance": {
        "lat": 4.0517204,
        "lng": 9.6958753
      },
      "officialAddress": "Rue Boué de Lapeyrère (N° 1.382), Douala"
    },
    {
      "machine": "CM-DLA1-001-1004-9",
      "home": "Akwa 1004",
      "written": "Akwa 10 04",
      "status": "provisional",
      "area": "DLA1-001",
      "entrance": {
        "lat": 4.0516491,
        "lng": 9.6959423
      },
      "officialAddress": "Boulevard de la Liberté, Douala"
    }
  ],
  "count": 3,
  "next": "CM-DLA1-001-1004-9"
}
```

A limit out of range:

```sh
curl -s 'http://localhost:8080/v1/zones/DLA1/codes?limit=0'
```

Response `400`:

```json
{
  "error": {
    "code": "bad_limit",
    "message": "limit is a whole number from 1 to 1000."
  }
}
```

## GET /v1/areas/{id}

One area, by its numeric id or its key: names, blocks, its name's national range, its codes.

```sh
curl -s 'http://localhost:8080/v1/areas/4368'
```

Response `200`:

```json
{
  "key": "DLA1-015",
  "id": 4368,
  "plateName": "Bonapriso",
  "officialName": "Bonapriso",
  "provisionalName": false,
  "zone": "DLA1",
  "zoneName": "Douala I",
  "index": "015",
  "nameKey": "BONAPRISO",
  "nameId": 2616,
  "digits": 4,
  "blocks": [
    [
      1000,
      2929
    ]
  ],
  "codes": 962,
  "compoundsAtFirstIssue": 962,
  "place": {
    "lat": 4.025615,
    "lng": 9.693015
  },
  "frame": [
    9.687462,
    4.017162,
    9.69728,
    4.031143
  ],
  "alertZone": false,
  "nameRange": {
    "range": [
      1000,
      9999
    ],
    "spareFrom": 2930,
    "areas": [
      "DLA1-015"
    ]
  }
}
```

By key:

```sh
curl -s 'http://localhost:8080/v1/areas/DLA1-015'
```

Response `200`:

```json
{
  "key": "DLA1-015",
  "id": 4368,
  "plateName": "Bonapriso",
  "officialName": "Bonapriso",
  "provisionalName": false,
  "zone": "DLA1",
  "zoneName": "Douala I",
  "index": "015",
  "nameKey": "BONAPRISO",
  "nameId": 2616,
  "digits": 4,
  "blocks": [
    [
      1000,
      2929
    ]
  ],
  "codes": 962,
  "compoundsAtFirstIssue": 962,
  "place": {
    "lat": 4.025615,
    "lng": 9.693015
  },
  "frame": [
    9.687462,
    4.017162,
    9.69728,
    4.031143
  ],
  "alertZone": false,
  "nameRange": {
    "range": [
      1000,
      9999
    ],
    "spareFrom": 2930,
    "areas": [
      "DLA1-015"
    ]
  }
}
```

An unknown area:

```sh
curl -s 'http://localhost:8080/v1/areas/99999'
```

Response `404`:

```json
{
  "error": {
    "code": "unknown_area",
    "message": "There is no area “99999”."
  }
}
```

## GET /v1/areas?name=

The areas whose plate name or official name is the name given, compared by name key (accents, case, spelling variants and articles folded). The areas of one plate name share its national range, each with its own block.

```sh
curl -s 'http://localhost:8080/v1/areas?name=Adjap'
```

Response `200`:

```json
{
  "name": "Adjap",
  "total": 30,
  "areas": [
    {
      "key": "DJLO-003",
      "id": 4031,
      "plateName": "Adjap",
      "officialName": "Adjap",
      "provisionalName": false,
      "zone": "DJLO",
      "zoneName": "Oveng",
      "codes": 52,
      "blocks": [
        [
          1000,
          1109
        ]
      ]
    },
    {
      "key": "DJLO-004",
      "id": 4032,
      "plateName": "Adjap",
      "officialName": "Adjap",
      "provisionalName": false,
      "zone": "DJLO",
      "zoneName": "Oveng",
      "codes": 19,
      "blocks": [
        [
          1110,
          1149
        ]
      ]
    },
    {
      "key": "DJLS-001",
      "id": 4070,
      "plateName": "Adjap",
      "officialName": "Adjap",
      "provisionalName": false,
      "zone": "DJLS",
      "zoneName": "Sangmélima",
      "codes": 5,
      "blocks": [
        [
          1150,
          1169
        ]
      ]
    },
    "... 27 more"
  ]
}
```

An official name:

```sh
curl -s 'http://localhost:8080/v1/areas?name=Place%20du%20D%C3%A9fil%C3%A9'
```

Response `200`:

```json
{
  "name": "Place du Défilé",
  "total": 1,
  "areas": [
    {
      "key": "DLA1-031",
      "id": 4384,
      "plateName": "Douala",
      "officialName": "Place du Défilé",
      "provisionalName": true,
      "zone": "DLA1",
      "zoneName": "Douala I",
      "codes": 1136,
      "blocks": [
        [
          10000,
          12279
        ]
      ]
    }
  ]
}
```

A name no area has:

```sh
curl -s 'http://localhost:8080/v1/areas?name=Qwertyville'
```

Response `404`:

```json
{
  "error": {
    "code": "unknown_name",
    "message": "No area of Cameroon is called “Qwertyville”."
  }
}
```

No name:

```sh
curl -s 'http://localhost:8080/v1/areas'
```

Response `400`:

```json
{
  "error": {
    "code": "missing_name",
    "message": "The query parameter name is required."
  }
}
```

## POST /v1/codes

Issues a code for a new compound, or for another door of a compound (`of`). Needs `Authorization: Bearer <key>` and exists only on the designated issuer's deployment. Body: `lat`, `lng`, optionally `outline` (`[lng, lat]` points) or `of` (a machine code). The rules are those of the N-Ways issuer ([server/README.md](../server/README.md#how-issue-works)). The new code is provisional. The point must be in Cameroon, as for [`GET /v1/at`](#get-v1atlatlng): in an arrondissement outline, or in no outline but given a zone by the spot-code rule (`422 outside` otherwise). The border decides: a point more than 300 m outside the national border (OpenStreetMap, admin_level 2) is in a neighbouring country and is refused (`422 outside`), even where the spot-code rule gives it a zone ([SPEC §6.1](../engine/SPEC.md#61-inputs)).

A new compound, with its outline:

```sh
curl -s -X POST -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"lat": 4.0243022, "lng": 9.6905933, "outline": [[9.6904933, 4.0242522], [9.6906933, 4.0242522], [9.6906933, 4.0243522], [9.6904933, 4.0243522], [9.6904933, 4.0242522]]}' 'http://localhost:8080/v1/codes'
```

Response `201`:

```json
{
  "country": "CM",
  "machine": "CM-DLA1-015-2286-3",
  "home": "Bonapriso 2286",
  "written": "Bonapriso 22 86",
  "spoken": "Bonapriso, 22 86",
  "number": 2286,
  "check": 3,
  "status": "provisional",
  "issued": "on-demand",
  "issuedAt": "2026-10-21T15:04:38Z",
  "area": {
    "key": "DLA1-015",
    "id": 4368,
    "plateName": "Bonapriso",
    "officialName": "Bonapriso",
    "provisionalName": false,
    "zone": "DLA1",
    "zoneName": "Douala I"
  },
  "zone": {
    "key": "DLA1",
    "name": "Douala I",
    "nameEn": "Douala 1",
    "region": "CM-LT",
    "language": "fr",
    "index": 20
  },
  "officialAddress": null,
  "entrance": {
    "lat": 4.0243022,
    "lng": 9.6905933,
    "kind": "centre"
  },
  "spotCode": "CM-DLA1 E0450 N0268",
  "plusCode": "6FPF2MFR+P6G",
  "profile": {
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": 1,
    "floorAreaM2": 245.6,
    "rule": null,
    "estate": null
  },
  "record": {
    "machine": "CM-DLA1-015-2286-3",
    "home": "Bonapriso 2286",
    "written": "Bonapriso 22 86",
    "zone": "DLA1-015",
    "official_name": "Bonapriso",
    "number": "2286",
    "check": "3",
    "status": "provisional",
    "issued": "on-demand",
    "issued_at": "2026-10-21T15:04:38Z",
    "entrance_lat": "4.0243022",
    "entrance_lng": "9.6905933",
    "entrance_kind": "centre",
    "spot_code": "CM-DLA1 E0450 N0268",
    "official_address": "",
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": "1",
    "floor_area_m2": "245.6",
    "rule": "",
    "estate": ""
  },
  "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
}
```

The same building again:

```sh
curl -s -X POST -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"lat": 4.0243022, "lng": 9.6905933}' 'http://localhost:8080/v1/codes'
```

Response `409`:

```json
{
  "error": {
    "code": "exists",
    "message": "This building already has its code: Bonapriso 2286."
  },
  "existing": {
    "country": "CM",
    "machine": "CM-DLA1-015-2286-3",
    "home": "Bonapriso 2286",
    "written": "Bonapriso 22 86",
    "spoken": "Bonapriso, 22 86",
    "number": 2286,
    "check": 3,
    "status": "provisional",
    "issued": "on-demand",
    "issuedAt": "2026-10-21T15:04:38Z",
    "area": {
      "key": "DLA1-015",
      "id": 4368,
      "plateName": "Bonapriso",
      "officialName": "Bonapriso",
      "provisionalName": false,
      "zone": "DLA1",
      "zoneName": "Douala I"
    },
    "zone": {
      "key": "DLA1",
      "name": "Douala I",
      "nameEn": "Douala 1",
      "region": "CM-LT",
      "language": "fr",
      "index": 20
    },
    "officialAddress": null,
    "entrance": {
      "lat": 4.0243022,
      "lng": 9.6905933,
      "kind": "centre"
    },
    "spotCode": "CM-DLA1 E0450 N0268",
    "plusCode": "6FPF2MFR+P6G",
    "profile": {
      "class": "residential",
      "use": "residential",
      "kind": "building",
      "structures": 1,
      "floorAreaM2": 245.6,
      "rule": null,
      "estate": null
    },
    "record": {
      "machine": "CM-DLA1-015-2286-3",
      "home": "Bonapriso 2286",
      "written": "Bonapriso 22 86",
      "zone": "DLA1-015",
      "official_name": "Bonapriso",
      "number": "2286",
      "check": "3",
      "status": "provisional",
      "issued": "on-demand",
      "issued_at": "2026-10-21T15:04:38Z",
      "entrance_lat": "4.0243022",
      "entrance_lng": "9.6905933",
      "entrance_kind": "centre",
      "spot_code": "CM-DLA1 E0450 N0268",
      "official_address": "",
      "class": "residential",
      "use": "residential",
      "kind": "building",
      "structures": "1",
      "floor_area_m2": "245.6",
      "rule": "",
      "estate": ""
    },
    "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
    "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
  }
}
```

Another door of a compound:

```sh
curl -s -X POST -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"lat": 4.0243762, "lng": 9.6904515, "of": "CM-DLA1-015-1401-6"}' 'http://localhost:8080/v1/codes'
```

Response `201`:

```json
{
  "country": "CM",
  "machine": "CM-DLA1-015-2287-4",
  "home": "Bonapriso 2287",
  "written": "Bonapriso 22 87",
  "spoken": "Bonapriso, 22 87",
  "number": 2287,
  "check": 4,
  "status": "provisional",
  "issued": "on-demand",
  "issuedAt": "2026-10-21T15:04:38Z",
  "area": {
    "key": "DLA1-015",
    "id": 4368,
    "plateName": "Bonapriso",
    "officialName": "Bonapriso",
    "provisionalName": false,
    "zone": "DLA1",
    "zoneName": "Douala I"
  },
  "zone": {
    "key": "DLA1",
    "name": "Douala I",
    "nameEn": "Douala 1",
    "region": "CM-LT",
    "language": "fr",
    "index": 20
  },
  "officialAddress": null,
  "entrance": {
    "lat": 4.0243762,
    "lng": 9.6904515,
    "kind": "door"
  },
  "spotCode": "CM-DLA1 E0449 N0269",
  "plusCode": "6FPF2MFR+Q54",
  "profile": {
    "class": "",
    "use": "residential",
    "kind": "door",
    "structures": 0,
    "floorAreaM2": 0.0,
    "rule": null,
    "estate": null
  },
  "record": {
    "machine": "CM-DLA1-015-2287-4",
    "home": "Bonapriso 2287",
    "written": "Bonapriso 22 87",
    "zone": "DLA1-015",
    "official_name": "Bonapriso",
    "number": "2287",
    "check": "4",
    "status": "provisional",
    "issued": "on-demand",
    "issued_at": "2026-10-21T15:04:38Z",
    "entrance_lat": "4.0243762",
    "entrance_lng": "9.6904515",
    "entrance_kind": "door",
    "spot_code": "CM-DLA1 E0449 N0269",
    "official_address": "",
    "class": "",
    "use": "residential",
    "kind": "door",
    "structures": "0",
    "floor_area_m2": "0.0",
    "rule": "",
    "estate": ""
  },
  "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
}
```

A door more than 80 m from its compound:

```sh
curl -s -X POST -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"lat": 4.025289, "lng": 9.6900355, "of": "CM-DLA1-015-1401-6"}' 'http://localhost:8080/v1/codes'
```

Response `422`:

```json
{
  "error": {
    "code": "too_far",
    "message": "That door is more than 80 m from Bonapriso 1401."
  }
}
```

An outline too small for a home:

```sh
curl -s -X POST -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"lat": 4.0343022, "lng": 9.6905933, "outline": [[9.6905933, 4.0343022], [9.6906033, 4.0343022], [9.6906033, 4.0343122000000005]]}' 'http://localhost:8080/v1/codes'
```

Response `422`:

```json
{
  "error": {
    "code": "bad_outline",
    "message": "That outline is 1 m², but a home's is between 6 m² and 2 ha."
  }
}
```

Outside Cameroon:

```sh
curl -s -X POST -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"lat": 6.455, "lng": 3.394}' 'http://localhost:8080/v1/codes'
```

Response `422`:

```json
{
  "error": {
    "code": "outside",
    "message": "That point is outside Cameroon, so it cannot have a Cameroon code."
  }
}
```

Across the border, about 380 m into a neighbouring country, where the spot-code rule alone would give the point a zone:

```sh
curl -s -X POST -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"lat": 2.2082029, "lng": 9.8957734}' 'http://localhost:8080/v1/codes'
```

Response `422`:

```json
{
  "error": {
    "code": "outside",
    "message": "That point is across Cameroon's border, in a neighbouring country, so it cannot have a Cameroon code."
  }
}
```

No coordinates:

```sh
curl -s -X POST -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"lat": "x"}' 'http://localhost:8080/v1/codes'
```

Response `400`:

```json
{
  "error": {
    "code": "bad_point",
    "message": "lat and lng are numbers (WGS 84 degrees)."
  }
}
```

Without a key:

```sh
curl -s -X POST -H 'Content-Type: application/json' -d '{"lat": 4.0243022, "lng": 9.6905933}' 'http://localhost:8080/v1/codes'
```

Response `401`:

```json
{
  "error": {
    "code": "unauthorised",
    "message": "Send the issuing key as \"Authorization: Bearer <key>\"."
  }
}
```

With a key that is not one of the deployment's:

```sh
curl -s -X POST -H 'Authorization: Bearer not-a-key' -H 'Content-Type: application/json' -d '{"lat": 4.0243022, "lng": 9.6905933}' 'http://localhost:8080/v1/codes'
```

Response `401`:

```json
{
  "error": {
    "code": "unauthorised",
    "message": "That key is not one of this deployment's issuing keys."
  }
}
```

On a read-only deployment (no ISSUE_KEYS), every write is refused:

```sh
curl -s -X POST -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"lat": 4.0243022, "lng": 9.6905933}' 'http://localhost:8080/v1/codes'
```

Response `403`:

```json
{
  "error": {
    "code": "read_only",
    "message": "This deployment is read-only: it is not designated to issue codes."
  }
}
```

## PATCH /v1/codes/{machine}

Confirms a code, retires it (for good: its number is never given again), or moves its entrance to the real gate or door, at most 80 m away and never more than 300 m outside the national border (`422 outside`). Needs `Authorization: Bearer <key>`.

Confirm a code:

```sh
curl -s -X PATCH -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"status": "confirmed"}' 'http://localhost:8080/v1/codes/CM-DLA1-015-2286-3'
```

Response `200`:

```json
{
  "country": "CM",
  "machine": "CM-DLA1-015-2286-3",
  "home": "Bonapriso 2286",
  "written": "Bonapriso 22 86",
  "spoken": "Bonapriso, 22 86",
  "number": 2286,
  "check": 3,
  "status": "confirmed",
  "issued": "on-demand",
  "issuedAt": "2026-10-21T15:04:38Z",
  "area": {
    "key": "DLA1-015",
    "id": 4368,
    "plateName": "Bonapriso",
    "officialName": "Bonapriso",
    "provisionalName": false,
    "zone": "DLA1",
    "zoneName": "Douala I"
  },
  "zone": {
    "key": "DLA1",
    "name": "Douala I",
    "nameEn": "Douala 1",
    "region": "CM-LT",
    "language": "fr",
    "index": 20
  },
  "officialAddress": null,
  "entrance": {
    "lat": 4.0243022,
    "lng": 9.6905933,
    "kind": "centre"
  },
  "spotCode": "CM-DLA1 E0450 N0268",
  "plusCode": "6FPF2MFR+P6G",
  "profile": {
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": 1,
    "floorAreaM2": 245.6,
    "rule": null,
    "estate": null
  },
  "record": {
    "machine": "CM-DLA1-015-2286-3",
    "home": "Bonapriso 2286",
    "written": "Bonapriso 22 86",
    "zone": "DLA1-015",
    "official_name": "Bonapriso",
    "number": "2286",
    "check": "3",
    "status": "confirmed",
    "issued": "on-demand",
    "issued_at": "2026-10-21T15:04:38Z",
    "entrance_lat": "4.0243022",
    "entrance_lng": "9.6905933",
    "entrance_kind": "centre",
    "spot_code": "CM-DLA1 E0450 N0268",
    "official_address": "",
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": "1",
    "floor_area_m2": "245.6",
    "rule": "",
    "estate": ""
  },
  "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
}
```

Move its entrance to the gate:

```sh
curl -s -X PATCH -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"entrance": {"lat": 4.0243479, "lng": 9.6906225, "kind": "gate"}}' 'http://localhost:8080/v1/codes/CM-DLA1-015-2286-3'
```

Response `200`:

```json
{
  "country": "CM",
  "machine": "CM-DLA1-015-2286-3",
  "home": "Bonapriso 2286",
  "written": "Bonapriso 22 86",
  "spoken": "Bonapriso, 22 86",
  "number": 2286,
  "check": 3,
  "status": "confirmed",
  "issued": "on-demand",
  "issuedAt": "2026-10-21T15:04:38Z",
  "area": {
    "key": "DLA1-015",
    "id": 4368,
    "plateName": "Bonapriso",
    "officialName": "Bonapriso",
    "provisionalName": false,
    "zone": "DLA1",
    "zoneName": "Douala I"
  },
  "zone": {
    "key": "DLA1",
    "name": "Douala I",
    "nameEn": "Douala 1",
    "region": "CM-LT",
    "language": "fr",
    "index": 20
  },
  "officialAddress": null,
  "entrance": {
    "lat": 4.0243479,
    "lng": 9.6906225,
    "kind": "gate"
  },
  "spotCode": "CM-DLA1 E0451 N0269",
  "plusCode": "6FPF2MFR+P6Q",
  "profile": {
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": 1,
    "floorAreaM2": 245.6,
    "rule": null,
    "estate": null
  },
  "record": {
    "machine": "CM-DLA1-015-2286-3",
    "home": "Bonapriso 2286",
    "written": "Bonapriso 22 86",
    "zone": "DLA1-015",
    "official_name": "Bonapriso",
    "number": "2286",
    "check": "3",
    "status": "confirmed",
    "issued": "on-demand",
    "issued_at": "2026-10-21T15:04:38Z",
    "entrance_lat": "4.0243479",
    "entrance_lng": "9.6906225",
    "entrance_kind": "gate",
    "spot_code": "CM-DLA1 E0451 N0269",
    "official_address": "",
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": "1",
    "floor_area_m2": "245.6",
    "rule": "",
    "estate": ""
  },
  "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
}
```

An entrance more than 80 m away:

```sh
curl -s -X PATCH -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"entrance": {"lat": 4.0263022, "lng": 9.6905933}}' 'http://localhost:8080/v1/codes/CM-DLA1-015-2286-3'
```

Response `422`:

```json
{
  "error": {
    "code": "too_far",
    "message": "The new entrance is 218 m from the old one; it may move at most 80 m."
  }
}
```

A status that does not exist:

```sh
curl -s -X PATCH -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"status": "gone"}' 'http://localhost:8080/v1/codes/CM-DLA1-015-2286-3'
```

Response `400`:

```json
{
  "error": {
    "code": "bad_status",
    "message": "status is provisional, confirmed or retired."
  }
}
```

Retire a code:

```sh
curl -s -X PATCH -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"status": "retired"}' 'http://localhost:8080/v1/codes/CM-DLA1-015-2286-3'
```

Response `200`:

```json
{
  "country": "CM",
  "machine": "CM-DLA1-015-2286-3",
  "home": "Bonapriso 2286",
  "written": "Bonapriso 22 86",
  "spoken": "Bonapriso, 22 86",
  "number": 2286,
  "check": 3,
  "status": "retired",
  "issued": "on-demand",
  "issuedAt": "2026-10-21T15:04:38Z",
  "area": {
    "key": "DLA1-015",
    "id": 4368,
    "plateName": "Bonapriso",
    "officialName": "Bonapriso",
    "provisionalName": false,
    "zone": "DLA1",
    "zoneName": "Douala I"
  },
  "zone": {
    "key": "DLA1",
    "name": "Douala I",
    "nameEn": "Douala 1",
    "region": "CM-LT",
    "language": "fr",
    "index": 20
  },
  "officialAddress": null,
  "entrance": {
    "lat": 4.0243479,
    "lng": 9.6906225,
    "kind": "gate"
  },
  "spotCode": "CM-DLA1 E0451 N0269",
  "plusCode": "6FPF2MFR+P6Q",
  "profile": {
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": 1,
    "floorAreaM2": 245.6,
    "rule": null,
    "estate": null
  },
  "record": {
    "machine": "CM-DLA1-015-2286-3",
    "home": "Bonapriso 2286",
    "written": "Bonapriso 22 86",
    "zone": "DLA1-015",
    "official_name": "Bonapriso",
    "number": "2286",
    "check": "3",
    "status": "retired",
    "issued": "on-demand",
    "issued_at": "2026-10-21T15:04:38Z",
    "entrance_lat": "4.0243479",
    "entrance_lng": "9.6906225",
    "entrance_kind": "gate",
    "spot_code": "CM-DLA1 E0451 N0269",
    "official_address": "",
    "class": "residential",
    "use": "residential",
    "kind": "building",
    "structures": "1",
    "floor_area_m2": "245.6",
    "rule": "",
    "estate": ""
  },
  "credit": "N-Ways Addressing for Cameroon, © N-WAYS LIMITED (nways.ng)",
  "creditUrl": "https://github.com/n-ways/open-addresses-cameroon"
}
```

A retired code never comes back:

```sh
curl -s -X PATCH -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"status": "confirmed"}' 'http://localhost:8080/v1/codes/CM-DLA1-015-2286-3'
```

Response `409`:

```json
{
  "error": {
    "code": "retired",
    "message": "Bonapriso 2286 is retired; a retired code never comes back and its number is never reused."
  }
}
```

A code that does not exist:

```sh
curl -s -X PATCH -H "Authorization: Bearer $ISSUE_KEY" -H 'Content-Type: application/json' -d '{"status": "confirmed"}' 'http://localhost:8080/v1/codes/CM-DLA1-015-2929-9'
```

Response `404`:

```json
{
  "error": {
    "code": "unknown_code",
    "message": "There is no code CM-DLA1-015-2929-9."
  }
}
```
