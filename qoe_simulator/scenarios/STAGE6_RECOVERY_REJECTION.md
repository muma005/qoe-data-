# Stage 6: Apex recovery and rejection verification

Source package: `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage2_sealed_complete_20261124\target_apex_supply`. Scenario `target_apex_supply`, seed `0x4a9f82c1e703bd55`. Original Stage 4 job `cc879ff2982646dfa50c528984ef5b5d`.
Code revision `462aefa` plus uncommitted changes; Python `3.14.3`.
Command: `python qoe_simulator/scenarios/verify_stage6_recovery.py --package 'C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage2_sealed_complete_20261124\target_apex_supply' --handoff 'C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage4_handoff_20261125_f' --output 'C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage6_recovery_20261125_a'`.
All mutations and job stores were isolated under `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage6_recovery_20261125_a`. Sealed package checksum SHA-256 `c19a9dbc4519d7c4f47e3f4dc83bf7105119aca5e2f54c8b07c7820b6928a329`.

## Observed faults and recovery

| Check | Request or fault | Result | Evidence |
| --- | --- | --- | --- |
| Workspace checksum | `POST /workspace/deliverables/compile, wrong base64 checksum` | REJECTED | HTTP 200 failure body; CLIENT_CHECKSUM_MISMATCH; zero jobs; no success event |
| Workspace wrong seed | `POST /workspace/deliverables/compile, changed seed` | REJECTED | HTTP 200 failure body; AUDIT_SUBMISSION_FAILED; seed mismatch; zero jobs |
| Audit HTTP checksum and seed | `POST /audit/submit twice with incorrect inputs` | REJECTED | both HTTP 400; no job persisted |
| Protobuf checksum | `SubmitEngagementForGrading with checksum` | INVALID_ARGUMENT | typed rejection; no job persisted |
| Protobuf seed | `SubmitEngagementForGrading with seed` | INVALID_ARGUMENT | typed rejection; no job persisted |
| Protobuf missing workbook URI | `SubmitEngagementForGrading with missing workbook URI` | NOT_FOUND | typed rejection; no job persisted |
| Missing sealed package file | `Disposable copy without ground_truth.duckdb` | REJECTED | Databook and policy loader reject; no empty replacement database |
| Damaged workbook | `Audit submit with bad XLSX and valid recomputed checksum` | FAILED | job `10aab93fd59e4551af1ebec7c659ad86` states ['QUEUED', 'PROCESSING', 'FAILED']; error `File is not a zip file`; memo 409; no certification |
| Queued restart | `Persisted valid QUEUED job; new EvaluationJobs service` | COMPLETED | job `stage6_queued_replay` states ['QUEUED', 'PROCESSING', 'COMPLETED']; stored artifacts used; one start event; review PENDING |
| Missing persisted payload | `QUEUED record with absent submissions row; restart` | FAILED | EVALUATION_INTERRUPTED: immutable artifacts unavailable |
| Tampered persisted payload | `Alter workbook blob without changing stored checksum; restart` | FAILED | Stored submission integrity failure |
| Competing owners | `Two services open same QUEUED job; stale write` | PASS | one start event; terminal COMPLETED; owner `046a26fa3d94410fabdff67d466d2b89`; other owner fenced |
| Interrupted processing service | `Terminate isolated PID after PROCESSING; restart; natural lease expiry` | COMPLETED | PID 26156; job `22050bee67b646e08e76c713de4ac405`; restart states ['PROCESSING', 'COMPLETED']; recovered in 61.5s; two starts (original and replay), no certification |
| Original controls | `Rehash sealed package; compare original Stage 4 job and events` | PASS | 43 files and original completed job unchanged |

## Boundaries

- The workspace returns HTTP 200 with a failure body for rejected deliverables. Both fields and absence of a job were checked.
- The damaged workbook used a valid newly computed checksum, reaching the worker rather than merely failing the checksum test.
- The interrupted child was terminated by its captured PID after the job entered PROCESSING. Its live lease prevented immediate duplicate replay; the new service recovered after natural expiry.
- The grade gate stayed closed because professional calibration remains pending. This is functional recovery evidence, not a QoE conclusion.
- Proto and sealed Apex package were unchanged.
