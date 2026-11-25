# Stage 2, step 4: Apex audit policy handoff

## Decision

**PASS for the audit policy handoff.** The application's `load_scenario_policy()` accepted the Apex policy, its intended seed, and its SHA-256 checksum. The referenced ledger entries, operational evidence documents, workbook cells, report fields, and SPA field resolved. This is a structural handoff check, not a judgment about the financial conclusions or professional calibration.

## Package and identity

The corrected Stage 1 package is `qoe_simulator/scenarios/.stage1_baseline_20261124_c/target_apex_supply/`. The final sealed JSON VDR package is `qoe_simulator/scenarios/.stage2_sealed_complete_20261124/target_apex_supply/`. Both have the **identical** `audit_policy.json` SHA-256:

`ebafeb3cd5d33e6b751dc75c007df0ba97d2ea0e19cda18c92b059604b8130e8`

Both policies load as scenario `target_apex_supply` with seed `0x4a9f82c1e703bd55`. The Stage 1 manifest's integer seed equals the hexadecimal value. The baseline checksum list contains nine entries; the rebuilt package now contains 43, including all JSON VDR documents and the remaining package inputs. The policy remains at `professional_calibration: structural_only`.

## Resolution checks

| Reference | Observed check | Result |
| --- | --- | --- |
| Policy integrity | `load_scenario_policy()` succeeded; independent SHA-256 of the policy bytes equaled its `checksum.sha256` entry | Pass |
| Ledger | All 13,145 policy IDs were present in `audit_evidence.json` and in distinct `gl_transactions` rows read from the package database; signed amounts agreed at four decimal places | Pass |
| Operational documents | All three policy documents matched the three source records in `audit_evidence.json` and `vdr_artifacts/operational_source_documents.json` | Pass |
| Anomalies | Each of three policy occurrences resolved to its evidence occurrence, document ID, ledger IDs, and document field value | Pass |
| Workbook | All 44 distinct policy cell references resolved within the rendered 11-tab Databook grid; check-bar formulas and PVM source values matched | Pass |
| Report and SPA paths | Four required policy checks and three reconciliation report paths resolved in the application's assembled report/SPA structures | Pass |
| Missing-record scope | The one policy scope-gap type matched the canonical document registry's explicit missing-record type | Pass |

The PVM source value at `04_Revenue_PVM!C12` is stored as `12952687.8250` in the policy and rendered as numeric `12952687.825`. Decimal comparison confirms equality; text comparison would be misleading.

## Boundary

The loader now requires `checksum.sha256` and checks the policy and manifest hashes and identity. The Databook checks all sealed package files when reading a completed package; the compiler explicitly bypasses that check while constructing a package before its checksum file exists. Negative rejection cases are documented in step 6. The policy identifies a missing-record scope gap; this check verifies that reference is explicit and consistent, not that the missing source document exists. No financial realism or grading outcome was assessed.
