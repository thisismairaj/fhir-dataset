# Learning log — FHIR dataset

Same format as the sibling repos: dated entries, 2-3 lines per new concept, written
as things are actually learned.

## Day (2026-09-29) — repo setup, dbignite

**A Marketplace listing can mount successfully but still be empty.** The
`databricks_fhir_r4_synthetic_data` catalog exists and is browsable, but has no
schema beyond `information_schema` - confirmed via SQL (`SHOW SCHEMAS`), not just a
CLI quirk. Mounting a share and having it actually deliver data are two different
steps; the gap between them isn't visible until you actually query it.

**Not every "dataset" is a table you can SELECT from - some are a library you run.**
BRFSS and Yelp are both "land raw data, then write SQL." FHIR bundles are deeply
nested (resources reference other resources, fields are optional per resource type),
so Databricks' own solution (`dbignite`) is a Python/PySpark library that flattens
the bundle programmatically, not a SQL script. That means this pipeline needs a
notebook run on real compute, not just SQL statements against a warehouse - a
genuinely different execution model from everything built so far in this project.

**Synthetic data is sometimes the *correct* choice, not a red flag.** Earlier in this
project, a synthetic e-commerce dataset was rejected for looking fake. FHIR sample
data being synthetic (Synthea-style) is different: real patient records are PHI and
legally can't be freely distributed, so synthetic is the actual industry-standard way
to work with this data shape. Same word ("synthetic"), opposite verdict - the
difference is *why* it's synthetic.
