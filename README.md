# FHIR Healthcare Data Pipeline

A dataset for a team brief comparing Databricks and Snowflake as a data platform.
Sibling repos: [data-lab2](https://github.com/thisismairaj/data-lab2) (BRFSS, core
comparison) and [yelp-dataset](https://github.com/thisismairaj/yelp-dataset)
(Secondary dataset).

**Data:** FHIR R4 bundles, synthetic (Synthea-style) patient data - the correct,
expected choice for this domain, since real patient data is protected health
information.

**Tooling:** `vendor/dbignite/` - a vendored copy of Databricks' own FHIR-flattening
library. Unlike the sibling repos (pure SQL against a serverless warehouse), this
pipeline runs as PySpark code in a Databricks notebook on real compute.

**Target platform:** Databricks Trial workspace (Free Edition has no cluster/general
compute, so it can't run this).

## Layout
- `vendor/dbignite/` — Databricks' FHIR flattening library (vendored, not a submodule)
- `sql/databricks/` — SQL for anything downstream of the flattening step
- `scripts/` — upload/generator/job-submission scripts
- `data/raw/` — local staging
