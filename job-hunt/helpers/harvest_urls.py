#!/usr/bin/env python3
"""Open LinkedIn guest job pages and extract offsite apply URLs. One browser."""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate import gate  # noqa: E402

DONE = {
    "openai",
    "permitflow",
    "babylist",
    "imc",
    "wispr",
}
KNOWN = {
    "allegis group": "https://careers-allegisgroup.icims.com/jobs/2368/ux-designer/job",
    "target": "https://corporate.target.com/jobs/w28/85/senior-ux-product-designer-stores",
}


def main() -> int:
    jobs = json.loads(Path("/tmp/li-jobs-75-detail.json").read_text())
    apply = []
    skipped = []
    seen = set()
    for j in jobs:
        key = (j["company"].lower(), j["title"].lower())
        if key in seen:
            continue
        seen.add(key)
        ok, reason = gate(j["title"], j["company"], j.get("desc") or "")
        rec = {
            "jobId": j["jobId"],
            "title": j["title"],
            "company": j["company"],
            "url": j["url"],
            "reason": reason,
        }
        if not ok:
            skipped.append(rec)
            continue
        if any(d in j["company"].lower() for d in DONE):
            rec["status"] = "already-logged"
            skipped.append(rec)
            continue
        apply.append(rec)

    t0 = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            channel="chrome",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page()
        for rec in apply:
            slug = rec["company"].split(" -")[0].strip().lower()
            if slug in KNOWN:
                rec["applyUrl"] = KNOWN[slug]
                rec["host"] = "known"
                continue
            try:
                page.goto(rec["url"], wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(600)
                hrefs = page.evaluate(
                    """() => {
                      const out = [];
                      document.querySelectorAll('a[href]').forEach(a => {
                        const h = a.href || '';
                        const t = (a.innerText || a.getAttribute('data-tracking-control-name') || '');
                        if (/apply|ashby|greenhouse|lever|workday|icims|myworkdayjobs|smartrecruiters|jobvite|greenhouse.io/i.test(h+t))
                          out.push(h);
                      });
                      return [...new Set(out)];
                    }"""
                )
                rec["hrefs"] = hrefs[:8]
                offsite = [
                    h
                    for h in hrefs
                    if not re.search(r"linkedin\.com", h)
                    and re.search(
                        r"ashby|greenhouse|lever|workday|icims|smartrecruiters|careers|jobs\.",
                        h,
                        re.I,
                    )
                ]
                rec["applyUrl"] = offsite[0] if offsite else (KNOWN.get(slug) or "")
            except Exception as e:
                rec["error"] = str(e)[:200]
            print(rec["company"][:28], rec.get("applyUrl") or rec.get("error") or rec.get("hrefs", [])[:2], flush=True)
        browser.close()
    out = {"seconds": round(time.time() - t0, 1), "apply": apply, "skipped": skipped}
    Path("/tmp/remaining-apply.json").write_text(json.dumps(out, indent=2))
    Path("/workspace/job-hunt/helpers/remaining_apply.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"n_apply": len(apply), "seconds": out["seconds"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
