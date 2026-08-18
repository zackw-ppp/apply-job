#!/usr/bin/env python3
"""Gate a LinkedIn job title + JD snippet. Exit 0 = apply, 1 = skip.

  python3 gate.py --title "Product Designer" --company PermitFlow --jd-file /tmp/jd.txt
"""

from __future__ import annotations

import argparse
import json
import re
import sys

ROLE_OK = re.compile(
    r"\b(product designer|product engineer|ux designer|ui/ux|ui ux|ux/ui|"
    r"user experience designer|product design engineer|design engineer)\b",
    re.I,
)
PHYSICAL = re.compile(
    r"\b(industrial design|fashion designer|interior designer|packaging designer|"
    r"find the right materials|mechanical enclosure)\b",
    re.I,
)
NO_SPONSOR = re.compile(
    r"(will not sponsor|no sponsorship|not eligible for visa sponsorship|"
    r"cannot sponsor|must be eligible to lawfully work|"
    r"required to be eligible to lawfully work|"
    r"authorized to work.{0,60}without sponsorship|"
    r"\bu\.?s\.? person\b|u\.?s\.? citizen|citizenship required|"
    r"must have (current )?(us )?work authorization)",
    re.I,
)
YEARS = re.compile(r"(?<!\d)(\d{1,2})\+\s*(?:years?|yrs?)", re.I)
YEARS_OF = re.compile(
    r"(?:over\s+)?(\d+|five|six|seven|eight|nine|ten)\s+years?\s+(?:of\s+)?(?:progressively )?(?:experience|product design|ux)",
    re.I,
)
WORD_YEARS = {"five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
SKIP_COMPANIES = re.compile(r"\bgoogle\b", re.I)
AGGREGATOR = re.compile(
    r"underdog\.io|sundayy|\bladders\b|jobright|posted\.careers",
    re.I,
)


def n(s: str) -> str:
    return re.sub(r"[\s\-]+", " ", s or "").strip().lower()


def gate(title: str, company: str, jd: str) -> tuple[bool, str]:
    t = title or ""
    text = f"{t}\n{jd or ''}"
    if SKIP_COMPANIES.search(company or "") or SKIP_COMPANIES.search(t):
        return False, "Zack: do not apply to Google"
    if AGGREGATOR.search(company or ""):
        return False, f"recruiter marketplace / aggregator: {company}"
    # Senior/Lead titles are OK. Staff in the title is a skip.
    if re.search(r"\bstaff\b", t, re.I):
        return False, f"Staff title: {t}"
    if not ROLE_OK.search(t) and not re.search(
        r"\b(ux|ui|product engineer|product design|user experience)\b", t, re.I
    ):
        return False, f"not product designer / product engineer / UX: {t}"
    if PHYSICAL.search(text):
        return False, "physical / industrial designer"
    jd_body = jd or ""
    for m in YEARS.finditer(jd_body):
        nyears = int(m.group(1))
        if nyears < 5 or nyears >= 20:
            continue  # 25+ company-age marketing is not a YOE knockout
        ctx = n(jd_body[max(0, m.start() - 50) : m.end() + 30])
        if re.search(r"nice to have|preferred|plus\b|bonus", ctx):
            continue
        return False, f"JD minimum years {nyears}+"
    for m in YEARS_OF.finditer(jd_body):
        raw = m.group(1).lower()
        nyears = WORD_YEARS.get(raw) or (int(raw) if raw.isdigit() else 0)
        if nyears >= 5:
            ctx = n(jd_body[max(0, m.start() - 50) : m.end() + 20])
            if re.search(r"nice to have|preferred", ctx):
                continue
            return False, f"JD minimum years {nyears}"
    if NO_SPONSOR.search(text):
        return False, "no sponsorship / must already have work auth"
    if re.search(r"public trust|security clearance required|us government client", text, re.I):
        return False, "gov clearance / Public Trust"
    return True, "apply"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--company", default="")
    p.add_argument("--jd", default="")
    p.add_argument("--jd-file", default="")
    args = p.parse_args()
    jd = args.jd
    if args.jd_file:
        jd = open(args.jd_file, encoding="utf-8").read()
    ok, reason = gate(args.title, args.company, jd)
    print(json.dumps({"apply": ok, "reason": reason, "company": args.company, "title": args.title}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
