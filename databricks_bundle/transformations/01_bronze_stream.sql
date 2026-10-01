-- Lakeflow Declarative Pipeline: streaming bronze for the FHIR bundle set.
-- CREATE OR REFRESH STREAMING TABLE watches the /Volumes/workspace/fhir_bronze/
-- landing/streaming_landing/ FOLDER (a new folder inside the existing `landing`
-- volume, sibling to synthea_covid/ - not a separate volume of its own) via
-- Auto Loader - on every pipeline update it only ingests files it hasn't seen before
-- (tracked via an internal checkpoint), never reprocessing earlier waves.
--
-- This is the wave test: scripts/stream_waves.py releases the 1,156 known
-- Synthea bundle files into this folder in 4 waves of 289. Wave 1 lands before
-- the pipeline's first update (so its update does the initial load); waves 2-4
-- land between later updates. Expected row_count after each update:
-- 289 -> 578 -> 867 -> 1156 - proving incremental ingestion, not one big batch.
--
-- Same read shape as the static bronze table (sql/databricks/01_bronze_patient_bundle.sql):
-- each file is one pretty-printed JSON document, not JSONL, so wholetext => true
-- is required to get one row per FILE.
CREATE OR REFRESH STREAMING TABLE patient_bundle_stream
COMMENT 'FHIR patient bundles, one row per source file, ingested incrementally as files arrive in the landing folder.'
AS
SELECT
  value                 AS raw_json,
  _metadata.file_name   AS _source_file,
  current_timestamp()   AS _loaded_at
FROM STREAM read_files(
  '/Volumes/workspace/fhir_bronze/landing/streaming_landing/',
  format => 'text',
  wholetext => true
);
