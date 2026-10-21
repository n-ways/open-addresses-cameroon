# Contributing

Thank you for helping to improve N-Ways Addressing for Cameroon. This repository holds the specification, the reference engine, the registry, the registry server and the research paper; each kind of change has its own path.

## What can change, and how

| You want to | Do this |
|---|---|
| Report a wrong gate, a missing compound, two homes under one code or one home under two | Use "This is right / This is wrong" on the code in the N-Ways app. Corrections settle automatically by consensus of people at the compound ([GOVERNANCE.md](GOVERNANCE.md), rule 4); a pull request cannot move an issued code. |
| Propose an area's plate name or a spelling | Open an issue with the area key (`DLA1-015`), the name people say and a source (a council list, the Commission nationale de toponymie, a published map). Renames go through `model/areas/renames.json` and `tools/rename-areas.py`; respellings through `tools/respell.py`. No number, range or check digit moves. |
| Fix the engine, the server, a tool or the documents | Open a pull request (below). |
| Report a security or privacy problem | Do not open a public issue: write to hello@nways.ng ([SECURITY.md](SECURITY.md)). |

## Pull requests

1. Keep each pull request to one change, and say why it is right.
2. Run the checks, all of which must pass:
   ```sh
   python3 engine/reference/test_cm.py                  # the reference engine
   python3 -m unittest discover -s server/tests -t .    # the registry server
   ```
3. A change to the engine must keep every conformance vector in `engine/reference/vectors.json`; a change that would alter an issued code, a name id, a block or a check digit is rejected (GOVERNANCE.md, rule 1).
4. A change to the server's issue rules must keep `server/testdata/parity.json`: those values come from the N-Ways issuer itself, and every deployment must give the same answers.
5. Code uses the Python standard library only (Python 3.9 or newer), and comments say what a rule is and why it holds.
6. By contributing you agree that your contribution is licensed under the licence of the part you change ([LICENSING.md](LICENSING.md)).

## The issuer rule

Codes come from **one issuer for the whole country**. Two issuers working from the same registry would give the same free number to two different compounds. Anyone may run the server read-only; a deployment issues codes only when the State of Cameroon or N-WAYS LIMITED has designated it in writing ([server/README.md](server/README.md), "One issuer"). A pull request that makes a deployment issue without designation, or that lets two deployments issue from the same blocks, is rejected.

## Contact

N-WAYS LIMITED, hello@nways.ng, https://nways.ng
