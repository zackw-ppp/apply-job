#!/usr/bin/env python3
"""Map a form question to Zack's canned answer. No invented PII.

Usage:
  python3 answer_engine.py "How many years of UX/UI experience?"
  python3 answer_engine.py --why --company PermitFlow --role "Product Designer" --location "New York"
  python3 answer_engine.py --cover --company OpenAI --role "Product Designer" --location "San Francisco"
  python3 answer_engine.py --salary --bands "80000-100000,100000-120000,120000-140000" --company-size large
"""

from __future__ import annotations

import argparse
import re
import sys

PORTFOLIO = "https://zackw.framer.website"
EMAIL = "zackw294@outlook.com"
PHONE = "+1 206 579 2808"
ADDRESS = {
    "street": "18815 Aurora Avenue North",
    "city": "Shoreline",
    "state": "Washington",
    "state_code": "WA",
    "zip": "98133",
    "country": "United States",
    "full": "18815 Aurora Avenue North, Shoreline, Washington 98133",
}

USD_TARGET = 120_000


def norm(q: str) -> str:
    return re.sub(r"\s+", " ", q).strip().lower()


def years_answer() -> str:
    return "3+ years"


def salary_usd(bands: list[tuple[int, int]] | None, company_size: str) -> str:
    if not bands:
        return "120000"
    closest = min(bands, key=lambda b: abs(((b[0] + b[1]) / 2) - USD_TARGET))
    lo, hi = closest
    size = (company_size or "").lower()
    if size in {"large", "big", "faang", "public"}:
        # Prefer a range if the caller will paste it; otherwise sit a bit above the band floor.
        if hi - lo >= 20_000:
            return f"{max(lo, 120000)}-{hi}"
        return str(min(max(lo + 5000, 120000), hi))
    # SMB: lowest option closest to 120k
    return str(lo if abs(lo - USD_TARGET) <= abs(hi - USD_TARGET) else hi)


def parse_bands(raw: str) -> list[tuple[int, int]]:
    out = []
    for part in raw.split(","):
        nums = [int(x.replace(",", "").replace("k", "000")) for x in re.findall(r"\d[\d,]*", part)]
        if len(nums) == 1:
            n = nums[0]
            if n < 1000:
                n *= 1000
            out.append((n, n))
        elif len(nums) >= 2:
            a, b = nums[0], nums[1]
            if a < 1000:
                a *= 1000
            if b < 1000:
                b *= 1000
            out.append((min(a, b), max(a, b)))
    return out


def answer(question: str, jd_location: str = "") -> str | None:
    q = norm(question)

    if re.search(r"legal name|legal first|given name \(legal", q):
        if "last" in q or "family" in q or "surname" in q:
            return "WANG"
        if "first" in q or "given" in q:
            return "ZXIAO"
        return "ZXIAO WANG"
    if re.search(r"\bfirst name\b|\bgiven name\b|\bpreferred name\b", q):
        return "Zack"
    if re.search(r"\blast name\b|\bfamily name\b|\bsurname\b", q):
        return "WANG"
    if re.search(r"\bfull name\b|\byour name\b|^name$", q):
        return "Zack Wang"

    if "email" in q:
        return EMAIL
    if re.search(r"phone|mobile|tel", q):
        return PHONE
    if "github" in q:
        return ""  # do not fill
    if re.search(r"birth|dob|date of birth", q):
        return ""  # do not fill
    if re.search(r"portfolio|personal (site|website)|website url|portfolio url", q):
        return PORTFOLIO
    if re.search(r"linkedin(.+url| profile)", q):
        return "https://www.linkedin.com/in/zack-wang-6239a1210"

    if re.search(r"street|address line 1", q):
        return ADDRESS["street"]
    if re.search(r"\bcity\b", q) and "work" not in q and "job" not in q:
        return ADDRESS["city"]
    if re.search(r"\bstate\b|\bprovince\b", q):
        return ADDRESS["state"]
    if re.search(r"zip|postal", q):
        return ADDRESS["zip"]
    if re.search(r"country|nation|residence|located in|current location|where do you (live|reside)", q):
        if re.search(r"citizen|nationality|citizenship", q):
            return None  # do not claim US citizenship
        return "United States"
    if re.search(r"where (are you|would you like to work)|preferred (location|city|office)|job location", q):
        return jd_location or "United States"

    if re.search(r"start|available|notice period|when can you", q):
        return "as soon as possible"
    if re.search(r"relocat", q):
        return "Yes"

    if re.search(r"sponsor|visa|work authorization|immigration", q):
        if re.search(r"authorized|without sponsor|do you have authorization|currently authorized", q) and not re.search(
            r"need|require|will you", q
        ):
            return "No"
        if re.search(r"need|require|will you|future", q) or "sponsor" in q:
            return "Yes"
        return "Yes"

    if re.search(r"singapore.*(permit|ep|pass|authoriz)|work permit", q):
        return "No"

    if re.search(r"year.{0,20}(ux|ui|product design|design experience)|how many years", q):
        return years_answer()

    if re.search(r"hear about|how did you find|source", q):
        return "LinkedIn"

    if re.search(r"gender|race|ethnicity|veteran|disability|lgbt|sexual orientation|pronoun", q):
        return "Decline to self-identify"

    if re.search(r"clearance|secret|ts/sci", q):
        return "No"
    if re.search(r"us person|us citizen|green card|lawful permanent", q):
        return "SKIP_JOB"

    if re.search(r"work(ed)? (at|for) this (company|employer)|previously employed", q):
        return "No"
    if re.search(r"18 years|over 18|age of majority", q):
        return "Yes"

    if re.search(r"salary|compensation|pay expectation|expected pay", q):
        return "120000"

    if re.search(r"after effects|motion design|motion graphics", q):
        return "Yes"
    if re.search(r"\bfigma\b", q):
        return "Yes"

    return None


def why_text(company: str, role: str, location: str) -> str:
    loc = location or "the office listed on the role"
    return (
        f"At Trip.com I owned the charter-service redesign and raised order conversion 49.7% "
        f"in a year through behavior data, usability studies, and A/B tests. At Ansys I collapsed "
        f"seven Discovery variation-panel pop-ups into one flow for mechanical engineers, then "
        f"prototyped an AI Copilot that helped the team argue the roadmap with working artifacts "
        f"instead of decks. Sony work was similar: 11 interviews on an AI sports-commentator "
        f"experience, mapping what people actually needed before pushing UI. That mix — messy "
        f"B2B systems, consumer conversion, and AI prototyping — is what I would bring to the "
        f"{role} seat at {company}. I can relocate to {loc}. I will need employment sponsorship."
    )


def cover_text(company: str, role: str, location: str) -> str:
    # Shorter, less polished on purpose — forms that force a cover letter.
    loc = location or "your office"
    return (
        f"Hi {company} team —\n\n"
        f"I'm applying for the {role} role. Two pieces of work are probably the most useful "
        f"context. At Trip.com I led the charter-service redesign; conversion went up 49.7% "
        f"over a year after we changed the flow from mixed business/travel to a travel-first "
        f"product, backed by interviews, funnels, and A/B tests. At Ansys I took a Variation "
        f"Panel that lived in seven pop-ups and turned it into a single path, then used a "
        f"Copilot prototype to get stakeholders aligned faster than a slide review would have.\n\n"
        f"Portfolio: {PORTFOLIO}\n\n"
        f"I'm based in the US (Shoreline, WA), can move to {loc}, and I will need sponsorship.\n\n"
        f"Zack Wang\n{EMAIL}\n{PHONE}"
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("question", nargs="*")
    p.add_argument("--why", action="store_true")
    p.add_argument("--cover", action="store_true")
    p.add_argument("--salary", action="store_true")
    p.add_argument("--company", default="")
    p.add_argument("--role", default="Product Designer")
    p.add_argument("--location", default="")
    p.add_argument("--bands", default="")
    p.add_argument("--company-size", default="smb")
    args = p.parse_args()
    q = " ".join(args.question)

    if args.why:
        print(why_text(args.company or "the team", args.role, args.location))
        return 0
    if args.cover:
        print(cover_text(args.company or "the team", args.role, args.location))
        return 0
    if args.salary:
        bands = parse_bands(args.bands) if args.bands else None
        print(salary_usd(bands, args.company_size))
        return 0
    if not q:
        p.print_help()
        return 1
    a = answer(q, jd_location=args.location)
    if a is None:
        print("UNKNOWN_ASK_ZACK")
        return 2
    print(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
