# FHIR Healthcare Data Pipeline

A dataset for the team brief being worked on in the sibling repos `D:\data-lab2`
(BRFSS, core comparison) and `D:\yelp-dataset` (Secondary dataset). See
`docs/brief.md` for the full brief and `docs/scope_and_gaps.md` for what's actually
built vs. what's still open.

**Data:** FHIR R4 bundles, synthetic (Synthea-style) patient data - the correct,
expected choice for this domain, since real patient data is protected health
information.

**Tooling:** `vendor/dbignite/` - a vendored copy of Databricks' own FHIR-flattening
library. Unlike the sibling repos (pure SQL against a serverless warehouse), this
pipeline runs as PySpark code in a Databricks notebook on real compute.

**Target platform:** Databricks Trial workspace (Free Edition has no cluster/general
compute, so it can't run this).

## Layout
- `docs/` — brief, scope/gaps, learning log
- `vendor/dbignite/` — Databricks' FHIR flattening library (vendored, not a submodule)
- `sql/databricks/` — SQL for anything downstream of the flattening step
- `scripts/` — upload/generator/job-submission scripts
- `data/raw/` — local staging (git-ignored, not committed)
