#!/usr/bin/env python3
"""Fast Ashby + Greenhouse filler. Structured fields from profile.json.

  python3 ats_autofill.py --url URL --company NAME [--submit] [--code CODE]
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / "profile.json").read_text())
RESUME = P["resume"]

WHY = P["why"]
ABILITY = (
    "At Trip.com I owned the charter-service redesign and raised order conversion "
    "49.7% in a year, validated with usability studies and A/B tests. At Ansys I "
    "collapsed seven Discovery variation-panel pop-ups into one flow and prototyped "
    "an AI Copilot that the team used to align on roadmap instead of slides."
)

SUCCESS_RE = re.compile(
    r"success(fully)? submitted|thanks for (your )?app|thank you for (your )?app|"
    r"application (was |has been )?(successfully )?submitted|we received your application|"
    r"application received|you('ve| have) applied",
    re.I,
)
ALREADY_RE = re.compile(r"already applied|wait 180 days|you previously applied", re.I)
CODE_RE = re.compile(
    r"verification code was sent|enter the 8-character|confirm you're a human|confirm you’re a human",
    re.I,
)
SPAM_RE = re.compile(r"possible spam|flagged as possible spam", re.I)


def n(s: str) -> str:
    return re.sub(r"[\s\-]+", " ", s or "").strip().lower()


def body_text(page) -> str:
    try:
        return page.inner_text("body")
    except Exception:
        return ""


def by_id(page, fid: str):
    return page.locator(f'[id="{fid}"]')


def click_text(page, text: str) -> bool:
    loc = page.get_by_text(text, exact=True)
    if loc.count() == 0:
        loc = page.get_by_text(re.compile(rf"^{re.escape(text)}$", re.I))
    if loc.count() == 0:
        return False
    try:
        loc.first.click(timeout=2500)
        return True
    except Exception:
        return False


def pick_combo(page, el, wanted: str, log: list, key: str = "") -> bool:
    """Greenhouse/Ashby React-Select: click, then pick from THIS listbox only."""
    if not wanted or not el.count():
        return False
    box = el.first
    want = n(wanted)
    try:
        box.click(timeout=2500)
        page.wait_for_timeout(120)
        controls = box.get_attribute("aria-controls") or box.get_attribute("aria-owns") or ""
        opts = (
            page.locator(f'[id="{controls}"] [role="option"]')
            if controls
            else page.locator('[role="option"]')
        )

        def click_match() -> bool:
            total = min(opts.count(), 120)
            for i in range(total):
                t = n(opts.nth(i).inner_text())
                if not t:
                    continue
                if t == want or t.startswith(want) or want in t or t in want:
                    opts.nth(i).click(timeout=2000)
                    log.append(f"combo:{key}={wanted}")
                    return True
            return False

        if click_match():
            return True
        box.fill("")
        box.press_sequentially(wanted[:64], delay=25)
        for _ in range(8):
            page.wait_for_timeout(250)
            if click_match():
                return True
            if opts.count():
                break
        if opts.count() == 1:
            opts.first.click(timeout=2000)
            log.append(f"combo-only:{key}")
            return True
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        log.append(f"combo-enter:{key}")
        return True
    except Exception as e:
        log.append(f"combo-fail:{key}:{e}")
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        return False


def set_field(page, fid: str, val: str, log: list, key: str = "") -> bool:
    el = by_id(page, fid)
    if not el.count():
        return False
    node = el.first
    role = (node.get_attribute("role") or "").lower()
    typ = (node.get_attribute("type") or "text").lower()
    tag = node.evaluate("e => e.tagName")
    if typ in {"hidden", "file"}:
        return False
    if typ == "checkbox":
        try:
            if n(val) in {"yes", "true", "on", "1"}:
                node.check()
            log.append(f"check:{key or fid}")
            return True
        except Exception:
            return False
    if tag == "SELECT":
        opts = node.locator("option").all_inner_texts()
        pick = next((o for o in opts if n(val) in n(o) or n(o) == n(val)), None)
        if pick:
            node.select_option(label=pick)
            log.append(f"sel:{key or fid}={pick}")
            return True
        return False
    if role == "combobox":
        return pick_combo(page, el, val, log, key or fid)
    try:
        node.fill(val)
        log.append(f"fill:{key or fid}")
        return True
    except Exception as e:
        log.append(f"fail:{fid}:{e}")
        return False


def click_apply_if_needed(page) -> bool:
    if page.locator("input[type=file], [id='first_name'], input[type=email]").count():
        return False
    for pat in (r"^apply$", r"^apply now$", r"^apply for this job$"):
        for kind in ("button", "link"):
            loc = page.get_by_role(kind, name=re.compile(pat, re.I))
            if loc.count():
                try:
                    loc.first.click(timeout=3000)
                    page.wait_for_timeout(700)
                    return True
                except Exception:
                    continue
    return False


def accept_required_checks(page, log: list) -> None:
    boxes = page.locator("input[type=checkbox]:visible")
    for i in range(min(boxes.count(), 20)):
        el = boxes.nth(i)
        try:
            if el.is_checked():
                continue
            label = n(
                el.evaluate(
                    """e => {
                  const id = e.id;
                  if (id) {
                    const l = document.querySelector('label[for="'+CSS.escape(id)+'"]');
                    if (l) return l.innerText;
                  }
                  return (e.closest('label') || e.parentElement || e).innerText || '';
                }"""
                )
            )
            if re.search(r"privacy|terms|consent|agree|acknowledge|gdpr|i have read", label) and not re.search(
                r"text message|sms|marketing", label
            ):
                el.check()
                log.append(f"check:{label[:40]}")
        except Exception:
            continue


def answer_for_question(text: str) -> str | None:
    q = n(text)
    if "linkedin" in q:
        return P["linkedin"]
    if "github" in q or "birth" in q or "date of birth" in q:
        return ""
    if "portfolio" in q or "website" in q or "personal url" in q:
        return P["portfolio"]
    if "pronoun" in q:
        return "Prefer not to say"
    if ("address" in q and "email" not in q) or q.startswith("address"):
        return P["street"]
    if "zip" in q or "postal" in q:
        return P["zip"]
    if "city of residence" in q or (q.startswith("city") and "location" not in q):
        return P["city"]
    if "state or canadian" in q or "province" in q:
        return P["state"]
    if "country of residence" in q or (q.startswith("country") and "code" not in q):
        return P["country"]
    if "authorized" in q and ("without" in q or "sponsor" in q or "any employer" in q):
        return "No"
    if "authorized to work" in q:
        return "No"
    if "sponsor" in q or "visa" in q or "immigration" in q:
        return "Yes"
    if "relocat" in q:
        return "Yes"
    if "last company" in q or q.startswith("company name"):
        return "Trip.com"
    if "last job title" in q or (q.startswith("title") and "gender" not in q):
        return "UX Designer"
    if "referred" in q:
        return "No"
    if "text message" in q or "sms" in q:
        return "No"
    if "how did you hear" in q or (q.startswith("hear") or "source" in q):
        return "LinkedIn"
    if "year" in q and "experience" in q:
        return P["years"]
    if "gender" in q or "hispanic" in q or "veteran" in q or "disability" in q or "race" in q or "ethnicity" in q:
        if "veteran" in q:
            return "I do not want to answer"
        if "disability" in q:
            return "I do not want to answer"
        return "Decline To Self Identify"
    if "privacy" in q or "confidential" in q or "acknowledge" in q:
        return "I agree"
    if "school" in q:
        return "University of Washington"
    if "start date month" in q:
        return "June"
    if "start date year" in q:
        return "2022"
    if "end date month" in q:
        return "August"
    if "end date year" in q:
        return "2024"
    if "cover" in q or "why " in q or "additional" in q:
        return WHY
    return None


def fill_ashby(page) -> dict:
    log = []
    page.wait_for_selector("input, textarea", timeout=20000)
    if Path(RESUME).exists():
        files = page.locator("input[type=file]")
        if files.count():
            files.first.set_input_files(RESUME)
            log.append("resume")
            page.wait_for_timeout(600)

    def qtext(el) -> str:
        return el.evaluate(
            """e => {
              let n = e.closest('[class*="Field"], [class*="field"], form > div, label') || e.parentElement;
              return (n && n.innerText) ? n.innerText.slice(0, 400) : '';
            }"""
        )

    vis = page.locator("input:visible, textarea:visible")
    for i in range(vis.count()):
        el = vis.nth(i)
        typ = (el.get_attribute("type") or "text").lower()
        if typ in {"hidden", "file", "checkbox", "radio", "submit", "button"}:
            continue
        name = (el.get_attribute("name") or "") + " " + qtext(el)
        q = n(name)
        val = None
        if "email" in q:
            val = P["email"]
        elif re.search(r"\bname\b", q) and "user" not in q:
            val = P["full_name"]
        elif "phone" in q or "mobile" in q:
            val = P["phone"]
        elif "linkedin" in q:
            val = P["linkedin"]
        elif re.search(r"portfolio|website|personal", q):
            val = P["portfolio"]
        elif "github" in q or "birth" in q:
            val = ""
        elif "location" in q or "city" in q:
            val = P["location"]
        elif re.search(r"exceptional ability|example or evidence", q):
            val = ABILITY
        elif re.search(r"why are you interested|why this|additional", q):
            val = WHY
        elif re.search(r"year", q) and re.search(r"experience|ux|design", q):
            val = P["years"]
        if val is None:
            continue
        try:
            role = (el.get_attribute("role") or "").lower()
            if role == "combobox" or "location" in q:
                pick_combo(page, el, val, log, q[:40])
            else:
                el.click()
                el.fill(val)
                log.append(f"fill:{q[:50]}")
        except Exception as e:
            log.append(f"fail-fill:{e}")

    body = n(body_text(page))
    if "willing to relocate" in body or "located in the bay" in body:
        if click_text(page, "No, but willing to relocate"):
            log.append("relocate: willing")
        elif click_text(page, "Yes"):
            log.append("relocate: Yes")
    if "authorized to work" in body:
        try:
            page.locator("text=Are you legally authorized to work").locator("..").get_by_text(
                "No", exact=True
            ).first.click(timeout=2000)
            log.append("authorized: No")
        except Exception:
            nos = page.get_by_text("No", exact=True)
            if nos.count():
                nos.last.click()
                log.append("authorized: No (last)")
    if "need sponsorship" in body or "require sponsorship" in body or "visa" in body:
        try:
            page.locator("text=/sponsor/i").locator("..").get_by_text("Yes", exact=True).first.click(
                timeout=2000
            )
            log.append("sponsorship: Yes")
        except Exception:
            pass
    accept_required_checks(page, log)
    return {"log": log}


def fill_greenhouse(page) -> dict:
    log = []
    page.wait_for_selector("input, textarea, select", timeout=20000)
    if Path(RESUME).exists():
        files = page.locator("input[type=file]")
        if files.count():
            files.first.set_input_files(RESUME)
            log.append("resume")
            page.wait_for_timeout(500)

    set_field(page, "first_name", P["first_name"], log, "first_name")
    set_field(page, "last_name", P["last_name"], log, "last_name")
    set_field(page, "preferred_name", P["first_name"], log, "preferred_name")
    set_field(page, "email", P["email"], log, "email")
    set_field(page, "country", P["country"], log, "country")
    set_field(page, "phone", P["phone_national"], log, "phone")
    set_field(
        page,
        "candidate-location",
        f"{P['city']}, {P['state']}, United States",
        log,
        "location",
    )
    set_field(page, "company-name-0", "Trip.com", log, "company")
    set_field(page, "title-0", "UX Designer", log, "title")
    set_field(page, "start-date-month-0", "June", log, "start-month")
    set_field(page, "start-date-year-0", "2022", log, "start-year")
    set_field(page, "end-date-month-0", "August", log, "end-month")
    set_field(page, "end-date-year-0", "2024", log, "end-year")
    set_field(page, "school--0", "University of Washington", log, "school")

    for i in range(page.locator("label[for]").count()):
        lab = page.locator("label[for]").nth(i)
        try:
            text = lab.inner_text()
        except Exception:
            continue
        fid = lab.get_attribute("for") or ""
        if not fid or fid in {
            "first_name",
            "last_name",
            "preferred_name",
            "email",
            "phone",
            "country",
            "candidate-location",
            "resume",
            "resume_text",
            "company-name-0",
            "title-0",
            "start-date-month-0",
            "start-date-year-0",
            "end-date-month-0",
            "end-date-year-0",
            "school--0",
        }:
            continue
        val = answer_for_question(text)
        if val is None:
            continue
        set_field(page, fid, val, log, n(text)[:40])

    accept_required_checks(page, log)
    loc = by_id(page, "candidate-location")
    if loc.count() and not page.locator(".select__single-value").filter(
        has_text=re.compile("Shoreline", re.I)
    ).count():
        pick_combo(
            page,
            loc,
            "Shoreline, Washington, United States",
            log,
            "location-retry",
        )
    return {"log": log}


def enter_code(page, code: str, log: list) -> None:
    labeled = page.get_by_label(re.compile(r"security code|verification code", re.I))
    if labeled.count():
        labeled.first.fill(code)
        log.append("code-label")
        return
    loc = page.locator(
        "input[name*=code], input[id*=code], input[autocomplete=one-time-code]"
    )
    if loc.count():
        loc.first.fill(code)
        log.append("code")
        return
    # last visible short input near the submit button
    try:
        page.locator("input[type=text]:visible").last.fill(code)
        log.append("code-last")
    except Exception:
        log.append("code-miss")


def click_submit(page) -> bool:
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass
    btn = page.get_by_role("button", name=re.compile(r"submit application", re.I))
    if btn.count() == 0:
        btn = page.locator('button[type="submit"]')
    if btn.count() == 0:
        btn = page.get_by_role("button", name=re.compile(r"submit", re.I))
    if btn.count() == 0:
        return False
    try:
        btn.last.scroll_into_view_if_needed()
        btn.last.click(timeout=4000)
        return True
    except Exception:
        try:
            btn.last.click(timeout=4000, force=True)
            return True
        except Exception:
            return False


def classify(page) -> tuple[bool, bool, bool, bool, str]:
    text = body_text(page)
    low = n(text)
    submitted = bool(SUCCESS_RE.search(low))
    already = bool(ALREADY_RE.search(low))
    need_code = bool(CODE_RE.search(low))
    spam = bool(SPAM_RE.search(low))
    return submitted, already, need_code, spam, text[:900]


def launch_browser(p, headed: bool):
    return p.chromium.launch(
        headless=not headed,
        channel="chrome",
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ],
        ignore_default_args=["--enable-automation"],
    )


def new_page(browser):
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1400, "height": 900},
        locale="en-US",
        timezone_id="America/Los_Angeles",
    )
    context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    )
    return context, context.new_page()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--company", default="")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--code", default="")
    ap.add_argument("--wait-code-file", default="/tmp/gh-code.txt")
    args = ap.parse_args()
    t0 = time.time()
    with sync_playwright() as p:
        browser = launch_browser(p, args.headed)
        context, page = new_page(browser)
        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(900)
        clicked_apply = click_apply_if_needed(page)
        already = False
        submitted = False
        need_code = False
        spam = False
        confirm = ""
        _, already, _, spam, confirm = classify(page)
        result = {"log": []}
        if already:
            result = {"log": ["already-applied"]}
        else:
            if "ashbyhq.com" in page.url:
                result = fill_ashby(page)
            else:
                result = fill_greenhouse(page)
            if clicked_apply:
                result.setdefault("log", []).append("clicked-apply")
            apply_btn = page.get_by_role("button", name=re.compile(r"^apply$", re.I))
            submit_btn = page.get_by_role("button", name=re.compile(r"submit", re.I))
            if apply_btn.count() and submit_btn.count() == 0:
                try:
                    apply_btn.first.click()
                    page.wait_for_timeout(900)
                    if "ashbyhq.com" in page.url:
                        result = fill_ashby(page)
                    else:
                        result = fill_greenhouse(page)
                    result.setdefault("log", []).append("clicked-apply-2")
                except Exception:
                    pass
            if args.code:
                enter_code(page, args.code, result.setdefault("log", []))
            if args.submit:
                page.wait_for_timeout(800)
                clicked = click_submit(page)
                result.setdefault("log", []).append("submit-click" if clicked else "no-submit-btn")
                for _ in range(10):
                    page.wait_for_timeout(600)
                    submitted, already, need_code, spam, confirm = classify(page)
                    if submitted or already or need_code or spam:
                        break
                if spam:
                    result.setdefault("log", []).append("spam-flag")
                if not submitted and not already and not need_code and not spam and clicked:
                    click_submit(page)
                    page.wait_for_timeout(2500)
                    submitted, already, need_code, spam, confirm = classify(page)
                if need_code and not submitted:
                    code = (args.code or "").strip()
                    code_path = Path(args.wait_code_file) if args.wait_code_file else None
                    Path("/tmp/ats-waiting-code").write_text(args.company)
                    result.setdefault("log", []).append("waiting-code")
                    for _ in range(180):
                        if not code and code_path and code_path.exists():
                            code = code_path.read_text().strip().split()[0]
                        if code and len(code) >= 6:
                            break
                        page.wait_for_timeout(1000)
                    if code and len(code) >= 6:
                        enter_code(page, code, result.setdefault("log", []))
                        click_submit(page)
                        for _ in range(10):
                            page.wait_for_timeout(600)
                            submitted, already, need_code, spam, confirm = classify(page)
                            if submitted or already:
                                break
                    else:
                        result.setdefault("log", []).append("code-timeout")
        safe = re.sub(r"[^A-Za-z0-9]+", "", args.company) or "job"
        shot = f"/tmp/apply-{safe}.png"
        try:
            page.screenshot(path=shot, full_page=True)
        except Exception:
            shot = ""
        errors = []
        try:
            errors = [
                t.strip()
                for t in page.locator(".helper-text--error").all_inner_texts()
                if t.strip()
            ][:12]
        except Exception:
            pass
        elapsed = round(time.time() - t0, 1)
        out = {
            "company": args.company,
            "url": args.url,
            "seconds": elapsed,
            "submitted": submitted,
            "already_applied": already,
            "need_code": need_code,
            "spam": spam,
            "log": result.get("log"),
            "errors": errors,
            "final_url": page.url,
            "screenshot": shot,
            "confirm_head": confirm[:400],
        }
        print(json.dumps(out, indent=2))
        Path("/tmp/ats-last-fill.json").write_text(json.dumps(out, indent=2))
        Path(f"/tmp/ats-{safe}.json").write_text(json.dumps(out, indent=2))
        context.close()
        browser.close()
    return 0 if submitted or already else (2 if need_code else 1)


if __name__ == "__main__":
    raise SystemExit(main())
