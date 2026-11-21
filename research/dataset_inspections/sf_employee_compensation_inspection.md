# Technical Inspection Report: City of San Francisco Employee Compensation Register

**Category:** `Category 5: Payroll, Employees and Operating Structure`  
**Inspection Date:** `2026-11-12 10:51:24`  
**Originating Organization:** City and County of San Francisco Controller's Office  
**Classification:** `Real-world, Anonymized ID / Identifiable Department & Job Title`  
**License:** Open Data Policy (City of San Francisco / Public Domain)  
**Total Sample Records Inspected:** 50,000 employee records  
**Total Monitored Payroll Spend:** $6,999,928,448.48  

## 1. Schema & Field Architecture
- `organization_group` (object): High-level operational cluster (Public Protection, Community Health, Public Works).
- `department` (object): Specific operating municipal department (Police, Fire, Public Health, DPH, Airport).
- `job_family` (object): Functional labor classification.
- `job` (object): Specific official job title.
- `employee_identifier` (int64): Anonymized unique employee key.
- `salaries` (float64): Base regular salary pay.
- `overtime` (float64): Overtime premium pay.
- `other_salaries` (float64): Bonuses, shift differentials, settlement stipends.
- `total_salary` (float64): Total gross cash wages.
- `retirement` (float64): City employer pension contribution.
- `health_and_dental` (float64): Employer medical and dental insurance benefits.
- `total_benefits` (float64): Sum of non-cash employment benefits.
- `total_compensation` (float64): Total employer cash and non-cash expense.

## 2. Compensation & Benefits Loading Profile
- **Base Regular Salaries:** $4,572,664,423.47 (65.3% of total cost)
- **Overtime Premiums:** $467,250,320.39 (6.7% of total cost)
- **Other Incentive / Shift Pay:** $264,466,262.08 (3.8% of total cost)
- **Total Cash Wages:** $5,304,381,005.94
- **Retirement Contributions:** $691,597,352.69
- **Health & Dental Benefits:** $681,599,440.31
- **Total Benefits Package:** $1,695,547,442.54
- **Benefits Loading Factor:** `31.97%` of base cash wages.

## 3. Forensic Labor & Overtime Anomalies
- **Overtime Loading Ratio:** `8.81%` of gross cash salary is paid out as overtime.
- **Extreme Overtime Outliers (>50% of Total Salary):** `255` employees earn over 50% of their total cash compensation purely in overtime premiums.
- **Negative Compensation / Adjustment Records:** `2` records representing retroactive wage clawbacks, benefit adjustments, or payroll correction journals.

## 4. Top Departmental Cost Drivers
```
department
Public Health                    1.635915e+09
Municipal Transportation Agcy    9.224602e+08
Police                           7.201077e+08
Public Utilities Commission      4.975223e+08
Fire Department                  4.697763e+08
```

## 5. QoE Quality of Earnings Applications
1. **Fringe Benefits Loading Normalization:** In middle-market carve-outs or acquisitions, target companies often underestimate the true burden of employer payroll taxes, healthcare, and pension contributions. This dataset establishes empirical evidence for a `32.0%` benefit loading factor.
2. **Overtime Normalization Add-Back / Adjustment:** Identifies structural staffing shortages where reliance on expensive overtime premiums should be normalized to standard full-time equivalent (FTE) headcount costs.
3. **Headcount & Run-Rate Wage Bridges:** Supports building the QoE bridge between historical payroll register expense and forward run-rate labor cost under post-acquisition operational structures.
