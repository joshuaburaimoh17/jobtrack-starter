# My JobTrack profile

> `/setup` creates your real `profile.md` from this template by interviewing you.
> `profile.md` is private (gitignored). Claude reads ALL of it before every job search,
> cover letter, CV tailoring and interview prep, so the more honest and specific it is, the better.
> Edit it any time, by hand or by telling Claude ("add Cork to my locations").

## About me
- **Name:** Alex Example
- **Lives in:** Swords, Co. Dublin, Ireland
- **Degree:** BSc (Hons) Computing, 2:1, graduated 2026
- **Application email:** alex.example@gmail.com. This is the Gmail connected to Claude; all replies arrive here.
- **Right to work:** EU citizen (no sponsorship needed)
- **Driving licence:** no

## What I'm looking for
- **Target roles:** Graduate/Junior Business Analyst, Data Analyst, Technical Analyst, graduate programmes (tech/business streams)
- **Not interested in:** pure software engineering, sales, call-centre roles
- **Level:** graduate / entry level only. Skip anything asking for 2+ years.
- **Locations:** Dublin (commutable from Swords). Hybrid or remote is fine. Not Cork/Galway/Limerick.
- **Minimum salary:** €30,000. This is a preference, not a hard cutoff. If a posting advertises MORE, use the posting's number, never this one.
- **Start date:** want to start ASAP / in 2026. Programmes starting in Sept 2027 only as a labelled fallback.
- **Applications per search run:** 5

## My experience, in my own words (the true version)
Claude uses this to keep tailored CVs, cover letters and interview answers honest.
- *Summer internship, Company X (Jun–Aug 2025):* helped prepare weekly Excel reports; tested a new internal tool and logged bugs. I was one of three testers. I did NOT lead the testing.
- *Part-time, café (2023–now):* customer service, cash handling, trained two new starters.
- *Final-year project:* a Django web app with … (what you actually built).

## Honesty rules
Claude must never break these, even to match a job description. Repeat the key ones in the yaml below.
- Never say I "led" the testing at the internship; I was one of three testers.
- Never claim experience with tools I've only read about.

## Writing style (cover letters, emails, application answers)
- No em dashes or en dashes.
- Open cover letters with a hook about the company, never "I am writing to apply for…"
- Plain, confident, not over the top. Irish/UK spelling.

## Skills I'm honest about
- **Strong:** Python, Excel
- **Working level:** SQL (selects, joins, group by; not window functions yet), Power BI basics
- **Learning:** …

---

## Settings the app reads (keep this block valid YAML)

`cv:` tells the app which headings in YOUR `cvs/base_cv.docx` hold the summary, skills and experience.
Copy the heading text exactly as it appears in your CV (capitals and a trailing colon don't matter).
Set a key to `null` if your CV doesn't have that section. `headings:` lists EVERY section heading in
your CV, top to bottom, so the app knows where each section ends.

```yaml
name: Alex Example
cv:
  path: cvs/base_cv.docx
  summary: Professional Summary
  skills: Skills
  experience: Work Experience
  headings:
    - Professional Summary
    - Work Experience
    - Projects
    - Skills
    - Education
honesty_rules:
  - Never say I led the testing at the internship; I was one of three testers.
  - Never claim tools or experience that are not already in my CV.
```
