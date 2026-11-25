# Stage 2, step 6: disposable-package rejection verification

## Run definition

The source is `qoe_simulator/scenarios/.stage2_sealed_complete_20261124/target_apex_supply/`, three years, seed `0x4a9f82c1e703bd55`. Each mutation was made to a fresh temporary copy. The source checksum, manifest, audit policy, and ledger hashes were compared before and after the initial diagnostic run and were unchanged. Follow-up automated tests compile their own two-year Apex fixture and make isolated copies.

The intact final source passed a fresh integrity check of 43 data files; `load_scenario_policy()` loaded its 13,145 ledger bindings, `Databook.build()` produced 11 tabs, and the VDR tree contained 25 documents.

## What the first diagnostic exposed

| Experiment on a disposable copy | First observation | Final behavior |
| --- | --- | --- |
| No mutation | Policy loaded | All application readers and package integrity pass |
| Add a byte to sealed `audit_policy.json` | Policy checksum mismatch | Rejected with policy checksum mismatch |
| Add a byte to cataloged `entity_master.json` | VDR document checksum mismatch | Rejected by VDR |
| Add a byte to sealed `operational_trajectory.json` | Policy loader accepted it; package verifier caught the changed hash in the later diagnostic | Policy loader, Databook, and package verifier now reject it |
| Remove `audit_policy.json` | File-not-found failure | File-not-found failure |
| Remove cataloged `entity_master.json` | VDR file-not-found failure | VDR file-not-found failure |
| Remove `ground_truth.duckdb` | **Databook returned successfully and created an empty replacement database** | Rejected before opening a database; no replacement file created |
| Remove `subledgers.json` | File-not-found failure, but the Databook left the database connection open on Windows | Rejected as missing sealed input; connection is closed on error |
| Place package under another scenario directory | Code inspection showed the loader did not compare the requested ID with the manifest; first diagnostic was interrupted by the open connection before this case | Rejected with scenario identifier mismatch |
| Request a wrong seed | Code inspection showed policy seed checking; first diagnostic was interrupted before this case | Rejected with scenario seed mismatch |
| Alter manifest seed without resealing | Code inspection showed no manifest validation; first diagnostic was interrupted before this case | Rejected with manifest checksum mismatch |
| Change manifest seed **and reseal its hash** | Not part of first diagnostic | Rejected on the actual manifest seed mismatch |
| Remove `checksum.sha256` | Code inspection showed the policy loader skipped the hash when the file was absent; first diagnostic was interrupted before this case | Rejected because the checksum manifest is required |
| Add a byte to `subledgers.json` | Old 35-entry verifier passed and Databook built 11 tabs because that input was unsealed | New 43-entry verifier, policy loader, and Databook reject the altered file |

The initial run stopped after the missing-subledgers case because its open database connection prevented temporary-directory cleanup on Windows. The follow-up test verifies the connection is released by renaming the database after the failure.

## Repairs

1. The compiler now lists all 43 package data files in `checksum.sha256`, including `subledgers.json`, `entity_ledger.json`, the canonical document registry, and the source CSV files. Only `checksum.sha256` itself is unlisted. The new package and sibling archive were rebuilt from the same Apex scenario and seed.
2. `ReadProjectionsDB` supports read-only opening of an existing ledger. The Databook uses it and closes the connection on every error path.
3. The Databook verifies every listed package file before reading a finished package. The compiler explicitly skips this preseal check while constructing its policy before the checksum file exists.
4. The policy loader now requires the checksum file, checks both the policy and manifest hashes, compares the manifest scenario ID and seed with the request, and verifies the entire sealed package.
5. Existing Level 6 HTTP test fixtures were given a manifest and checksum rather than bypassing the stricter loader.

The proto was not edited. The original Stage 1 baseline package was not rewritten.

## Final checks

| Check | Result |
| --- | --- |
| Dedicated disposable-copy rejection tests | 10 passed |
| New final Apex package SHA-256 entries | 43/43 match |
| Baseline original SHA-256 entries | 9/9 match; all nine agree with the rebuilt package |
| Final package application load | 43 sealed files accepted; 11 Databook tabs, 13,145 policy ledger bindings, 25 VDR documents |
| Level 2 compiler tests | 24 passed |
| Level 5 tests | 70 passed |
| Database projection tests | 2 passed |
| Level 4 tests | 69 passed |
| Level 6 tests | 40 passed |

## Boundary

The checker protects package data **relative to the checksum file supplied with the package**. It is not an external signature or proof against an attacker who can replace both data and checksum together. These tests establish rejection behavior and internal consistency, not realism of financial results or authenticity of external legal and tax documents.
