#!/usr/bin/env python3
"""LinkedIn guest search: paginate cards, fetch JDs with backoff, gate, filter reposts."""

from __future__ import annotations

import json
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate import gate  # noqa: E402

SEARCH = (
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    "?keywords=product%20designer&geoId=103644278&f_TPR=r86400&start={start}"
)
JD_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

APPLIED_IDS = {
    "4378051109",  # PermitFlow
    "4417167197",  # OpenAI
    "4451437464",
    "4451429545",
    "4390738931",  # Crossing Hurdles
    "4440496344",  # HeartCentrix
    "4445665322",  # Chewy
    "4378368494",  # Nuvo
    "4438764462",  # LodgeLink
    "4454264141",  # Hexaware
    "4443879946",  # J.Hilburn
    "502692",  # IDR (non-li id)
    "4454283745",  # Primis
    "4452228163",  # Aaru
    "4451199451",  # Photon
    "4454277642",  # MaximaTek
    "4450820438",  # Biorce
}

REPOST_LOW_IDS = {
    "4359825226",  # FanDuel
    "4386971740",  # Fetch
    "4425670533",  # Klaviyo Senior repost
    "4426412153",  # Social Discovery Dil Mil
}


def fetch(url: str, retries: int = 5) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(2 ** attempt + 1)
                continue
            raise
        except Exception:
            if attempt < retries - 1:
                time.sleep(1 + attempt)
                continue
            raise
    return ""


def _clean_html(s: str) -> str:
    return unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or ""))).strip()


def parse_cards(html: str, page_start: int) -> list[dict]:
    cards = []
    blocks = re.split(r'data-entity-urn="urn:li:jobPosting:(\d+)"', html)[1:]
    for i in range(0, len(blocks) - 1, 2):
        job_id, block = blocks[i], blocks[i + 1]
        tm = re.search(r'base-search-card__title[^>]*>(.*?)</h3>', block, re.S)
        cm = re.search(
            r'base-search-card__subtitle[^>]*>.*?<a[^>]*>(.*?)</a>',
            block,
            re.S,
        )
        um = re.search(
            r'href="(https://www\.linkedin\.com/jobs/view/[^"?]+)',
            block,
        )
        if not (tm and um):
            continue
        cards.append(
            {
                "jobId": job_id,
                "title": _clean_html(tm.group(1)),
                "company": _clean_html(cm.group(1)) if cm else "",
                "url": unescape(um.group(1)),
                "pageStart": page_start,
            }
        )
    return cards


def fetch_jd(job_id: str) -> tuple[str, str]:
    try:
        html = fetch(JD_URL.format(job_id=job_id))
    except Exception as e:
        return "", str(e)[:200]
    m = re.search(
        r'<div class="show-more-less-html__markup[^"]*"[^>]*>(.*?)</div>',
        html,
        re.S,
    )
    if not m:
        return "", "no desc markup"
    text = unescape(re.sub(r"<[^>]+>", " ", m.group(1)))
    text = re.sub(r"\s+", " ", text).strip()
    return text, ""


def company_from_url(url: str) -> str:
    m = re.search(r"/jobs/view/[^/]+-at-([^/?]+)", url)
    if not m:
        return ""
    return unescape(m.group(1).replace("-", " ")).strip()


def repost_cutoff(ids: list[int]) -> int:
    if not ids:
        return 0
    return int(statistics.quantiles(sorted(ids), n=4)[0])


def is_repost(job_id: str, cutoff: int) -> bool:
    jid = int(job_id)
    if job_id in REPOST_LOW_IDS:
        return True
    return jid < cutoff


def harvest_cards() -> list[dict]:
    seen: dict[str, dict] = {}
    start = 0
    while start <= 950:
        html = fetch(SEARCH.format(start=start))
        cards = parse_cards(html, start)
        if not cards:
            break
        for c in cards:
            seen.setdefault(c["jobId"], c)
        print(f"start={start} +{len(cards)} total={len(seen)}", flush=True)
        start += 25
        time.sleep(0.35)
    return list(seen.values())


def main() -> int:
    import argparse
    from datetime import date

    p = argparse.ArgumentParser()
    p.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    p.add_argument("--force-refresh", action="store_true", help="Ignore card checkpoint")
    args = p.parse_args()
    day = args.date

    out_cards = Path(f"/tmp/li-{day}-cards.json")
    out_gated = Path(f"/tmp/li-{day}-gated.json")
    checkpoint = Path(f"/tmp/li-{day}-gated-partial.json")

    if out_cards.exists() and not args.force_refresh:
        cards = json.loads(out_cards.read_text())
        print(f"loaded {len(cards)} cards from checkpoint", flush=True)
    else:
        cards = harvest_cards()
        out_cards.write_text(json.dumps(cards, indent=2))
        print(f"saved {len(cards)} cards", flush=True)

    ids = [int(c["jobId"]) for c in cards]
    cutoff = repost_cutoff(ids)
    print(f"repost cutoff P25 jobId={cutoff}", flush=True)

    done: dict[str, dict] = {}
    if checkpoint.exists():
        done = {r["jobId"]: r for r in json.loads(checkpoint.read_text())}

    apply_list: list[dict] = []
    skip_list: list[dict] = []
    repost_list: list[dict] = []

    for i, c in enumerate(cards):
        jid = c["jobId"]
        if jid in done:
            rec = done[jid]
        else:
            if not c.get("company"):
                c["company"] = company_from_url(c["url"])
            desc, err = fetch_jd(jid)
            ok, reason = gate(c["title"], c["company"], desc)
            rec = {
                **c,
                "desc": desc[:8000] if desc else "",
                "desc_err": err,
                "apply": ok,
                "reason": reason,
            }
            done[jid] = rec
            time.sleep(0.55)
            if (i + 1) % 50 == 0:
                checkpoint.write_text(json.dumps(list(done.values()), indent=2))
                print(f"gated {i+1}/{len(cards)}", flush=True)

        if jid in APPLIED_IDS:
            rec = {**rec, "apply": False, "reason": "already applied (log)"}
            skip_list.append(rec)
            continue
        if is_repost(jid, cutoff):
            rec = {**rec, "apply": False, "reason": f"repost heuristic (id<{cutoff})"}
            repost_list.append(rec)
            continue
        if rec.get("apply"):
            apply_list.append(rec)
        else:
            skip_list.append(rec)

    result = {
        "date": day,
        "search": SEARCH.format(start=0),
        "total_cards": len(cards),
        "repost_cutoff": cutoff,
        "gated": len(done),
        "apply_count": len(apply_list),
        "skip_count": len(skip_list),
        "repost_count": len(repost_list),
        "apply": apply_list,
        "skipped": skip_list,
        "reposted": repost_list,
    }
    out_gated.write_text(json.dumps(result, indent=2))
    checkpoint.unlink(missing_ok=True)
    print(
        json.dumps(
            {
                "date": day,
                "total": len(cards),
                "apply": len(apply_list),
                "skip": len(skip_list),
                "repost": len(repost_list),
                "cutoff": cutoff,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
