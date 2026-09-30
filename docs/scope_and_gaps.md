# Scope and gaps — FHIR dataset

Status: DRAFT. Nothing measured yet - same rule as the sibling projects: numbers only
go here once they come from a real run.

## What this is, and how it relates to the other repos

The team brief (`docs/brief.md`) asks for 3 dataset shapes. `D:\data-lab2` (BRFSS)
covers the core comparison. `D:\yelp-dataset` covers Secondary (nested/semi-structured).
This repo's role in the brief is still being decided - FHIR bundles are also genuinely
nested/semi-structured (arguably an even stronger Secondary fit than Yelp, since FHIR's
own spec defines variable, optional fields per resource type), so there may be a choice
to make between the two, or a case for using both. Record that decision here once made.

## Source

- Marketplace listing `databricks_fhir_r4_synthetic_data` (Databricks Trial workspace):
  mounted but **empty** as of 2026-09-29 - only `information_schema`, no actual data
  schema. Real finding, not a check error (confirmed via SQL `SHOW SCHEMAS`, not just
  the CLI). Cause not yet known; needs checking in the Databricks UI (can't click in
  myself). Recorded as an open gap, not silently worked around.
- Working around it: `vendor/dbignite/` (Databricks' own FHIR flattening library,
  https://github.com/databricks-industry-solutions/dbignite, cloned 2026-09-29, `.git`
  stripped so it's tracked as plain files in this repo, not a submodule). Its own
  bundled sample data (`vendor/dbignite/sampledata/`) is real, synthetic FHIR data we
  can build against immediately, independent of the empty marketplace catalog.
- **Data is synthetic (Synthea-style), not real patients.** This is the correct,
  expected choice for FHIR work (real patient records are PHI, can't be freely
  distributed) - not a data-quality red flag the way the earlier fake e-commerce
  dataset was.

## Streaming source decision (2026-09-30)

The 4 ADT sample files bundled with dbignite are real, complete data records - not
schemas, not a preview of something bigger. There are only 4, period. That's fine for
proving the ADT lookup logic works, but too small to demonstrate real incremental/
streaming ingestion.

**Decision: use `s3://hls-eng-data-public/data/synthea/fhir/fhir/` instead** - the same
public bucket dbignite's own demo notebook is built around (Synthea's COVID module).
Confirmed via `aws s3 ls --no-sign-request --summarize`: **1,156 files, 2.08GB total**.
One file = one patient's full FHIR bundle (not an ADT message) - checked one directly:
1,213 entries across 16 resource types (447 Observations, 174 Claims, 131
DiagnosticReports, 98 MedicationRequests, 76 Encounters, etc.) for that single patient.

Streaming design: batched "arrival waves" (e.g. 50-100 patient files per wave),
triggering a Lakeflow pipeline update per wave rather than per file, to prove
incremental processing without 1,156 separate pipeline runs.

## Architecture difference from the sibling repos (real, not a choice)

BRFSS and Yelp are pure SQL, run via the Databricks SQL Statement Execution API
(`databricks api post /api/2.0/sql/statements`) against a serverless SQL warehouse -
no cluster, no notebook. dbignite is a Python/PySpark **library**: flattening a FHIR
bundle means running actual PySpark code in a notebook, on real compute (a cluster or
serverless Python notebook) - not something the SQL-only approach used so far can do.
This means: Free Edition (no clusters at all) cannot run this pipeline; it has to be
Trial. Running notebook code isn't a live interactive session either - it has to be
submitted as a Databricks Job/run and the result read back.

## Deviations from the brief (to fill in as we go)

| # | Brief says | What we have | Impact |
|---|-----------|--------------|--------|
| (none yet) | | | |

## Out of scope for this delivery
