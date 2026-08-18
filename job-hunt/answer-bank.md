# Answer bank / yes–no policy

Call `python3 /workspace/job-hunt/helpers/answer_engine.py "<question>"` during a form. Do not improvise PII.

## Binary / dropdown policy

| Pattern | Answer |
| --- | --- |
| Need sponsorship / visa / now or in future | **Yes** |
| Authorized to work without sponsorship | **No** |
| Have you ever worked at this company | **No** (unless story bank has it) |
| Have you done X (unfamiliar tool/domain) | **No** unless a real story maps |
| Willing to relocate | **Yes** |
| On-site / hybrid OK | **Yes** if JD is NL/SG/AU/NZ/US-from-this-search |
| Remote-only preference | do not claim remote-only |
| Can you start ASAP / notice period | **As soon as possible** |
| 18+ / eligible to work age | **Yes** |
| Require export-controlled US Person / citizenship | knockout **skip** |
| Security clearance | **No** |
| Disability / veteran / race / gender (EEO) | **Decline to self-identify** |
| How did you hear | **LinkedIn** (or the source Job hunter cited) |
| Gender / pronouns if optional | skip / decline |
| LinkedIn Easy Apply “follow company” | uncheck if optional |
| Convicted of felony | **No** (do not invent; if asked in a jurisdiction that is sensitive, still No unless Zack says otherwise) |
| Non-compete / currently employed at competitor | **No** unless true |
| GitHub | leave blank |
| Date of birth | leave blank |
| Salary (USD, no band) | 120000 |
| Years of UX/UI | **3+ years** |

## “Have you used / done X?”

Map to the story bank:

| Topic | Yes / No | Proof |
| --- | --- | --- |
| Figma, design systems | Yes | Alibaba migration; Ansys; Trip.com |
| B2B SaaS / complex workflows | Yes | Ansys Discovery; Trip.com B2B CS |
| AI product / Copilot / prototyping | Yes | Ansys Copilot; Sony AI commentator |
| Motion / After Effects | Yes only if asked about motion | Trip.com airport transfer; Sony |
| Consumer / growth / conversion | Yes | Trip.com +49.7%; Freshippo +3.12% |
| User research / usability | Yes | Sony 11 interviews; Trip.com; Shoonya |
| Code / vibe coding | Yes if asked about AI prototyping / light engineering | Cursor, HTML, Java listed on CV — not a SWE |
| Hardware / industrial / fashion / interior | **No** | skip those jobs |
| 5+ years leading a design team | **No** | never claim 5+ |

## Long text

English, first person, 80–150 words, metric in sentence one, no “passionate about”, no internship disclaimers.

Generator: `python3 /workspace/job-hunt/helpers/answer_engine.py --why --company "X" --role "Y" --location "Z"`.

Cover letter (required only): `python3 /workspace/job-hunt/helpers/answer_engine.py --cover --company "X" --role "Y" --location "Z"`.
