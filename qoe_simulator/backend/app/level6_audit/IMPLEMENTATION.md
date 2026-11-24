# Level 6 implementation and integration contract

The production entry point is `rubric_scorer.create_router`, mounted by the Level 5 server.
`POST /api/v1/audit/submit` queues an isolated process; GET `/jobs/{job_id}` and
`/jobs/{job_id}/memo` expose results. `/benford` scans server-owned ledger data.
The legacy `AuditEvaluationService` remains a compatibility facade and does not certify.

## Trusted scenario policy

Each scenario requires `scenarios/packages/<scenario_id>/audit_policy.json`.
The policy is server-owned; never accept it from a learner. Required fields:

- `seed_hex_64`: exact scenario seed string.
- `workbook_policy`: eleven `required_sheets`, eleven formula `check_bars`,
  trusted `check_bar_formulas` for generated packages,
  `calculation_cells`, `whole_dollar_cells`, and `pvm` records referencing
  `delta`, `price`, `volume`, and `mix` cells.
- `ledger`: ID to record mapping with `amount`, and for evidence-bearing rows,
  `cell`, `document_id`, `document_path`, `document_value`.
- `documents`: canonical document ID to JSON mapping.
- `anomalies`: ID to expected `cell`, `amount`, and nonempty `ledger_ids`.
- `replacement_costs`: records with `gross_cell`, `net_cell`, `replacement_cost`.
- `allocations`: exposure ID to mutually exclusive workbook cell references.
- `scope_gaps`: gap ID to `minimum_escrow`.
- `reconciliations`: `report_path`, `cell`, optional `display_only` records.
- `professional_checks`, `commercial_checks`, `legal_checks`, `behavior_checks`:
  explicit structured rules containing `source` (report/spa), dotted `path`, and
  `expected`, `minimum`, `maximum`, or `required` constraints.

Report anomaly claims use `anomaly_id`, `cell`, `amount`. Scope caveats use
`gap_id` and `disclosure`; SPA `escrows` use `gap_id` and `amount`.
The submission checksum is SHA256(workbook bytes + UTF-8 canonical JSON of
{"report": report, "spa": spa}), sorted keys, separators comma/colon, no NaN.

## Verification

Run from backend: `python -B -m unittest discover tests`.
Tests include OpenXML fixtures, independent recalculation, cycles, missing references,
constants, evidence disconnection, checksum tampering, worker errors, and deterministic
certification/rejection. Supported formulas include arithmetic, comparisons, references,
ranges, IF, SUM, SUMIF, SUMIFS, MIN, MAX, ABS, ROUND, AND, OR.
Unsupported formulas fail closed. Named ranges and shared/array formulas are not supported.

## Remaining design gaps

This implementation is not yet full compliance with the design document.
New compilations generate `audit_policy.json` from the workbook layout, ledger and
simulated operational sources. The checked-in target_apex_supply package has an
empty manifest and must be regenerated before grading.
Scoring uses versioned finding penalties and the verified anomaly detection ratio.
Every emitted defect category has an explicit penalty; unknown categories are rejected.
External professional calibration remains outstanding. PVM checks verify additivity,
formula-linked price/volume/mix components, and source totals from posted invoice
line allocations (or recognized contract-month units for SaaS). The SaaS
single-service measure cannot claim customer-level mix insight. Professional
checks are structured criteria, not expert review.
Job status, results and CloudEvents envelopes persist in a separate SQLite journal.
Queued and interrupted jobs replay from integrity-checked immutable submission snapshots.
Legacy jobs without saved artifacts fail explicitly. Transactional leases prevent duplicate claims across schedulers sharing a journal;
expired owners cannot commit results. The HTTP router lifespan starts periodic recovery
and stops it at shutdown. Lease duration exceeds the worker deadline.
`register_grpc_service` binds all five methods from the shared flat protobuf contract
using runtime descriptors, with trusted artifact-reader and engagement-resolver callbacks.
When `QOE_EVAL_READONLY_DSN` is set, the scenario provider loads a JSONB policy
from `audit_eval.scenario_policies` under a PostgreSQL `qoe_eval_readonly` role
inside a read-only transaction, checks mutation privileges and a canonical JSON
SHA-256 digest, and never issues application-state writes. The table contract is
`(scenario_id text, seed_hex_64 text, policy_json jsonb, policy_sha256 text)` with
unique `(scenario_id, seed_hex_64)`. Provision the role with SELECT on this table
and no mutation privileges; provide the connection string through deployment
secrets. Without a DSN, verified package policies remain the local source.
The role adapter is tested with a simulated connection; live PostgreSQL
provisioning and a live integration test need deployment credentials.
Standalone AST auditing is available
as POST `/api/v1/audit/formulas`, with a SHA-256 of decoded workbook bytes; its job never
certifies an engagement or generates an EQCR memo.
Authentication/authorization is inherited from the surrounding deployment, not provided
by this module. No production readiness or standards certification is claimed.


## Four-file ownership

- `ast_audit.py`: parser, OpenXML ingestion, dependency evaluation, formula checks,
  evidence-chain traversal, replacement-cost verification, double-dipping detection,
  and cross-schedule reconciliation.
- `benford_scanner.py`: eligible population processing and digit statistics.
- `rubric_scorer.py`: rubric policy, criterion assessment, certification,
  evaluation orchestration, isolated workers, persistence, leases, and transport adapters.
- `eqrc_memo.py`: deterministic presentation of completed assessments.

`__init__.py` only re-exports public symbols. Tests and the shared protobuf contract
remain separate. The count-based legacy facade remains non-certifying for compatibility;
both scoring entry paths use the same composite/threshold implementation.


Scenario mapping validation checks required policy sections, eleven distinct sheets,
cell coordinates, anomaly-to-ledger references, canonical document values, and positive
escrow requirements. This validates mappings; it does not invent absent mappings or
establish independent source authenticity or professional judgment calibration.

Rubric tests cover exact 80/92 boundaries, invalid counts, unknown rules, and duplicate
finding deductions. This is implementation verification, not expert calibration.


## Compiler and databook provenance integration

New compilations include private `audit_evidence.json` and `audit_policy.json`
in the package checksum.
Anomaly occurrences retain year, month and source-document reference; the exporter
links them only to actual journal lines with matching period, reference and account.
Repeated anomaly types are preserved as distinct occurrences. Each supported
occurrence has a source GL magnitude cell and linked formula cell; the policy
verifies source JSON, ledger magnitude, workbook dependency, and reported amount.
The operational documents are simulator-generated, not independently obtained
primary documents from a real company.

`Databook.audit_cell_bindings()` exposes cells from the actual exported XLSX
layout. Eleven check bars, the transaction-derived PVM values and anomaly
formula schedules use
that same grid. Every formula is recalculated; OpenXML caches are compared when
present and may be absent in a newly generated workbook.
Existing packages must be regenerated to receive compiler provenance exports.
The generated criteria are structural only, so grading reports
`expert_calibration` incomplete and T01 false. A blind partner review can only be
recorded by a trusted administrator with `QOE_REVIEW_SIGNING_KEY`; the signed
record binds a reviewer, comparison, real-deal artifact digest, verdict and
baseline policy hash. Every grade includes a review packet with artifact hashes.
No human verdict has been supplied, so actual certification remains pending.
The tests use a clearly synthetic review record to exercise the transition;
they do not demonstrate professional equivalence.
