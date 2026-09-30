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

## Day (2026-09-30) — pivoting to a real streaming demo, on a bigger real dataset

**The 4 bundled ADT sample files are not a "small version of something bigger" - they
are the whole thing.** They're real, complete data records (not schemas/templates),
but there are only 4 of them, period. No hidden larger dataset behind them. If a real
streaming demo needs real volume, those 4 files alone can't provide it.

**Found a genuinely large, real, free alternative: `s3://hls-eng-data-public/data/
synthea/fhir/fhir/`** - the same public bucket dbignite's own demo notebook uses.
Confirmed via `aws s3 ls --no-sign-request --summarize` (not guessed): 1,156 files,
2.08GB total. Different data shape than the 4 ADT files though - not more ADT
messages, but one full patient history bundle per file.

**One patient's FHIR bundle is not "one record" - it's ~1,200 bundled resources of
16 different types.** Checked a real file directly: 1,213 entries - 447 Observations
(lab results), 174 Claims, 131 DiagnosticReports, 98 MedicationRequests, 76
Encounters, plus Procedures/Conditions/Immunizations/CarePlans/etc., all for ONE
Patient resource. This is the real reason a generic JSON flattener isn't enough here -
a loader has to understand 16 different resource shapes mixed together in one file,
not just "parse nested JSON" in general.

**Decision: use this 2GB bucket for the streaming demo, not the 4 ADT files.** Real
volume (1,156 patients) makes "simulate patients arriving over time, process only
what's new" a genuine demonstration instead of a 4-record toy example.
