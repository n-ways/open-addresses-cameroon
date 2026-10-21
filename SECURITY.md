# Security and privacy

## Reporting a problem

Write to **hello@nways.ng** with "Security" in the subject. Please include what you found, where (a file, an endpoint, a code), how to reproduce it and what it could allow. Do not open a public issue for a vulnerability or for anything that exposes a person.

We acknowledge a report within three working days, keep you informed while we fix it, and credit you when the fix is published if you wish.

## What counts

- A way to issue, change or retire codes on a deployment without one of its issuing keys, or to exceed its daily limit.
- A way to make the server answer with data that is not in its registry, to corrupt its database, or to stop it with a small request.
- A registry row, a document or a log that reveals anything about a person: who lives at a compound, who confirmed a code, a phone or device identifier. The registry describes places only; a row that says more is a defect.
- A code that leads somewhere unsafe because its entrance is wrong in a way the in-app correction cannot fix.

## Requests about a home

A household that wants its compound shown only as "residential", or that believes its code puts it at risk, can ask N-Ways at hello@nways.ng. A code is never withdrawn or reused, but what is shown about the compound can be reduced.

## Deployments

The server speaks plain HTTP: run it behind a TLS proxy and keep its port closed to the outside ([server/README.md](server/README.md)). Issuing keys are secrets: never commit them, give each office its own, and revoke a key by removing it from `ISSUE_KEYS`.
