CREATE SCHEMA IF NOT EXISTS workspace.fhir_bronze;

CREATE OR REPLACE TABLE workspace.fhir_bronze.patient_bundle AS
SELECT
  value AS raw_json,
  _metadata.file_name AS _source_file,
  current_timestamp() AS _loaded_at,
  'fhir-bronze-20260930' AS _run_id
FROM read_files(
  '/Volumes/workspace/fhir_bronze/landing/synthea_covid/',
  format => 'text',
  wholetext => true
);

SELECT count(*) FROM workspace.fhir_bronze.patient_bundle;
