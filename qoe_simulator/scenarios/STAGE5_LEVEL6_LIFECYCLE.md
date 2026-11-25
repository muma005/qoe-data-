# Stage 5: Apex Level 6 lifecycle verification

Source package: `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage2_sealed_complete_20261124\target_apex_supply`; seed `0x4a9f82c1e703bd55`; engagement `STAGE4_APEX_20261124`.
Stage 4 handoff: `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage4_handoff_20261125_f`; original job `cc879ff2982646dfa50c528984ef5b5d`.
Code revision `462aefa` plus uncommitted changes; Python `3.14.3`.
Command: `python qoe_simulator/scenarios/verify_stage5_lifecycle.py --handoff 'C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage4_handoff_20261125_f' --package 'C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage2_sealed_complete_20261124\target_apex_supply' --output 'C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage5_lifecycle_20261125_d'`.
Isolated new RPC jobs: `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage5_lifecycle_20261125_d\jobs.sqlite3`. Proto unchanged.

## Observed checks

| Check | Request/action | Result | Evidence |
| --- | --- | --- | --- |
| Stored handoff | `JobStore.get; JobStore.submission` | PASS | job `cc879ff2982646dfa50c528984ef5b5d` COMPLETED; all three artifacts and trusted Apex policy match |
| Result consistency | `Stored result and event records` | PASS | 218 cells scanned, 11 check bars, 6 findings; score 65.0; no certification event |
| Professional boundary | `Policy, incomplete checks, memo, review packet` | PASS | structural_only; expert_calibration incomplete; review PENDING; no certification |
| HTTP result and memo | `GET /audit/jobs/{id}; GET /audit/jobs/{id}/memo; unknown ID` | PASS | exact durable result and memo; unknown ID 404 |
| SubmitEngagementForGrading | `gRPC, actual Stage 4 artifacts and checksum` | PASS | new durable job `a5105b5685f74931b5781183af00424e`; terminal `COMPLETED` |
| GetGradingStatus | `gRPC completed grading job` | PASS | polled statuses `['QUEUED', 'PROCESSING', 'COMPLETED']`; typed AST, scores, Benford, memo and timestamp agree with durable job |
| GenerateEQCRMemo | `gRPC completed grading job and matching engagement` | PASS | attributed memo, matching scores, pending professional review |
| RunASTFormulaAudit | `gRPC Stage 4 XLSX URI` | PASS | formula-only job `d21edf6358d84e3d89f77871f0e3ca77`; no memo, Benford result, or certification |
| ScanBenfordDistribution | `gRPC proj_gl, full ledger and category filter` | PASS | full 13142 nonzero transactions, filtered 0 for `NONEXISTENT_CATEGORY`; 9/10 digit bins |
| RPC rejection contracts | `wrong checksum, unknown job, unsupported table, wrong engagement, formula-only memo` | PASS | INVALID_ARGUMENT, NOT_FOUND, INVALID_ARGUMENT, PERMISSION_DENIED, FAILED_PRECONDITION |
| HTTP formula-only boundary | `GET /audit/jobs/{formula_job}/memo` | 409 PASS | completed AST-only job has no grading memo |
| Original job protobuf retrieval | `gRPC GetGradingStatus and GenerateEQCRMemo on workspace job` | PASS | original job `cc879ff2982646dfa50c528984ef5b5d`; score, AST and attributed memo match HTTP and stored result |
| Sealed package | `Recheck all package hashes` | PASS | 43 sealed files unchanged |

## Actual result from Stage 4 job

- Formula scan: 218 cells, 21 reproducible formulas, 11 check bars.
- Findings: 6; codes: UNSUPPORTED_ANOMALY, UNSUPPORTED_ANOMALY, UNVERIFIED_ANOMALY, UNVERIFIED_ANOMALY, UNVERIFIED_ANOMALY, SCOPE_PROTECTION.
- Composite score: 65.0; gates: `{"T01": false, "T02": false, "T03": true, "T04": true, "T05": false}`.
- Incomplete checks: `["expert_calibration"]`; institutional gate: `False`.
- Professional review: PENDING. A generated memo is an automated result, not partner sign-off.
- Grading status proto has only job_id; its contract cannot enforce engagement-specific lookup.
- The sealed policy contains no ledger account_category values; category-filter request therefore returned zero rows.
- Functional lifecycle and RPC transport PASS. No claim about realism or validity of business conclusions.
