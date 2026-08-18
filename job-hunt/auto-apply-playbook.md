# Auto-apply playbook

Run this when Job hunter (or Zack) hands a role, or a LinkedIn search URL.

Source of truth:

- Profile: `/workspace/job-hunt/candidate-profile.md`
- Answers: `/workspace/job-hunt/answer-bank.md`
- This file
- Skip/applied: `/workspace/job-hunt/applied.md`, `/workspace/job-hunt/skipped.md`
- Resume: `/workspace/zack-wang-cv.pdf`
- Fill helper: `python3 /workspace/job-hunt/helpers/answer_engine.py`

Do not invent personal facts. UNKNOWN required field → stop and ask Zack.

This run: **auto-submit is ON** (Zack: apply every matching role through page 3, then dismiss with X).

## 1. Intake

Collect: apply URL, company, role, location, years required (quote), visa note, source (LinkedIn / Ashby / Greenhouse / company board), Job hunter apply/skip label.

LinkedIn search for this session:

`https://www.linkedin.com/jobs/search-results/?currentJobId=4451437464&keywords=product%20designer&origin=JOB_SEARCH_PAGE_JOB_FILTER&start=0&geoId=103644278&f_TPR=r86400`

Scope: **pages 1–3**, **25 jobs per page** (`start=0, 25, 50` → 75 cards). Titles: product designer / product engineer / UX. Exclude physical/industrial designers. **Staff in the title = skip.** Senior/Lead/Principal titles can still be applied to. Overly senior for years means **JD asks for 5+ years**.

## 2. Gate (before opening the form)

Stop if any of these are true:

- **Google** — Zack: do not apply (any Google role, including Search Ads 360)
- Already in `applied.md`
- JD minimum years is **5+** (Senior/Lead/Principal title alone is not a skip)
- **Staff** appears in the job title
- Knockout: must already have work authorization / no sponsorship / US Person / citizen-only
- Hard-skip company/role already listed
- Physical product / industrial / fashion / interior / graphic-only
- Not NL, SG, AU, NZ — **unless Zack overrides** (this LinkedIn URL is a US override)

Visa: need sponsorship. “Need sponsorship?” = Yes. “Authorized without sponsorship?” = No.

## 3. Open the form

1. Prefer Chrome on the box. LinkedIn Easy Apply needs Zack’s logged-in session.
2. If login / 2FA: hand the box to Zack once, then reuse the session. Agent may **read** verification emails only — never send or delete mail.
3. computerUse for clicking Easy Apply. Use `answer_engine.py` so repetitive fields are not re-thought.

## 4. Inventory every field

Classify: PII, file upload, binary, dropdown, short text, long text, knockout, EEO.

## 5. Fill

- PII from candidate profile; name rule (Zack vs legal ZXIAO)
- Upload CV PDF; portfolio = `https://zackw.framer.website` only
- Binary / dropdown from answer-bank
- Long text via `--why` / `--cover`
- EEO: decline
- How did you hear: LinkedIn
- Years: **3+ years**
- Country: United States
- Start: ASAP
- Salary: $120k policy
- Never claim 5+ years
- After Effects / motion: only with Trip.com / Sony stories

## 6. Review, then submit

Screenshot the completed form. This run: **submit**.

After submit: click the job card **X** (dismiss) so it leaves the list. Log the role so Job hunter does not re-recommend it.

## 7. Log

Append `applied.md` (America/Los_Angeles date) and `skipped.md`. Record elapsed minutes and the slowest step in `job-hunt/runs/`.

## Speed notes (2026-08-18)

What actually moved the needle:

| Path | Typical | Use when |
| --- | --- | --- |
| Playwright `ats_autofill.py --submit` | 30–125s including Greenhouse OTP | Ashby/Greenhouse URLs we already have |
| Desktop Chrome for Ashby | ~few minutes | Playwright got “possible spam” |
| computerUse click-by-click | 10–20 min/role, 100-image crash | iCIMS / Workday / unknown ATS only |
| LinkedIn guest “apply URL harvest” | wasted | Guest pages hide offsite apply behind login |

Rules that saved retries:

1. Gate **before** opening a form. Skip Google (Zack), Staff-in-title, aggregators (Sundayy/Ladders/Underdog), 5+ **required** years (not “nice to have”), Public Trust.
2. Don’t treat `curious person` as US Person; don’t treat `25+ Years of Proven Industry` as YOE.
3. Greenhouse: fill React-Select via `aria-controls` listbox; OTP is **8 boxes**; keep the session open and drop the code in `/tmp/gh-code.txt`.
4. Ashby: one Playwright submit; if spam, **one** desktop Chrome retry, not a third Playwright.
5. Never start a Google application.
6. Log seconds + bottleneck in `runs/timing.md` after each role.

Card left: finding company-board URLs without LinkedIn login; iCIMS/Workday still need the desktop Chrome session.
