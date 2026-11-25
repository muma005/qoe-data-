# Stage 3: Apex workspace interaction verification

Package: `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage2_sealed_complete_20261124\target_apex_supply`; scenario `target_apex_supply`; seed `0x4a9f82c1e703bd55`.
Code revision: `462aefa` plus uncommitted Stage 2/3 changes. Python `3.14.3`, FastAPI `0.136.0`, workspace API `1.0.0`.
Package checksum manifest SHA-256: `c19a9dbc4519d7c4f47e3f4dc83bf7105119aca5e2f54c8b07c7820b6928a329`. Engagement: `STAGE3_APEX_20261124`; user: `USR_STAGE3_ANALYST`.
Command: `python qoe_simulator/scenarios/verify_stage3_workspace.py --package qoe_simulator/scenarios/.stage2_sealed_complete_20261124/target_apex_supply --report qoe_simulator/scenarios/STAGE3_WORKSPACE_VERIFICATION.md`.
State database was created in a disposable directory outside the sealed package.

## Diagnosed and repaired before the final run

- IRL submissions existed only in a service instance; there was no retrieval route. A SQLite-backed store and engagement-scoped GET route now persist and retrieve inquiries.
- State sync previously acknowledged input without saving it. Signed sync now stores the tab and document state; a signed retrieval route returns it after restart.
- Search previously returned stale `is_locked` flags. It now computes the flag from the server clock.
- The first storage test exposed SQLite connections left open on Windows. The store now closes each connection, including failure paths. No proto field or RPC was edited.

| Operation | Request or action | Response | Observed result |
| --- | --- | --- | --- |
| Initial VDR tree | `POST /vdr/tree (client day 20)` | 200 | 6 folders, 25 documents, 20 locked; server day 1 |
| Release boundary | `POST /vdr/document before day 14` | 403 | VDR_NODE_019 denied on day 1 |
| Unknown document | `POST /vdr/document unknown ID` | 404 | No document returned |
| Search | `POST /vdr/search mixed case and no-match` | 200 / 200 | Found VDR_NODE_009 locked on day 1; no-match returned [] |
| Clock unlock | `Clock events to days 14 and 20` | 200 | Day-14 document opened; all 25 documents unlocked by day 20 |
| Document retrieval | `POST /vdr/document for each cataloged ID` | 25 x 200 | 25 valid JSON payloads; MIME, size, SHA-256, source bytes and hidden-field checks matched |
| Information request | `POST /irl/submit; GET /irl/{id}` | 404 / 200 / 200 | Invalid citation rejected; IRL_REQ_0001 saved and retrieved for STAGE3_APEX_20261124 |
| Workspace state | `POST /state/sync; POST /state/get` | 200 / 200 / 403 | Signed state round-tripped; wrong signature rejected |
| Service restart | `New WorkspaceGatewayService with the same state DB` | 200 / 200 | Inquiry IRL_REQ_0001 and active tab 2 survived restart |
| Databook | `POST /databook/tabs and /databook/tab x11` | 12 x 200 / 404 | All 11 named tabs returned nonempty data; unknown tab rejected |
| Package unchanged | `Rehash package after HTTP run` | PASS | 43 sealed files valid; selected source hashes unchanged |

## Submitted and retrieved inquiry

- Engagement `STAGE3_APEX_20261124`, request `IRL_REQ_0001`, cited VDR document `VDR_NODE_019`.
- Subject: `Rebate source terms`. Body: `Please reconcile the cited rebate source terms with the journal reference.`.
- The retrieved inquiry, including its initial thread and citation, equaled the submitted response both before and after a new service instance opened the same state store.

## Synchronized and retrieved state

- User `USR_STAGE3_ANALYST`, active tab index `2`, active document `VDR_NODE_019`.
- `03_Income_Statement` active cell `B4`, scroll row `2`, scroll column `1`, check bar flag `true`. The stored tab state matched after service restart.

## Every retrieved VDR document

| ID | JSON title | Delivered bytes | Delivered SHA-256 |
| --- | --- | ---: | --- |
| `VDR_NODE_007` | `Entity_Master.json` | 14,205 | `ba397181c8f824bb49dae0e29e9f408aae572c7bb5a80bc07978c41529a9731b` |
| `VDR_NODE_017` | `Corporate_Identity_and_Bylaws_Register.json` | 430 | `d046b3c4da55b611b7abea0a8c5cd1a5f321312d9deeeb02bf014b501a937e48` |
| `VDR_NODE_018` | `Board_Minutes_Register.json` | 898 | `c088f4aff7c966be38db1eb60ad11ff837b62fb96a9560fc99f331a2c0f5b0cc` |
| `VDR_NODE_019` | `Litigation_and_Claims_Register.json` | 413 | `dd3cc8c764be137bb27fb330f49419412a961d79d7d5b93b8df09bbcdc152ae1` |
| `VDR_NODE_008` | `Operational_Trajectory.json` | 24,799 | `655040b7e607d66572fc071c78a627efa983d1082d989a8e7e92c21c327c4641` |
| `VDR_NODE_009` | `ERP_General_Ledger.json` | 3,773,681 | `82f3db616499d42e29e08f3719c0a6ffb1b6e7852e1227ccfb1321e405e17723` |
| `VDR_NODE_010` | `Aged_AR_Schedule.json` | 395 | `c54cc78cd0ee58900444c09d1ec0ea05f830d918ef91b0b793cabefbea89a688` |
| `VDR_NODE_011` | `Subledgers.json` | 1,147 | `3fd32700279d09fcb7e2f4739962c9ec1e49ae72c318e7d58843d0655eee33c6` |
| `VDR_NODE_012` | `SKU_Inventory.json` | 144 | `cc9a63d092aaa167e0b47d9de2445292e65b8bf2bc0437a0b9bf19f2b3ba45e1` |
| `VDR_NODE_013` | `Working_Capital_Schedule.json` | 536 | `6d8c42b1b1f490f23c1505e7551737329f9cce0d03d4d36102e34392012ddb6e` |
| `VDR_NODE_014` | `Cutoff_Break_Schedule.json` | 176 | `dd3c8143654f1ee108b348bf1ee4e2d647cd2032a15201aec2c6ac7144d97065` |
| `VDR_NODE_020` | `Annual_Financial_Statements.json` | 841 | `4c597a88ea094efff2126120ef6314b4cd3b7fccdfac6091916d6a5fb7fbc140` |
| `VDR_NODE_021` | `Cash_Ledger_and_Bank_Reconciliation_Register.json` | 8,400 | `7a422a084c7d52e54b6612d83cc1395181fa7a4cc431b10d264bce3c4a4b6259` |
| `VDR_NODE_022` | `Federal_Tax_Return_Source_Register.json` | 832 | `aaa5f80eaade8d215bf97b60fb564050a78aed36324fc36cae1e3c13fe846134` |
| `VDR_NODE_023` | `State_Apportionment_Source_Register.json` | 358 | `56b5649454b3db7d0f765d35a77ffd5e5c268712a5094f3a95d0ee9c83c27dfc` |
| `VDR_NODE_024` | `Sales_Tax_Correspondence_Register.json` | 384 | `5ac1a2b2c7707ee65c36ebfef9535be6bb7fd74614817665ae90829c80616443` |
| `VDR_NODE_015` | `Product_Sales_Lines.json` | 1,022,626 | `a81393b10c0c2188f90589a5533bf509a2fdc7aa2aaf149db99a3bed773ab046` |
| `VDR_NODE_025` | `Customer_Agreement_Register.json` | 2,156 | `48938e9a8350e25fa0f2278a31ef1bbc6aaa186d00f4f5b06cc1e27e6a98794b` |
| `VDR_NODE_026` | `Customer_Churn_and_Credit_Activity.json` | 409 | `4b1a87b27fdb8ea86f0b0ca285ff316174fd60483f97228f1342aaaec737cfc3` |
| `VDR_NODE_016` | `Operational_Source_Documents.json` | 624 | `9c36bc3dcf0272844564bcf9ff7838d7b6f95bb3df70526ba1970bcf058d7471` |
| `VDR_NODE_027` | `Facility_Rent_and_Lease_Register.json` | 12,033 | `f4c6d9f57478e5479dddf6f9e7010468614343cd5c9cfcc95cf6bb9bf1fbdd20` |
| `VDR_NODE_028` | `Product_Units_and_BOM_Register.json` | 972 | `aa00976d36d34d9da9523da66ae80cf32fbe8f1c6a0805a0d5377018cd9ec1b1` |
| `VDR_NODE_029` | `Payroll_and_Employee_Census_Register.json` | 44,395 | `7fc282e742e960228ddf29ff6e0f07d13921351cc9c7498ae4b19258325ac367` |
| `VDR_NODE_030` | `Executive_Employment_Register.json` | 986 | `cbfe0c06c7772f0a83b4ca48be017dc171f42d2105ac3320fde8471fd31ca31b` |
| `VDR_NODE_031` | `Owner_Expense_Attribution_Register.json` | 556 | `ce24396b9a58964db53fcff3d1cb7c5688120eb6a9b1e6358118a8a52f5396a9` |

## Every loaded Databook tab

| Tab | Top-level fields |
| --- | ---: |
| `01_Summary` | 5 |
| `02_EBITDA_Bridges` | 7 |
| `03_Income_Statement` | 7 |
| `04_Revenue_PVM` | 2 |
| `05_Gross_Margin` | 6 |
| `06_OPEX_Detail` | 5 |
| `07_Working_Capital` | 12 |
| `08_Net_Debt` | 7 |
| `09_Cash_Flow_Capex` | 7 |
| `10_Debt_Like_Items` | 4 |
| `11_SPA_Exhibit_B` | 5 |

## Regression checks

- Focused Stage 3 tests: 2 passed, including restart persistence and access rejection.
- Level 5 workspace tests: 70 passed. Level 6 tests: 40 passed. `git diff --check`: passed.

**Stage 3 result: PASS.** Every operation above returned the expected response. The run exercised HTTP routes with FastAPI TestClient, not a visual browser session. It verifies workspace behavior and artifact handoff, not the realism of financial data or QoE conclusions.
