# Stage 4: Apex deliverable handoff verification

Package: `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage2_sealed_complete_20261124\target_apex_supply`. Scenario: `target_apex_supply`. Seed: `0x4a9f82c1e703bd55`. Engagement: `STAGE4_APEX_20261124`.
Code revision: `462aefa` plus uncommitted changes. Python: `3.14.3`.
Command: `python qoe_simulator/scenarios/verify_stage4_deliverables.py --package 'C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage2_sealed_complete_20261124\target_apex_supply' --output 'C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage4_handoff_20261125_f'`.
Isolated workspace and Level 6 job stores: `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage4_handoff_20261125_f`. Sealed files: 43.

## Artifact inventory

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage4_handoff_20261125_f\apex_databook.xlsx` | 16,301 | `abe97279507e2a40d010f1d6c76b9f7595bd82dcc509cf80dfef0de072f07f52` |
| `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage4_handoff_20261125_f\apex_report.json` | 6,608 | `40dfb1d2adf0ed13d47226b7c5b178452519a0ed8e99c17229fa4b904c6262a8` |
| `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage4_handoff_20261125_f\apex_spa_exhibit_b.json` | 888 | `c2517b034c97fcf48668a07e797570543a489a3ea0f9073ffc6b208514bec1ad` |

## Observed operations

| Operation | Request/action | Result | Evidence |
| --- | --- | --- | --- |
| Package preflight | `verify_package_integrity` | PASS | 43 sealed files; checksum manifest SHA-256 `c19a9dbc4519d7c4f47e3f4dc83bf7105119aca5e2f54c8b07c7820b6928a329` |
| Workbook export | `Databook.build; XLSXSerializer.serialize; reopen XLSX` | PASS | 11 sheets and 11 check-bar formulas; 164 rendered cells matched |
| Report assembly | `POST /api/v1/workspace/report/assemble` | 200 PASS | 10 sections; exact response equals builder output for selected Databook |
| SPA assembly | `POST /api/v1/workspace/spa/exhibit-b` | 200 PASS | six required fields; target peg and net debt agree with report and builder |
| Package binding | `POST /report/assemble with unrelated directory` | 409 PASS | Caller cannot substitute an unrelated package |
| Checksum rejection | `POST /deliverables/compile with incorrect checksum` | 200 FAIL RESPONSE | CLIENT_CHECKSUM_MISMATCH; no Level 6 job |
| Queue failure rejection | `POST /deliverables/compile without seed` | 200 FAIL RESPONSE | AUDIT_SUBMISSION_FAILED; no false success or placeholder job |
| Deliverable submission | `POST /api/v1/workspace/deliverables/compile` | 200 PASS | submission `SUB_000003`; real job `cc879ff2982646dfa50c528984ef5b5d` |
| Level 6 receipt | `GET /api/v1/audit/jobs/cc879ff2982646dfa50c528984ef5b5d; JobStore.submission` | 200 PASS | engagement `STAGE4_APEX_20261124`; scenario and seed match; status `QUEUED`; all submitted artifacts match |
| Background worker settlement | `EvaluationJobs.wait(30); JobStore.get` | COMPLETED | job `cc879ff2982646dfa50c528984ef5b5d`; error `` |
| Package after submission | `verify_package_integrity` | PASS | All sealed hashes still match |

## Submission and checksum contracts

- Workspace checksum (SHA-256 of base64 text): `254cb25989701c2b2bc76c7aa1a78f2326166f0bac270b2651c212201cf77bd6`.
- Workbook bytes SHA-256: `abe97279507e2a40d010f1d6c76b9f7595bd82dcc509cf80dfef0de072f07f52`.
- Level 6 checksum: SHA-256 of workbook bytes plus compact, sorted JSON of `report` and `spa`; the server computes this from the submitted sanitized JSON.
- Submission `SUB_000003` yielded durable job `cc879ff2982646dfa50c528984ef5b5d` for `STAGE4_APEX_20261124`.
- The job state shown above was observed during handoff; terminal evaluation is assessed in Stage 5.
- The proto was unchanged. The report and SPA endpoints accept `package_dir`; bound workspace rejects a different directory.
- Functional handoff PASS. No business realism, financial correctness, or certification conclusion is inferred.
