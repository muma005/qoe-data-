# Stage 1 baseline verification — Target Apex Supply

## Run definition

- Scenario: `target_apex_supply` (registered wholesale profile, NetSuite export, `SR-B01`).
- History: 3 years, January 2021 through December 2023; opening balance entries dated December 2020 are expected.
- Seed: `0x4a9f82c1e703bd55` (explicit hexadecimal; manifest stores its integer value).
- Compiler: `python qoe_simulator/scenarios/compiler/build_scenario.py --scenario target_apex_supply --years 3 --seed 0x4a9f82c1e703bd55 --output-dir <fresh-directory>`.
- Baseline after packaging fix: `.stage1_baseline_20261124_c/target_apex_supply/` and sibling `target_apex_supply_package.tar.gz`.

## Functional results

| Check | Observed result |
| --- | --- |
| Compiler exit and accounting gates | Exit 0; compiler reports INV1 and INV2 pass |
| Journal and GL counts | 6,570 journals; 13,145 GL lines; database count agrees with manifest |
| Monthly coverage | 36 consecutive trajectory months, January 2021–December 2023 |
| Required files | 18 package files plus one archive, all readable and nonempty |
| Sales and ledger linkage | Every recorded sales journal matched its revenue credit; every journal's debits equaled credits |
| Anomaly evidence | Three `SR-B01` occurrences (one each December); referenced documents and policy ledger IDs resolved |
| Package checksums | All nine selected SHA-256 checksums recomputed successfully |
| Archive | All 18 member files matched the corresponding package bytes |
| Repeatability | All 18 files matched byte for byte in two fresh runs; after fix, test also checks archive hashes match |
| Existing compiler tests | 23 tests pass, including the strengthened archive repeatability assertion |

The NetSuite CSV has 26,291 data rows. The database contains four December 2020 opening-balance lines plus 2021–2023 lines. These counts are observations, not hardcoded acceptance targets.

## Discrepancy found and fixed

Before the fix, two runs had identical contents for every package file but different `.tar.gz` hashes. Both gzip and tar headers contained run-time creation timestamps. The compiler now fixes archive metadata timestamps and identities to stable values; the existing reproducibility test also compares archive hashes. The corrected archive's SHA-256 is `2d35a903ce09e508464cd9066ab101a2004c451e70bc7f5feba8a442b6f7ba10`.

## Boundary of this result

DuckDB was not installed in this environment. The compiler used its supported SQLite fallback, stored in a file named `ground_truth.duckdb`. SQLite integrity check passed and Level 6 policy construction completed; native DuckDB output remains untested here. This stage verifies compilation and internal file consistency, not the realism of the business history or the quality of a QoE conclusion.
