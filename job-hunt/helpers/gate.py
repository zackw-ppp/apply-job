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
    r"tabletop accessories|find the right materials|mechanical enclosure|"
    r"mechanical design engineer|hardware design engineer|pcb design|"
    r"graduate design engineer|associate design engineer)\b",
    re.I,
)
NO_SPONSOR = re.compile(
    r"(will not sponsor|no sponsorship|not eligible for visa sponsorship|"
    r"cannot sponsor|not able to sponsor|unable to sponsor|"
    r"unable to provide sponsorship|not able to offer.{0,40}sponsorship|"
    r"must be eligible to lawfully work|"
    r"required to be eligible to lawfully work|"
    r"authorized to work.{0,80}without (the need for |the need of )?(employer )?sponsorship|"
    r"without the need (?:for|of) employer sponsorship|"
    r"\bu\.?s\.? person\b|u\.?s\.? citizen|citizenship required|"
    r"must have (current )?(us )?work authorization)",
    re.I,
)
YEARS = re.compile(r"(?<!\d)(\d{1,2})\+\s*(?:years?|yrs?)", re.I)
YEARS_OF = re.compile(
    r"(?:over\s+)?(\d+|five|six|seven|eight|nine|ten)\s+years?\s+"
    r"(?:of\s+)?(?:progressively |dedicated )?(?:experience|product design|ux)",
    re.I,
)
# Floor of ranges like "5-8 years" / "5 to 10 years" / "8–10+ years"
YEARS_RANGE = re.compile(
    r"(?<!\d)(\d{1,2})\s*(?:to|–|-|—)\s*\d{1,2}\+?\s*(?:years?|yrs?)",
    re.I,
)
AT_LEAST_YEARS = re.compile(
    r"(?:at least|minimum of|minimum|more than|over)\s+(\d{1,2})\s+years?|"
    r"(\d{1,2})\s+years?\s+or\s+more|"
    r"(?:bachelor|ba|bs)\+?\s*(\d{1,2})\s+years?",
    re.I,
)
WORD_YEARS = {"five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
SENIOR_TITLE = re.compile(r"\b(senior|lead|principal)\b", re.I)


def _in_year_range(jd_body: str, m: re.Match) -> bool:
    """Skip the high end of '3-10 years' / '3 to 10 years' (floor is the requirement)."""
    before = jd_body[max(0, m.start() - 16) : m.start()]
    return bool(re.search(r"(?<!\d)\d{1,2}\s*(?:to|–|-|—)\s*$", before, re.I))


def _nice_to_have(jd_body: str, m: re.Match) -> bool:
    """Only soft-req YOE like '5+ years preferred', not 'Preferred Qualifications: 5+'."""
    after = n(jd_body[m.end() : m.end() + 40])
    before = n(jd_body[max(0, m.start() - 35) : m.start()])
    if re.search(r"^(?:years?|yrs?)?\s*(?:preferred|a plus|nice to have|is a plus|bonus)", after):
        return True
    if re.search(r"(nice to have|bonus|plus)[:\s]*$", before):
        return True
    # "preferred 5+ years" — but not "Preferred Qualifications" section headers
    if re.search(r"preferred\s*$", before) and not re.search(r"qualifications?\s*$", before):
        return True
    return False


def _year_limit(title: str) -> int:
    # Zack 2026-08-18: if the JD explicitly requires 5+ years, skip (Senior title does not override).
    return 5
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
    # Senior/Lead titles are OK. Staff / Principal in the title is a skip.
    if re.search(r"\bstaff\b", t, re.I):
        return False, f"Staff title: {t}"
    if re.search(r"\bprincipal\b", t, re.I):
        return False, f"Principal title: {t}"
    if re.search(r"\bproduct engineer\b", t, re.I) and not re.search(
        r"\b(product design engineer|design engineer)\b", t, re.I
    ):
        return False, f"physical product engineer, not UX: {t}"
    if not ROLE_OK.search(t) and not re.search(
        r"\b(ux|ui|product engineer|product design|user experience)\b", t, re.I
    ):
        return False, f"not product designer / product engineer / UX: {t}"
    if PHYSICAL.search(text):
        return False, "physical / industrial designer"
    jd_body = jd or ""
    limit = _year_limit(t)
    for m in YEARS.finditer(jd_body):
        nyears = int(m.group(1))
        if nyears < limit or nyears >= 20:
            continue  # 25+ company-age marketing is not a YOE knockout
        if _in_year_range(jd_body, m) or _nice_to_have(jd_body, m):
            continue
        return False, f"JD minimum years {nyears}+"
    for m in YEARS_OF.finditer(jd_body):
        raw = m.group(1).lower()
        nyears = WORD_YEARS.get(raw) or (int(raw) if raw.isdigit() else 0)
        if nyears < limit:
            continue
        if _in_year_range(jd_body, m) or _nice_to_have(jd_body, m):
            continue
        return False, f"JD minimum years {nyears}"
    for m in YEARS_RANGE.finditer(jd_body):
        nyears = int(m.group(1))
        if nyears < limit or nyears >= 20:
            continue
        if _nice_to_have(jd_body, m):
            continue
        return False, f"JD minimum years {nyears}+ (range floor)"
    for m in AT_LEAST_YEARS.finditer(jd_body):
        nyears = int(next(g for g in m.groups() if g))
        if nyears < limit or nyears >= 20:
            continue
        if _nice_to_have(jd_body, m):
            continue
        return False, f"JD minimum years {nyears}+ (at least)"
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
