"""FHIR streaming simulation, Lakeflow Declarative Pipelines way (the YAML one,
databricks_bundle/). Releases the 1,156 already-loaded Synthea bundle files in
4 waves of 289 each into a fresh, initially-empty UC Volume folder
(`streaming_landing/`), then triggers a real pipeline update per wave via
`databricks bundle run`.

Wave 1: copy 289 files, deploy the bundle, then trigger the pipeline's first
update (initial load). Waves 2-4: copy the next 289 files, trigger another
update - Auto Loader (inside CREATE OR REFRESH STREAMING TABLE) tracks which
files it already saw, so each update should only ingest the newly-arrived
files, not reprocess earlier waves.

Proof: row_count grows 289 -> 578 -> 867 -> 1156 across 4 separate pipeline
updates, exactly matching the known source file count, never jumping straight
there in one update.

File copies run in parallel (ThreadPoolExecutor) since each is a separate CLI
subprocess call - 1,156 of them serially would be the real wall-clock cost.
"""
import subprocess, sys, time, os
from concurrent.futures import ThreadPoolExecutor, as_completed

PROFILE = "actual-trial-personal-email"
TARGET = "dev"
PIPELINE_KEY = "fhir_stream_pipeline"
MASTER = "dbfs:/Volumes/workspace/fhir_bronze/landing/synthea_covid"
# A folder INSIDE the existing `landing` volume, sibling to synthea_covid/ - not
# a separate volume of its own. A bare 4th path segment under /Volumes/<catalog>/
# <schema>/ has to be a real Volume object; "streaming_landing" isn't one, and
# mkdir on it fails with a real, non-obvious error - caught by checking mkdir's
# exit code below instead of discarding it silently.
STREAM_LANDING = "dbfs:/Volumes/workspace/fhir_bronze/landing/streaming_landing"
STREAM_TABLE = f"workspace.fhir_lakeflow_{TARGET}.patient_bundle_stream"
WAVE_SIZE = 289  # 1156 / 4, exact
COPY_WORKERS = 12
HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE_DIR = os.path.join(HERE, "..", "databricks_bundle")
DB_RUN = os.path.join(HERE, "db_run.py")


def list_master_files():
    r = subprocess.run(["databricks", "fs", "ls", MASTER + "/", "-p", PROFILE],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return sorted(l.strip() for l in r.stdout.splitlines() if l.strip())


def copy_one(fn):
    src, dst = f"{MASTER}/{fn}", f"{STREAM_LANDING}/{fn}"
    r = subprocess.run(["databricks", "fs", "cp", src, dst, "-p", PROFILE],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return fn, r.returncode == 0, r.stderr.strip()


def copy_wave(files):
    ok, failed = 0, []
    with ThreadPoolExecutor(max_workers=COPY_WORKERS) as ex:
        futs = [ex.submit(copy_one, fn) for fn in files]
        for i, fut in enumerate(as_completed(futs), 1):
            fn, success, err = fut.result()
            ok += success
            if not success:
                failed.append((fn, err))
            if i % 50 == 0 or i == len(files):
                print(f"   ...{i}/{len(files)} copied ({ok} ok, {len(failed)} failed)", flush=True)
    if failed:
        print(f"   FAILURES ({len(failed)}):")
        for fn, err in failed[:10]:
            print(f"     {fn}: {err}")
    return ok, failed


def bundle_deploy():
    print("=== Deploying bundle ===", flush=True)
    r = subprocess.run(["databricks", "bundle", "deploy", "-t", TARGET, "-p", PROFILE,
                         "--auto-approve"], cwd=BUNDLE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout)
    if r.returncode != 0:
        print("DEPLOY STDERR:", r.stderr)
        raise RuntimeError("bundle deploy failed")


def bundle_run_pipeline():
    r = subprocess.run(["databricks", "bundle", "run", PIPELINE_KEY, "-t", TARGET, "-p", PROFILE],
                        cwd=BUNDLE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout)
    if r.returncode != 0:
        print("RUN STDERR:", r.stderr)
    return r.returncode == 0


def query_row_count():
    r = subprocess.run([sys.executable, DB_RUN, f"SELECT count(*) AS row_count FROM {STREAM_TABLE};"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout)
    return r.stdout


def main():
    files = list_master_files()
    print(f"Master file count: {len(files)}")
    waves = [files[i:i + WAVE_SIZE] for i in range(0, len(files), WAVE_SIZE)]
    print(f"{len(waves)} waves, sizes {[len(w) for w in waves]}\n")

    r = subprocess.run(["databricks", "fs", "mkdir", STREAM_LANDING, "-p", PROFILE],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        # Not fatal if it already exists from a prior run; fatal otherwise.
        if "already exists" not in (r.stderr or "") and "RESOURCE_ALREADY_EXISTS" not in (r.stderr or ""):
            raise RuntimeError(f"mkdir {STREAM_LANDING} failed: {r.stderr.strip()}")
        print(f"(streaming_landing already exists, continuing)")

    bundle_deploy()

    for idx, wave in enumerate(waves, 1):
        print(f"\n=== Wave {idx}/{len(waves)}: copying {len(wave)} files ===", flush=True)
        t0 = time.perf_counter()
        ok, failed = copy_wave(wave)
        t_copy = time.perf_counter() - t0
        print(f"Wave {idx} copy: {ok}/{len(wave)} ok in {t_copy:.1f}s", flush=True)

        print(f"=== Wave {idx}: triggering pipeline update ===", flush=True)
        t1 = time.perf_counter()
        success = bundle_run_pipeline()
        t_run = time.perf_counter() - t1
        print(f"Wave {idx} pipeline update: {'OK' if success else 'FAILED'} in {t_run:.1f}s", flush=True)

        query_row_count()

    print("\nDone. Expected final row_count: 1156 (verify against the last wave's output above).")


if __name__ == "__main__":
    main()
