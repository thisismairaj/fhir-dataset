CREATE SCHEMA IF NOT EXISTS workspace.fhir_gold;

CREATE OR REPLACE TABLE workspace.fhir_gold.fact_patient AS
SELECT
  patient_id, gender, birth_date,
  floor(datediff(current_date(), birth_date) / 365.25) AS age_years,  -- age as of today, not as of data generation - real caveat
  family_name, given_name, city, state, marital_status
FROM workspace.fhir_silver.patient_clean;

SELECT count(*) FROM workspace.fhir_gold.fact_patient;   -- expect 1154

-- Real finding: age distribution by decade
SELECT floor(age_years/10)*10 AS age_decade, gender, count(*) AS patient_count
FROM workspace.fhir_gold.fact_patient
GROUP BY age_decade, gender
ORDER BY age_decade, gender;

SELECT state, count(*) AS patient_count FROM workspace.fhir_gold.fact_patient
GROUP BY state ORDER BY patient_count DESC LIMIT 10;
