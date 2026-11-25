# Stage 2, step 5: package-wide checksum verification

## Inputs and method

- Stage 1 baseline: `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage1_baseline_20261124_c\target_apex_supply`
- Rebuilt handoff: `C:\Users\ADMIN\Desktop\QOE  data aquisition\qoe_simulator\scenarios\.stage2_sealed_complete_20261124\target_apex_supply`
- Expected scenario: `target_apex_supply`; seed: `0x4a9f82c1e703bd55`.
- Parsed the compiler's `SHA-256  relative/path` lines; rejected unsafe and duplicate paths.
- Streamed each existing file's bytes through SHA-256; compared with its recorded digest.
- Compared the original nine paths and hashes across packages and checked VDR catalog coverage.
- The verification did not modify either package.

## Observed results

| Check | Observed |
| --- | --- |
| Baseline sealed files | 9/9 matching |
| Rebuilt sealed files | 43/43 matching |
| Shared original files | 9 paths compared |
| Catalog coverage | 25 document paths; catalog itself sealed |
| Package files outside checksum list | 1 (named below) |
| Overall step 5 | PASS |

## Rebuilt package: each listed file

| Listed path | Bytes | Recorded SHA-256 | Calculated SHA-256 | Result |
| --- | ---: | --- | --- | --- |
| `ground_truth.duckdb` | 2,084,864 | `eece040dc698d6bd4d18b22876266cb4b0335303471fc83a7a8f901f05058b78` | `eece040dc698d6bd4d18b22876266cb4b0335303471fc83a7a8f901f05058b78` | PASS |
| `manifest.json` | 320 | `52aa3a7ca62e3df0ce4e3d1d400902a8b698acfb8f62d15e6159c63d5b4cb17c` | `52aa3a7ca62e3df0ce4e3d1d400902a8b698acfb8f62d15e6159c63d5b4cb17c` | PASS |
| `operational_trajectory.json` | 24,799 | `655040b7e607d66572fc071c78a627efa983d1082d989a8e7e92c21c327c4641` | `655040b7e607d66572fc071c78a627efa983d1082d989a8e7e92c21c327c4641` | PASS |
| `injected_anomalies.json` | 2,071 | `695b910b26c530dc0557df44a589893984e7594a3a83244128391da45acd6cba` | `695b910b26c530dc0557df44a589893984e7594a3a83244128391da45acd6cba` | PASS |
| `sales_lines.json` | 1,022,626 | `a81393b10c0c2188f90589a5533bf509a2fdc7aa2aaf149db99a3bed773ab046` | `a81393b10c0c2188f90589a5533bf509a2fdc7aa2aaf149db99a3bed773ab046` | PASS |
| `audit_evidence.json` | 4,419,248 | `6621fa067056595f0b97227b3c47f6326774813c4df572e38f2f81749a0f5854` | `6621fa067056595f0b97227b3c47f6326774813c4df572e38f2f81749a0f5854` | PASS |
| `audit_policy.json` | 848,070 | `ebafeb3cd5d33e6b751dc75c007df0ba97d2ea0e19cda18c92b059604b8130e8` | `ebafeb3cd5d33e6b751dc75c007df0ba97d2ea0e19cda18c92b059604b8130e8` | PASS |
| `vdr_artifacts/operational_source_documents.json` | 708 | `bad088886d6252542df552ae5bcfcdfa20f57fdd392842f34e24a762a3eee3e8` | `bad088886d6252542df552ae5bcfcdfa20f57fdd392842f34e24a762a3eee3e8` | PASS |
| `vdr_artifacts/product_sales_lines.json` | 1,022,626 | `a81393b10c0c2188f90589a5533bf509a2fdc7aa2aaf149db99a3bed773ab046` | `a81393b10c0c2188f90589a5533bf509a2fdc7aa2aaf149db99a3bed773ab046` | PASS |
| `entity_ledger.json` | 14,205 | `ba397181c8f824bb49dae0e29e9f408aae572c7bb5a80bc07978c41529a9731b` | `ba397181c8f824bb49dae0e29e9f408aae572c7bb5a80bc07978c41529a9731b` | PASS |
| `sku_inventory.json` | 144 | `cc9a63d092aaa167e0b47d9de2445292e65b8bf2bc0437a0b9bf19f2b3ba45e1` | `cc9a63d092aaa167e0b47d9de2445292e65b8bf2bc0437a0b9bf19f2b3ba45e1` | PASS |
| `subledgers.json` | 1,147 | `3fd32700279d09fcb7e2f4739962c9ec1e49ae72c318e7d58843d0655eee33c6` | `3fd32700279d09fcb7e2f4739962c9ec1e49ae72c318e7d58843d0655eee33c6` | PASS |
| `vdr_artifacts/canonical_documents.json` | 2,302 | `afb0fab5ae42aae044a7cb92896f085d98b285f262354de120ea9592bf99acd5` | `afb0fab5ae42aae044a7cb92896f085d98b285f262354de120ea9592bf99acd5` | PASS |
| `vdr_artifacts/aged_ar_schedule.csv` | 136 | `c29a022484e7fd18c07719cc21464b9785cca2974ab3e6517e53d7d629cc834f` | `c29a022484e7fd18c07719cc21464b9785cca2974ab3e6517e53d7d629cc834f` | PASS |
| `vdr_artifacts/cutoff_break_schedule.csv` | 123 | `fa3988c27f0ecf538184f69d185689f647ed838986bdda43ab00e737e933fe07` | `fa3988c27f0ecf538184f69d185689f647ed838986bdda43ab00e737e933fe07` | PASS |
| `vdr_artifacts/erp_exports/netsuite_gl.csv` | 2,038,383 | `32a8d799870f3947c7d88599cdcc106fdf6fa96b2131d74b28fdc232a16ec0da` | `32a8d799870f3947c7d88599cdcc106fdf6fa96b2131d74b28fdc232a16ec0da` | PASS |
| `vdr_artifacts/working_capital_schedule.csv` | 229 | `6db81858694b940218fc2b79e868d0189b0f9d1069bd9ca27ad32a08082e0441` | `6db81858694b940218fc2b79e868d0189b0f9d1069bd9ca27ad32a08082e0441` | PASS |
| `vdr_artifacts/json/entity_master.json` | 14,205 | `ba397181c8f824bb49dae0e29e9f408aae572c7bb5a80bc07978c41529a9731b` | `ba397181c8f824bb49dae0e29e9f408aae572c7bb5a80bc07978c41529a9731b` | PASS |
| `vdr_artifacts/json/operational_trajectory.json` | 24,799 | `655040b7e607d66572fc071c78a627efa983d1082d989a8e7e92c21c327c4641` | `655040b7e607d66572fc071c78a627efa983d1082d989a8e7e92c21c327c4641` | PASS |
| `vdr_artifacts/json/erp_general_ledger.json` | 3,773,681 | `82f3db616499d42e29e08f3719c0a6ffb1b6e7852e1227ccfb1321e405e17723` | `82f3db616499d42e29e08f3719c0a6ffb1b6e7852e1227ccfb1321e405e17723` | PASS |
| `vdr_artifacts/json/aged_ar_schedule.json` | 395 | `c54cc78cd0ee58900444c09d1ec0ea05f830d918ef91b0b793cabefbea89a688` | `c54cc78cd0ee58900444c09d1ec0ea05f830d918ef91b0b793cabefbea89a688` | PASS |
| `vdr_artifacts/json/subledgers.json` | 1,147 | `3fd32700279d09fcb7e2f4739962c9ec1e49ae72c318e7d58843d0655eee33c6` | `3fd32700279d09fcb7e2f4739962c9ec1e49ae72c318e7d58843d0655eee33c6` | PASS |
| `vdr_artifacts/json/sku_inventory.json` | 144 | `cc9a63d092aaa167e0b47d9de2445292e65b8bf2bc0437a0b9bf19f2b3ba45e1` | `cc9a63d092aaa167e0b47d9de2445292e65b8bf2bc0437a0b9bf19f2b3ba45e1` | PASS |
| `vdr_artifacts/json/working_capital_schedule.json` | 536 | `6d8c42b1b1f490f23c1505e7551737329f9cce0d03d4d36102e34392012ddb6e` | `6d8c42b1b1f490f23c1505e7551737329f9cce0d03d4d36102e34392012ddb6e` | PASS |
| `vdr_artifacts/json/cutoff_break_schedule.json` | 176 | `dd3c8143654f1ee108b348bf1ee4e2d647cd2032a15201aec2c6ac7144d97065` | `dd3c8143654f1ee108b348bf1ee4e2d647cd2032a15201aec2c6ac7144d97065` | PASS |
| `vdr_artifacts/json/product_sales_lines.json` | 1,022,626 | `a81393b10c0c2188f90589a5533bf509a2fdc7aa2aaf149db99a3bed773ab046` | `a81393b10c0c2188f90589a5533bf509a2fdc7aa2aaf149db99a3bed773ab046` | PASS |
| `vdr_artifacts/json/operational_source_documents.json` | 624 | `9c36bc3dcf0272844564bcf9ff7838d7b6f95bb3df70526ba1970bcf058d7471` | `9c36bc3dcf0272844564bcf9ff7838d7b6f95bb3df70526ba1970bcf058d7471` | PASS |
| `vdr_artifacts/json/corporate_identity.json` | 430 | `d046b3c4da55b611b7abea0a8c5cd1a5f321312d9deeeb02bf014b501a937e48` | `d046b3c4da55b611b7abea0a8c5cd1a5f321312d9deeeb02bf014b501a937e48` | PASS |
| `vdr_artifacts/json/board_minutes_register.json` | 898 | `c088f4aff7c966be38db1eb60ad11ff837b62fb96a9560fc99f331a2c0f5b0cc` | `c088f4aff7c966be38db1eb60ad11ff837b62fb96a9560fc99f331a2c0f5b0cc` | PASS |
| `vdr_artifacts/json/litigation_register.json` | 413 | `dd3cc8c764be137bb27fb330f49419412a961d79d7d5b93b8df09bbcdc152ae1` | `dd3cc8c764be137bb27fb330f49419412a961d79d7d5b93b8df09bbcdc152ae1` | PASS |
| `vdr_artifacts/json/annual_financial_statements.json` | 841 | `4c597a88ea094efff2126120ef6314b4cd3b7fccdfac6091916d6a5fb7fbc140` | `4c597a88ea094efff2126120ef6314b4cd3b7fccdfac6091916d6a5fb7fbc140` | PASS |
| `vdr_artifacts/json/cash_reconciliation_register.json` | 8,400 | `7a422a084c7d52e54b6612d83cc1395181fa7a4cc431b10d264bce3c4a4b6259` | `7a422a084c7d52e54b6612d83cc1395181fa7a4cc431b10d264bce3c4a4b6259` | PASS |
| `vdr_artifacts/json/federal_tax_register.json` | 832 | `aaa5f80eaade8d215bf97b60fb564050a78aed36324fc36cae1e3c13fe846134` | `aaa5f80eaade8d215bf97b60fb564050a78aed36324fc36cae1e3c13fe846134` | PASS |
| `vdr_artifacts/json/state_apportionment_register.json` | 358 | `56b5649454b3db7d0f765d35a77ffd5e5c268712a5094f3a95d0ee9c83c27dfc` | `56b5649454b3db7d0f765d35a77ffd5e5c268712a5094f3a95d0ee9c83c27dfc` | PASS |
| `vdr_artifacts/json/sales_tax_correspondence.json` | 384 | `5ac1a2b2c7707ee65c36ebfef9535be6bb7fd74614817665ae90829c80616443` | `5ac1a2b2c7707ee65c36ebfef9535be6bb7fd74614817665ae90829c80616443` | PASS |
| `vdr_artifacts/json/customer_agreement_register.json` | 2,156 | `48938e9a8350e25fa0f2278a31ef1bbc6aaa186d00f4f5b06cc1e27e6a98794b` | `48938e9a8350e25fa0f2278a31ef1bbc6aaa186d00f4f5b06cc1e27e6a98794b` | PASS |
| `vdr_artifacts/json/customer_churn_credit_activity.json` | 409 | `4b1a87b27fdb8ea86f0b0ca285ff316174fd60483f97228f1342aaaec737cfc3` | `4b1a87b27fdb8ea86f0b0ca285ff316174fd60483f97228f1342aaaec737cfc3` | PASS |
| `vdr_artifacts/json/facility_lease_register.json` | 12,033 | `f4c6d9f57478e5479dddf6f9e7010468614343cd5c9cfcc95cf6bb9bf1fbdd20` | `f4c6d9f57478e5479dddf6f9e7010468614343cd5c9cfcc95cf6bb9bf1fbdd20` | PASS |
| `vdr_artifacts/json/product_bom_register.json` | 972 | `aa00976d36d34d9da9523da66ae80cf32fbe8f1c6a0805a0d5377018cd9ec1b1` | `aa00976d36d34d9da9523da66ae80cf32fbe8f1c6a0805a0d5377018cd9ec1b1` | PASS |
| `vdr_artifacts/json/employee_census_register.json` | 44,395 | `7fc282e742e960228ddf29ff6e0f07d13921351cc9c7498ae4b19258325ac367` | `7fc282e742e960228ddf29ff6e0f07d13921351cc9c7498ae4b19258325ac367` | PASS |
| `vdr_artifacts/json/executive_employment_register.json` | 986 | `cbfe0c06c7772f0a83b4ca48be017dc171f42d2105ac3320fde8471fd31ca31b` | `cbfe0c06c7772f0a83b4ca48be017dc171f42d2105ac3320fde8471fd31ca31b` | PASS |
| `vdr_artifacts/json/owner_expense_register.json` | 556 | `ce24396b9a58964db53fcff3d1cb7c5688120eb6a9b1e6358118a8a52f5396a9` | `ce24396b9a58964db53fcff3d1cb7c5688120eb6a9b1e6358118a8a52f5396a9` | PASS |
| `vdr_artifacts/json/catalog.json` | 5,189 | `3afe0e7e9c27af317f82cd858755d6d44f9ef80690deeff7176709f53086e29c` | `3afe0e7e9c27af317f82cd858755d6d44f9ef80690deeff7176709f53086e29c` | PASS |

## Stage 1 baseline: each listed file

| Listed path | Bytes | Recorded SHA-256 | Calculated SHA-256 | Result |
| --- | ---: | --- | --- | --- |
| `ground_truth.duckdb` | 2,084,864 | `eece040dc698d6bd4d18b22876266cb4b0335303471fc83a7a8f901f05058b78` | `eece040dc698d6bd4d18b22876266cb4b0335303471fc83a7a8f901f05058b78` | PASS |
| `manifest.json` | 320 | `52aa3a7ca62e3df0ce4e3d1d400902a8b698acfb8f62d15e6159c63d5b4cb17c` | `52aa3a7ca62e3df0ce4e3d1d400902a8b698acfb8f62d15e6159c63d5b4cb17c` | PASS |
| `operational_trajectory.json` | 24,799 | `655040b7e607d66572fc071c78a627efa983d1082d989a8e7e92c21c327c4641` | `655040b7e607d66572fc071c78a627efa983d1082d989a8e7e92c21c327c4641` | PASS |
| `injected_anomalies.json` | 2,071 | `695b910b26c530dc0557df44a589893984e7594a3a83244128391da45acd6cba` | `695b910b26c530dc0557df44a589893984e7594a3a83244128391da45acd6cba` | PASS |
| `sales_lines.json` | 1,022,626 | `a81393b10c0c2188f90589a5533bf509a2fdc7aa2aaf149db99a3bed773ab046` | `a81393b10c0c2188f90589a5533bf509a2fdc7aa2aaf149db99a3bed773ab046` | PASS |
| `audit_evidence.json` | 4,419,248 | `6621fa067056595f0b97227b3c47f6326774813c4df572e38f2f81749a0f5854` | `6621fa067056595f0b97227b3c47f6326774813c4df572e38f2f81749a0f5854` | PASS |
| `audit_policy.json` | 848,070 | `ebafeb3cd5d33e6b751dc75c007df0ba97d2ea0e19cda18c92b059604b8130e8` | `ebafeb3cd5d33e6b751dc75c007df0ba97d2ea0e19cda18c92b059604b8130e8` | PASS |
| `vdr_artifacts/operational_source_documents.json` | 708 | `bad088886d6252542df552ae5bcfcdfa20f57fdd392842f34e24a762a3eee3e8` | `bad088886d6252542df552ae5bcfcdfa20f57fdd392842f34e24a762a3eee3e8` | PASS |
| `vdr_artifacts/product_sales_lines.json` | 1,022,626 | `a81393b10c0c2188f90589a5533bf509a2fdc7aa2aaf149db99a3bed773ab046` | `a81393b10c0c2188f90589a5533bf509a2fdc7aa2aaf149db99a3bed773ab046` | PASS |

## Discrepancies

None in the checks above.

## Package files not named in the checksum list

- `checksum.sha256`

## Scope

This confirms the files listed in the checksum manifests, not every file in either package. The checksum file itself cannot practically include its own hash. In the rebuilt package, all other package files are now listed and checked. It does not assess source realism or prove that an external document exists. Negative rejection cases belong to Stage 2 step 6. The sibling `.tar.gz` archive is outside these checksum lists.
