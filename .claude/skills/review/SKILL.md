---
name: review
description: A retro on the owner's whole job search so far. Reads every application in JobTrack plus Gmail replies, works out what is getting responses and what isn't (by role type, company type, source, freshness), how fast rejections come, goal pace, and recommends concrete changes to targeting, CV or channels. Use when the owner says "/review", "review my applications", "what's working", or on their weekly review day.
---

# /review: what's working, and what to change

Best run weekly (e.g. Sundays), or whenever the owner feels stuck. Most useful after about 20 applications; with fewer, say the numbers are too small to conclude much and keep it short.

`PY` = `venv\Scripts\python.exe` (Windows) or `venv/bin/python` (Mac/Linux).

## 1. Get the data up to date
- Read `profile.md` and `docs/PLAYBOOK.md` §9.
- Do a quick Gmail sweep, as in `/job-search` step 1, so statuses are current before analysing.
- Export the applications: write a temp script that prints every `Application` as one row each (id, company, role, location, salary_range, date_applied, status, status_updated_at, notes, plus the linked lead's `date_found` if any), and run it with `PY manage.py shell -c "exec(open(r'<file>', encoding='utf-8').read())"`.

## 2. Analyse
Group each role into a **role type** yourself, based on its title and description, e.g. business/systems analyst, data analyst, software engineering, project management, finance/ops analyst, IT support, grad programme. Then work out:
- **Response rate**, overall and per role type. "Responded" = any status except `applied`. Also count **positive responses** (in_review / interview / offer) separately from rejections.
- **Interviews per role type.** This is the strongest signal of where they're competitive.
- **Time to rejection:** the median, and the share within 7 days and within 21 days. List the applications silent for 21+ days ("treat as a no").
- **Monthly trend:** do newer applications get better response rates than older ones? (This shows whether earlier changes worked.) The app's Analytics page has the same monthly table.
- **Goal pace:** applications in the goal window vs target, the linear pace to date, and how many per week are needed to finish on target.
- Anything else the data shows: company size or sector, agency vs direct, freshness when added, salary band, location.

Be honest about small samples. "0 of 3" is not a trend; "0 of 12" is.

## 3. Recommend
3–5 concrete, specific changes, each tied to the numbers. Examples of the kind that worked before (PLAYBOOK §9):
- Drop or deprioritise a role type with 0 positive responses from 10+ applications.
- Double down on the role type producing interviews.
- Change the CV angle for a role type that gets rejections.
- Add a channel (agencies, referrals, grad programmes) if cold applications are stalling.
- Change cadence or volume to hit the goal.

If they agree, **update `profile.md`** (targets / avoid list) so future `/job-search` runs follow the new strategy.

## 4. Housekeeping
- `my-job-hunt/grad_programme_deadlines.md`: anything opening or closing in the next 2 weeks?
- Follow-ups due, Gmail drafts waiting to be sent, interview prep needed for anything scheduled.
- Leads still in the queue for 7+ days: apply, or dismiss with `dismiss_lead`?

## 5. Report
Lead with a one-paragraph verdict, then:
1. the key numbers (a small table per role type);
2. the recommendations;
3. housekeeping to-dos.

Offer to save it as `my-job-hunt/reviews/<YYYY-MM-DD>.md`, so later reviews can compare against it. Read the previous review if one exists, and say what changed since.
