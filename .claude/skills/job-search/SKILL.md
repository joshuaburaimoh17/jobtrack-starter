---
name: job-search
description: The owner's end-to-end job-search run. Scans their Gmail for application responses and updates JobTrack, then finds N open graduate/junior postings that fit profile.md (each verified still accepting applications), adds them to the queue, and tailors a CV for each. Use when the owner says "run job search", "find me jobs", "/job-search 10", or asks for their applications to be checked.
---

# /job-search: one command does the whole run

Run start to finish without asking the owner to trigger each step. **N** = the number they gave, else "Applications per search run" in `profile.md`, else 5.

`PY` = `venv\Scripts\python.exe` (Windows) or `venv/bin/python` (Mac/Linux). Run everything from the repo root. Write temporary JSON files to your scratchpad/temp directory, as UTF-8.

## 0. Load context (every run)
- Read **`profile.md`** in full: targets, locations, salary, start-date preference, true experience, honesty rules, writing style, application email. Missing? Stop and suggest `/setup`.
- Read **`docs/PLAYBOOK.md`**. It has the search filters, traps, inbox rules, salary and honesty rules. Follow it.
- Run `PY manage.py tracker_status` to see every application and open lead.
- If `my-job-hunt/grad_programme_deadlines.md` exists, skim it.

## 1. Gmail sweep: update the tracker to match reality
Use the Gmail connector (`search_threads`, then `get_thread` for details). Cover everything since the last run: the newest `status set` age in `tracker_status` is a guide; default `newer_than:7d`. Search:
- each tracked company's name/domain from `tracker_status` (both applications and leads);
- broad sweeps: `subject:(application OR interview OR assessment OR unfortunately OR "next steps") newer_than:7d`;
- `from:jobs-noreply@linkedin.com` for application confirmations. Ignore LinkedIn social noise.

For each relevant email, act (see PLAYBOOK §4 for the gotchas, e.g. Workday senders being a parent brand):

| Email says | Do |
|---|---|
| Confirmation for a lead still in the queue | `PY manage.py apply_lead <lead_id>` (they applied) |
| Rejection | `PY manage.py set_status <app_id> rejected --note "<sender, date, one line>"` |
| Recruiter interest / "reviewing your application" | `set_status … in_review --note …` |
| Interview invite | `set_status … interview_scheduled --note "<date/time/format/who>" --follow-up <date>` |
| Online test / questionnaire / video interview | `set_status … interview_scheduled --note "ASSESSMENT, not an interview: <type>, due <deadline>" --follow-up <deadline>` |
| Offer | `set_status … offer --note …` |
| Needs a reply (questions, salary, availability) | Gmail **draft** reply (`create_draft`) in the owner's writing style. **Never send.** Salary questions: follow PLAYBOOK §5. |

Also flag any application with a follow-up date of today or earlier, and any `applied` status silent for 21+ days ("treat as a no").

Gmail tool missing or failing? Say so at the top of the report, give the reconnect steps (PLAYBOOK §4, last bullet), and carry on with the job search. Next run, sweep further back.

## 2. Don't repeat yourself
Never suggest a company+role that's already applied to, queued or dismissed (`tracker_status` lists them all; `add_leads` also refuses duplicates). Watch for reposts of roles they were rejected from (PLAYBOOK §3).

## 3. Search: freshest first, wider than N
Search for roles that match `profile.md` targets and locations, using the PLAYBOOK §1 sources and URL filters:
- LinkedIn with `f_TPR=r86400` or `r172800`, plus `f_E=1,2` and `sortBy=DD`. Vary keywords, because LinkedIn's search is flaky;
- Indeed `fromage=1` to `3`;
- gradireland;
- company Greenhouse/Lever boards.

Collect about 2–3 times N candidates, because some will be closed, ineligible or poor fits.

Ranking (PLAYBOOK §1, *Freshness*, and §3):
1. **Fit** with the profile: role type, level (entry/grad only, unless profile says otherwise), location/commute, eligibility.
2. **Start date** per the profile (Sept-2027 programmes only as a labelled fallback, unless the profile says they're fine).
3. **Freshness:** prefer the last 24–48h when fit is comparable.

Reject anything that hits a PLAYBOOK §3 trap: years of experience, 2027-graduate-only eligibility, a language requirement, a degree gate, a licence, not commutable, a repost. Keep a short "ruled out" list with reasons for the report.

## 4. Verify every posting is OPEN: mandatory
Fetch each candidate's posting and confirm it's still accepting applications (PLAYBOOK §2). LinkedIn blocked? Verify on the company's own careers page / ATS, and store that URL instead. Can't verify it? It doesn't count toward N. Note each one's posted date and applicant count while you're there.

## 5. Add the N jobs to JobTrack
Write a UTF-8 JSON list and run `PY manage.py add_leads <file>`:
```json
[{"company": "...", "role": "...", "location": "Dublin (hybrid, 2 days)",
  "salary_range": "€32-36k" , "job_description": "<the real JD: responsibilities + requirements, keyword lines kept>",
  "source_url": "https://..."}]
```
`salary_range`: use "Not disclosed" if unknown. Keep the keyword-bearing lines of the job description; tailoring and interview prep depend on it. Note the lead ids it prints.

## 6. Tailor a CV for each lead (in-session, no API key)
1. `PY manage.py cv_sections` prints the owner's current summary / skills / experience text.
2. For each lead, write tailored versions following these rules (the same ones the app uses, `TAILORING_RULES` in `tracker/services/cv_tailor.py`):
   - **Summary:** rewrite from scratch for this role and company. 3–4 sentences. Name the company, the type of work and the most relevant real experience.
   - **Keywords:** mirror the job description's exact keywords and phrases for ATS filters, wherever they're *true*.
   - **Skills:** reorder lines and items most-relevant-first. **Keep the same number of lines and the same line format.**
   - **Experience:** reword bullets toward this role with action verbs and JD language. **Keep the same number of lines in the same order.** Leave header lines (job title, employer, dates) unchanged. Keep the bullet character. Keep existing numbers; never invent metrics.
   - **Never invent** skills, tools, employers, qualifications or experience. **Never upgrade verbs.** `profile.md` honesty rules beat keyword matching, every time.
   - `changes_made`: specific, e.g. "Moved SQL to the front of Technical skills (role is data-heavy); added 'stakeholder reporting' to bullet 2 of the café job to match the JD."
3. Write `{"summary": "...", "skills": "...", "experience": "...", "changes_made": "..."}` (lines separated by `\n`) to a UTF-8 JSON file. Run `PY manage.py save_tailoring <lead_id> <file>`. It stores the tailoring (so the app's diff view works) and saves the .docx to `cvs/applications/<Month YYYY>/`.
4. A section the profile maps to `null` is left out; the original stays.

## 7. Check the output
For each saved .docx, open it with python-docx (via a temp script and `PY`):
- the company/role keywords are present;
- the paragraph count is roughly the same as the base CV (formatting kept);
- no leftover text from another job.

If `base_cv.docx` can't be opened, it's probably open in Word or marked read-only (PLAYBOOK §10).

## 8. Report (in this order)
1. **Inbox news first.** Status changes made, Gmail drafts waiting for review, deadlines/assessments with dates, and stale 21+ day silences. If there's an interview or offer, lead with it.
2. **New jobs table:**

   | # | Company / role (linked) | Location | Salary | Posted | Why it fits | CV |
   |---|---|---|---|---|---|---|

   Include the lead id and CV path. **Flag** any salary above their minimum ("advertised €38k, use this, not your minimum"), any 2027 start, and any stretch requirement.
3. **Ruled out**, with one-line reasons (so they trust the filtering).
4. **Goal pace:** "X / target, on pace or N behind" (from `tracker_status`).
5. Remind them: **after applying, tell me ("I applied to 1, 3 and 4") or press Apply in the app**, so the tracker stays accurate. Offer cover letters or application-question answers for any of them.

If they want to look at the jobs, start the app in the background (`PY manage.py runserver`, then http://127.0.0.1:8000, Job Queue).

## After the report
- "I applied to …": `PY manage.py apply_lead <ids>`.
- They dismiss a lead: `PY manage.py dismiss_lead <ids>`. This also deletes its tailored .docx (PLAYBOOK §8).
- Grad programmes with deadlines that came up during the search: update `my-job-hunt/grad_programme_deadlines.md`.
- They want a PDF for a portal: make it, give the path, and delete it once they've uploaded it.
