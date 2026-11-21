# Data Dictionary: City of San Francisco Employee Compensation Register

**Source:** City and County of San Francisco Controller's Office  
**Classification:** `Real-world, Anonymized ID / Identifiable Department`  
**License:** Public Domain  

## Fields
- `organization_group_code` (INT): High-level organizational cluster code (1 to 7).
- `organization_group` (VARCHAR): Name of organizational group (e.g. `Public Protection`, `Community Health`, `Human Welfare & Neighborhood Development`).
- `department_code` (VARCHAR(3)): Department abbreviation (e.g. `POL`, `FIR`, `DPH`).
- `department` (VARCHAR): Full municipal operating department name.
- `job_family_code` (VARCHAR(4)): Labor classification code.
- `job_family` (VARCHAR): Professional labor grouping (e.g. `Information Systems`, `Nursing`, `Protection & Apprehension`).
- `job_code` (VARCHAR(6)): Official job classification code.
- `job` (VARCHAR): Specific job title.
- `employee_identifier` (INT): Unique anonymized employee tracking number.
- `salaries` (FLOAT): Base regular cash wages earned during calendar/fiscal year.
- `overtime` (FLOAT): Overtime premium compensation.
- `other_salaries` (FLOAT): Shift differentials, bonuses, longevity pay, settlement stipends.
- `total_salary` (FLOAT): Gross cash compensation (`salaries + overtime + other_salaries`).
- `retirement` (FLOAT): City employer pension contribution paid on behalf of employee.
- `health_and_dental` (FLOAT): City employer health, medical, and dental premium payments.
- `other_benefits` (FLOAT): Employer life insurance, disability, workers' compensation allocations.
- `total_benefits` (FLOAT): Sum of non-cash employment benefits (`retirement + health_and_dental + other_benefits`).
- `total_compensation` (FLOAT): Total cost of employment to the city (`total_salary + total_benefits`).
