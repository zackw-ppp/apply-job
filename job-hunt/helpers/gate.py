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
    r"\b(product designer|product engineer|ux designer|ui/ux|ui ux|ux/ui|product design)\b",
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
    r"u\.?s\.? person|u\.?s\.? citizen|citizenship required|"
    r"must have (current )?(us )?work authorization)",
    re.I,
)
YEARS = re.compile(r"(\d+)\+\s*(?:years?|yrs?)", re.I)
YEARS_OF = re.compile(
    r"(?:over\s+)?(\d+|five|six|seven|eight|nine|ten)\s+years?\s+(?:of\s+)?(?:progressively )?(?:experience|product design|ux)",
    re.I,
)
WORD_YEARS = {"five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def gate(title: str, company: str, jd: str) -> tuple[bool, str]:
    t = title or ""
    text = f"{t}\n{jd or ''}"
    # Senior/Lead titles are OK. Staff in the title is a skip.
    if re.search(r"\bstaff\b", t, re.I):
        return False, f"Staff title: {t}"
    if not ROLE_OK.search(t) and not re.search(
        r"\b(ux|ui|product engineer|product design)\b", t, re.I
    ):
        return False, f"not product designer / product engineer / UX: {t}"
    if PHYSICAL.search(text):
        return False, "physical / industrial designer"
    years = [int(x) for x in YEARS.findall(text)]
    if years and max(years) >= 5 and YEARS.search(jd or ""):
        # 5+ in the JD body is a knockout; 4+ is allowed
        if max(int(x) for x in YEARS.findall(jd or "") or [0]) >= 5:
            return False, f"JD minimum years {max(years)}+"
    if NO_SPONSOR.search(text):
        return False, "no sponsorship / must already have work auth"
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
