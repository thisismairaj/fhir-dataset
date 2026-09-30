-- Silver for FHIR patient demographics, extracted via direct SQL get_json_object -
-- fast because Patient is exactly 1-per-bundle with simple top-level fields. This is
-- the honest limit of the SQL-only approach though: race/ethnicity live inside a
-- generic "extension" array matched by URL, and Condition/Encounter/Observation are
-- many-per-patient with deeply variable shape - that's the real reason dbignite (a
-- proper library, not ad hoc JSON-path SQL) exists, not solved here.

CREATE SCHEMA IF NOT EXISTS workspace.fhir_silver;

CREATE OR REPLACE TABLE workspace.fhir_silver._staged_patient AS
SELECT
  get_json_object(raw_json, '$.entry[0].resource.resourceType') AS resource_type,
  get_json_object(raw_json, '$.entry[0].resource.id')           AS patient_id,
  get_json_object(raw_json, '$.entry[0].resource.gender')       AS gender,
  get_json_object(raw_json, '$.entry[0].resource.birthDate')    AS birth_date,
  get_json_object(raw_json, '$.entry[0].resource.name[0].family') AS family_name,
  get_json_object(raw_json, '$.entry[0].resource.name[0].given[0]') AS given_name,
  get_json_object(raw_json, '$.entry[0].resource.address[0].city')  AS city,
  get_json_object(raw_json, '$.entry[0].resource.address[0].state') AS state,
  get_json_object(raw_json, '$.entry[0].resource.maritalStatus.text') AS marital_status,
  _source_file, _run_id
FROM workspace.fhir_bronze.patient_bundle;

CREATE OR REPLACE TABLE workspace.fhir_silver.patient_quarantine AS
SELECT patient_id AS record_id, 'fhir_patient' AS dataset_id, _run_id AS run_id,
  CASE WHEN resource_type != 'Patient' THEN 'BAD_ASSUMPTION' ELSE 'Q1' END AS rule_id,
  'quarantine' AS severity,
  to_json(named_struct('resource_type', resource_type, 'patient_id', patient_id, '_source_file', _source_file)) AS raw_payload,
  'entry[0] was not a Patient resource, or patient_id/birth_date missing' AS reason,
  'new' AS status, CAST(NULL AS STRING) AS resolved_by
FROM workspace.fhir_silver._staged_patient
WHERE resource_type != 'Patient' OR patient_id IS NULL OR birth_date IS NULL;

CREATE OR REPLACE TABLE workspace.fhir_silver.patient_clean AS
SELECT patient_id, gender, birth_date, family_name, given_name, city, state, marital_status, _run_id
FROM workspace.fhir_silver._staged_patient
WHERE resource_type = 'Patient' AND patient_id IS NOT NULL AND birth_date IS NOT NULL;

SELECT (SELECT count(*) FROM workspace.fhir_silver.patient_clean) AS clean,
       (SELECT count(*) FROM workspace.fhir_silver.patient_quarantine) AS quarantined,
       (SELECT count(*) FROM workspace.fhir_bronze.patient_bundle) AS bronze_rows;

SELECT gender, count(*) FROM workspace.fhir_silver.patient_clean GROUP BY gender;
