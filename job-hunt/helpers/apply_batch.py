#!/usr/bin/env python3
"""Run ats_autofill.py against jobs_queue.json and write /tmp/batch-results.json."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILLER = ROOT / "ats_autofill.py"
QUEUE = ROOT / "jobs_queue.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", default=str(QUEUE))
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    jobs = json.loads(Path(args.queue).read_text())
    if args.only:
        want = args.only.lower()
        jobs = [j for j in jobs if want in j.get("company", "").lower()]
    results = []
    t0 = time.time()
    for job in jobs:
        cmd = [sys.executable, str(FILLER), "--url", job["url"], "--company", job["company"]]
        if args.submit:
            cmd.append("--submit")
        print(f"\n=== {job['company']}  {job.get('role','')} ===", flush=True)
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        raw = p.stdout.strip()
        try:
            data = json.loads(raw[raw.rfind("{") :])
        except Exception:
            data = {"company": job["company"], "parse_error": True, "stdout": raw[-800:], "stderr": p.stderr[-400:]}
        data["exit"] = p.returncode
        data["role"] = job.get("role")
        results.append(data)
        print(json.dumps({k: data.get(k) for k in ("company", "seconds", "submitted", "already_applied", "need_code", "exit")}, indent=2), flush=True)
        if p.stderr:
            print(p.stderr[-300:], file=sys.stderr)
    out = {"seconds": round(time.time() - t0, 1), "results": results}
    Path("/tmp/batch-results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"batch_seconds": out["seconds"], "n": len(results)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
