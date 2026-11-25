# Stage 2 VDR handoff repair and verification

## Package

`qoe_simulator/scenarios/.stage2_sealed_complete_20261124/target_apex_supply/`

Compiled with scenario `target_apex_supply`, 3 years, and seed `0x4a9f82c1e703bd55`. The server selects this package with `QOE_SCENARIO_PACKAGE_DIR` set to that directory.

## Repair

- The compiler writes 25 sealed JSON VDR records and a sealed catalog. The 15 categories that previously had no backing file now have source-linked records derived from package data. Original CSV data remains in the package for existing internal consumers.
- The VDR tree uses the catalog. Existing answer-key files are excluded.
- Public JSON source references point to the sealed ledger document rather than the server-side ground-truth store.
- Document retrieval returns `application/json` in `canonical_json_payload`; `download_signed_url` is empty. The unchanged proto uses its existing unspecified node type for JSON documents.
- The client renders JSON as text. It does not interpret document content as HTML.
- The gateway uses its server clock for both the tree's lock state and document access.

## Checks completed

| Check | Result |
| --- | --- |
| Application HTTP tree and document route | 25 documents opened; six folders present |
| Delivered JSON content | All 25 payloads parsed and matched their source JSON files |
| Tree metadata | All 25 displayed sizes and SHA-256 digests matched delivered bytes |
| Supplemental source links | All 15 records linked to existing package source files |
| Unknown document | HTTP 404 |
| Package checksums | All 43 package data files sealed; all 43 listed hashes matched |
| Archive | All 44 package files present in the archive |
| Level 6 policy loader | Accepted the rebuilt package; `structural_only` calibration |
| Level 5 tests | 70 passed |
| Level 6 tests | 40 passed |
| Level 2 compiler tests | 24 passed, including three-sector checks of all 15 supplemental records and their source consistency |
| Frontend TypeScript | `npx tsc -b` passed |

The Vite production build could not read its config path in this sandbox, so that build is unverified. This package used the SQLite fallback under the `.duckdb` filename. All 15 supplemental JSON records are present, open, and source-linked for the simulated package. They intentionally state `source_derived_external_verification_pending`: a ledger can support a cash activity register, for example, but cannot prove a bank statement was issued; likewise it cannot prove an audit opinion, tax filing, signed agreement, or employee identity. These external facts are outside the simulator's modeled source data and are not fabricated.
