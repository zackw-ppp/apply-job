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
CODE_RE = re.compile(r"security code|verification code|enter the code|one-time", re.I)


def n(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()


def body_text(page) -> str:
    try:
        return page.inner_text("body")
    except Exception:
        return ""


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


def click_apply_if_needed(page) -> bool:
    """Job boards often show a listing page with Apply before the form."""
    if page.locator("input[type=file], #first_name, input[type=email]").count():
        return False
    for pat in (r"^apply$", r"^apply now$", r"^apply for this job$"):
        btn = page.get_by_role("button", name=re.compile(pat, re.I))
        if btn.count():
            try:
                btn.first.click(timeout=3000)
                page.wait_for_timeout(800)
                return True
            except Exception:
                continue
        link = page.get_by_role("link", name=re.compile(pat, re.I))
        if link.count():
            try:
                link.first.click(timeout=3000)
                page.wait_for_timeout(800)
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
            label = n(el.evaluate(
                """e => {
                  const id = e.id;
                  if (id) {
                    const l = document.querySelector('label[for="'+id+'"]');
                    if (l) return l.innerText;
                  }
                  return (e.closest('label') || e.parentElement || e).innerText || '';
                }"""
            ))
            if re.search(
                r"privacy|terms|consent|agree|acknowledge|gdpr|i have read|required",
                label,
            ) and not re.search(r"text message|sms|marketing", label):
                el.check()
                log.append(f"check:{label[:40]}")
        except Exception:
            continue


def fill_ashby(page) -> dict:
    log = []
    page.wait_for_selector("input, textarea", timeout=20000)
    if Path(RESUME).exists():
        files = page.locator("input[type=file]")
        if files.count():
            files.first.set_input_files(RESUME)
            log.append("resume")
            page.wait_for_timeout(500)

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
            el.click()
            el.fill(val)
            log.append(f"fill:{q[:50]}")
            if "location" in q:
                page.wait_for_timeout(600)
                opt = page.get_by_text(re.compile(r"Shoreline", re.I)).first
                if opt.count():
                    opt.click(timeout=1500)
                    log.append("location:Shoreline")
                else:
                    page.keyboard.press("ArrowDown")
                    page.keyboard.press("Enter")
                    log.append("location-enter")
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
            page.wait_for_timeout(400)

    mapping_ids = {
        "first_name": P["first_name"],
        "last_name": P["last_name"],
        "preferred_name": P["first_name"],
        "email": P["email"],
        "phone": P["phone"],
        "candidate-location": f"{P['city']}, {P['state']}, United States",
        "country": P["country"],
    }
    for fid, val in mapping_ids.items():
        loc = page.locator(f"#{fid}")
        if loc.count():
            try:
                loc.first.click()
                loc.first.fill(val)
                log.append(fid)
                if fid in {"candidate-location", "country"}:
                    page.wait_for_timeout(400)
                    opt = page.get_by_text(re.compile(r"Shoreline|Washington, United States", re.I))
                    if opt.count():
                        opt.first.click(timeout=1500)
                    else:
                        page.keyboard.press("ArrowDown")
                        page.keyboard.press("Enter")
            except Exception as e:
                log.append(f"fail:{fid}:{e}")

    for i in range(page.locator("label[for]").count()):
        lab = page.locator("label[for]").nth(i)
        text = n(lab.inner_text())
        fid = lab.get_attribute("for") or ""
        if not fid or fid in mapping_ids:
            continue
        val = None
        if "linkedin" in text:
            val = P["linkedin"]
        elif "address" in text and "email" not in text:
            val = P["street"]
        elif "zip" in text or "postal" in text:
            val = P["zip"]
        elif "city of residence" in text:
            val = P["city"]
        elif "state or canadian" in text or "province" in text:
            val = P["state"]
        elif "country of residence" in text:
            val = P["country"]
        elif "authorized to work" in text or "without needing sponsorship" in text:
            val = "No"
        elif "sponsor" in text or "visa" in text:
            val = "Yes"
        elif "last company" in text:
            val = "Ansys (Synopsys) / Trip.com"
        elif "last job title" in text:
            val = "UX Designer"
        elif "referred" in text:
            val = "No"
        elif "pronoun" in text:
            val = ""
        elif "text messages" in text:
            val = "No"
        elif "github" in text or "birth" in text:
            val = ""
        elif "portfolio" in text or "website" in text:
            val = P["portfolio"]
        elif "year" in text and "experience" in text:
            val = P["years"]
        elif "gender" in text or "hispanic" in text or "veteran" in text or "disability" in text:
            val = "Decline to self-identify"
        elif "hear" in text or "how did you" in text:
            val = P["hear"]
        elif "relocat" in text:
            val = "Yes"
        elif "cover" in text or "why " in text or "additional" in text:
            val = WHY
        if val is None:
            continue
        box = page.locator(f"#{fid}")
        if not box.count():
            continue
        try:
            tag = box.first.evaluate("e => e.tagName")
            if tag == "SELECT":
                opts = box.locator("option").all_inner_texts()
                pick = next((o for o in opts if n(o) == n(val) or n(val) in n(o)), None)
                if not pick and val in ("Yes", "No"):
                    pick = next((o for o in opts if n(o).startswith(n(val))), None)
                if not pick and "decline" in n(val):
                    pick = next((o for o in opts if "decline" in n(o) or "wish not" in n(o)), None)
                if pick:
                    box.select_option(label=pick)
                    log.append(f"qsel:{text[:40]}")
            else:
                box.fill(val)
                log.append(f"q:{text[:40]}")
                if "location" in text or "country" in text or "city" in text or "state" in text:
                    page.wait_for_timeout(250)
                    page.keyboard.press("ArrowDown")
                    page.keyboard.press("Enter")
        except Exception as e:
            log.append(f"fail:{fid}:{e}")

    for i in range(page.locator("select").count()):
        el = page.locator("select").nth(i)
        try:
            label = n(el.evaluate("e => (e.closest('label')||e.parentElement).innerText"))
            opts = el.locator("option").all_inner_texts()
            pick = None
            if "sponsor" in label or "visa" in label:
                pick = next((o for o in opts if n(o) == "yes" or n(o).startswith("yes")), None)
            elif "authorized" in label:
                pick = next((o for o in opts if n(o) == "no" or n(o).startswith("no")), None)
            elif "relocat" in label:
                pick = next((o for o in opts if n(o) == "yes" or n(o).startswith("yes")), None)
            elif "gender" in label or "race" in label or "veteran" in label or "disability" in label or "hispanic" in label:
                pick = next((o for o in opts if "decline" in n(o) or "wish" in n(o)), None)
            elif "country" in label:
                pick = next((o for o in opts if "united states" in n(o)), None)
            elif "hear" in label or "source" in label:
                pick = next((o for o in opts if "linkedin" in n(o)), None)
            if pick:
                el.select_option(label=pick)
                log.append(f"select:{label[:30]}={pick}")
        except Exception:
            continue

    accept_required_checks(page, log)
    return {"log": log}


def enter_code(page, code: str, log: list) -> None:
    loc = page.locator(
        "input[name*=code], input[id*=code], input[autocomplete=one-time-code], input[type=text]"
    )
    for i in range(min(loc.count(), 8)):
        el = loc.nth(i)
        try:
            q = n((el.get_attribute("name") or "") + " " + (el.get_attribute("id") or "") + " " + (el.get_attribute("placeholder") or ""))
            if "code" in q or loc.count() == 1:
                el.fill(code)
                log.append("code")
                return
        except Exception:
            continue
    # last resort: first visible short text input
    try:
        page.locator("input:visible").first.fill(code)
        log.append("code-first")
    except Exception:
        log.append("code-miss")


def click_submit(page) -> bool:
    btn = page.get_by_role("button", name=re.compile(r"submit", re.I))
    if btn.count() == 0:
        btn = page.get_by_role("button", name=re.compile(r"send application|apply now|^apply$", re.I))
    if btn.count() == 0:
        return False
    try:
        btn.first.click(timeout=4000)
        return True
    except Exception:
        try:
            btn.last.click(timeout=4000)
            return True
        except Exception:
            return False


def classify(page) -> tuple[bool, bool, bool, str]:
    text = body_text(page)
    low = n(text)
    submitted = bool(SUCCESS_RE.search(low))
    already = bool(ALREADY_RE.search(low))
    need_code = bool(CODE_RE.search(low))
    return submitted, already, need_code, text[:900]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--company", default="")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--code", default="")
    args = ap.parse_args()
    t0 = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not args.headed, args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(700)
        clicked_apply = click_apply_if_needed(page)
        host = page.url
        already = False
        submitted = False
        need_code = False
        confirm = ""
        _, already, _, confirm = classify(page)
        if already:
            result = {"log": ["already-applied"]}
        else:
            if "ashbyhq.com" in host:
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
                clicked = click_submit(page)
                result.setdefault("log", []).append("submit-click" if clicked else "no-submit-btn")
                for _ in range(8):
                    page.wait_for_timeout(700)
                    submitted, already, need_code, confirm = classify(page)
                    if submitted or already or need_code:
                        break
                if not submitted and not already and not need_code and clicked:
                    click_submit(page)
                    page.wait_for_timeout(2000)
                    submitted, already, need_code, confirm = classify(page)
        safe = re.sub(r"[^A-Za-z0-9]+", "", args.company) or "job"
        shot = f"/tmp/apply-{safe}.png"
        try:
            page.screenshot(path=shot, full_page=True)
        except Exception:
            shot = ""
        elapsed = round(time.time() - t0, 1)
        out = {
            "company": args.company,
            "url": args.url,
            "seconds": elapsed,
            "submitted": submitted,
            "already_applied": already,
            "need_code": need_code,
            "log": result.get("log"),
            "final_url": page.url,
            "screenshot": shot,
            "confirm_head": confirm[:400],
        }
        print(json.dumps(out, indent=2))
        Path("/tmp/ats-last-fill.json").write_text(json.dumps(out, indent=2))
        Path(f"/tmp/ats-{safe}.json").write_text(json.dumps(out, indent=2))
        browser.close()
    return 0 if submitted or already else (2 if need_code else 1)


if __name__ == "__main__":
    raise SystemExit(main())
