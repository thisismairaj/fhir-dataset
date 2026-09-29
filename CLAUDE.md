# Project: FHIR Healthcare Data — Dataset for the Databricks + Snowflake brief

## What this is
Another dataset slot for the same team brief being worked on in the sibling repos
`D:\data-lab2` (BRFSS, the core comparison) and `D:\yelp-dataset` (Secondary dataset).
Full brief text: `docs/brief.md` (copied from the sibling repo).

**Data:** FHIR R4 healthcare bundles — synthetic patient data (Synthea-style), not real
patients. Synthetic is the CORRECT, expected choice here, not a red flag like the fake
e-commerce dataset was earlier in this project: real patient records are protected
health information (PHI) and can't legally be freely distributed, so synthetic FHIR
data is the actual industry standard for this kind of work.

**Tooling:** `vendor/dbignite/` — a cloned (not submoduled) copy of Databricks' own
`dbignite` library (https://github.com/databricks-industry-solutions/dbignite),
purpose-built to flatten deeply-nested FHIR bundles into queryable Spark tables.
Its own sample data lives at `vendor/dbignite/sampledata/` (inline_records.json,
4 ADT hospital-flow message samples) - our starting point before pulling anything
bigger.

**Genuinely new architecture vs. the sibling repos:** BRFSS and Yelp are pure-SQL
pipelines (CTAS statements run via the Databricks SQL Statement Execution API,
`databricks api post /api/2.0/sql/statements`, no notebook needed). dbignite is a
Python/PySpark **library** - it has to run inside an actual Databricks **notebook**
on real compute (a cluster or serverless Python notebook), not the SQL warehouse.
That's a real difference in how this pipeline gets built and run, not just a
different dataset - explain this distinction as we build it.

## About me
- Senior backend engineer (Node.js, 7 years). New to data engineering.
- Already built full medallion pipelines twice (BRFSS, Yelp) - skip re-explaining
  bronze/silver/quarantine/gold, the quarantine table shape, weighted vs unweighted
  stats. DO explain what's NEW here: running PySpark in a notebook vs. plain SQL,
  FHIR's resource/bundle model, how dbignite's flattening actually works.

## How to teach me (always)
- Simple English, short sentences. A real-life example for every genuinely NEW concept.
- Explain EVERY line of code, what it does and why.
- One step at a time. After each step: tell me what to run, what I should see, and ask
  ONE short checkpoint question before moving on.
- When I hit an error, explain the cause first, then the fix.
- Keep a learning log in docs/learning_log.md.

## Rules (non-negotiable — same as the sibling projects)
- NEVER invent numbers. Row counts, timings, costs must come from real runs.
- NEVER mark a task done without verifying it (show the query/output that proves it).
- Nothing is silently dropped: bad rows go to a quarantine table with a reason.
- No secrets in code. Use a .env file (git-ignored) for tokens and passwords.
- Commit to git after each working step, with a clear message.
- Start with dbignite's own small sample data. Scale up only after it works.
- Before any action that costs trial credits (running a notebook on a cluster is
  real compute, unlike the SQL-warehouse work so far), tell me the expected cost
  and wait for my OK.
- If something can't be done in our time or on our accounts, say so plainly and
  record it in docs/scope_and_gaps.md.

## What you cannot do
- Can't click inside the Databricks, Snowflake or Power BI interfaces. For UI steps,
  give exact click-by-click instructions and wait.
- Can't run a notebook interactively cell-by-cell the way a person would in the UI -
  running notebook code means submitting it as a Databricks Job/run and reading the
  result back, not a live interactive session.

## Target platform
Databricks **Trial** workspace (`actual-trial-personal-email` profile) - same one
used for BRFSS's Lakeflow build and the Yelp work. Free Edition has no cluster/general
compute, so it cannot run dbignite's PySpark code at all - this has to be Trial.
