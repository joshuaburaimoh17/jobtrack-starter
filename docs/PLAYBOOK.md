# Job-search playbook

Everything learned from a real graduate job hunt in Ireland, autumn 2026: ~90 applications, which led to recruiter calls, two multi-round interview processes and an offer. **Claude follows this on every `/job-search`.** You can read it too; it's written in plain English.

The owner's `profile.md` always overrides this file where they conflict (e.g. their own roles, locations and salary).

---

## 1. Where to search, and the filters that actually work

### LinkedIn (the most reliable source)
Use URL filters on `https://ie.linkedin.com/jobs/search/?keywords=<role>&location=<place>`, adding:
| Filter | Meaning |
|---|---|
| `f_TPR=r86400` | posted in the **last 24 hours** |
| `f_TPR=r172800` | last 48 hours |
| `f_TPR=r604800` | last week |
| `f_E=1,2` | experience level: **Internship + Entry level** (`3` = Associate) |
| `f_C=<company id>` | **one company only**. Get the id from the company's LinkedIn jobs URL. Use this for companies whose own careers site can't be read (Workday). |
| `f_WT=2` / `f_WT=3` | remote / hybrid |
| `sortBy=DD` | newest first |

Example: `https://ie.linkedin.com/jobs/search/?keywords=graduate%20business%20analyst&location=Dublin&f_TPR=r172800&f_E=1,2&sortBy=DD`

Quirks:
- LinkedIn's job search is "AI-powered" and **flaky**: some keyword searches return 0 results for no reason. Vary the wording ("junior analyst", "graduate analyst", "analyst graduate programme") before concluding there's nothing.
- LinkedIn geo-tags pages with **your** town. That is NOT where the job is; read the actual job location.
- Applicant counts ("200+ applicants") are a useful freshness/competition signal. Note them in the report.
- Prefer storing the company/ATS link over the LinkedIn link when you can find it. LinkedIn links die sooner.

### Other sources
- **Indeed:** `ie.indeed.com/jobs?q=<role>&l=<place>&fromage=1` (`fromage=1` = last day, `3` = last 3 days).
- **gradireland.com:** graduate programmes and grad roles.
- **Company ATS boards fetch reliably:**
  - Greenhouse: `boards.greenhouse.io/<company>`, API `boards-api.greenhouse.io/v1/boards/<company>/jobs`
  - Lever: `jobs.lever.co/<company>`, API `api.lever.co/v0/postings/<company>`
  - Workable, Teamtailor and SmartRecruiters pages usually fetch fine too.
- **Workday** careers pages (`*.myworkdayjobs.com`) usually come back **empty** when fetched. Use LinkedIn with `f_C=<id>` for those companies instead.
- Some big companies' own career search returns global results and is useless for a local search. Use LinkedIn.

### Sources that waste time
- A generic web search like "graduate jobs Dublin" returns only job-board index pages. That's one wasted call; search the boards directly.
- **IrishJobs email alerts** for "business analysis" surface senior/contract roles (€100k+ day-rate contracts), not grad roles.
- **Aggregator listings go stale.** A job shown on an aggregator may not exist on the company's site. Always check the source.
- Some agencies repost "junior" titles that are really 1–3+ year roles. If an agency never has true grad roles, stop checking it.

### Freshness
**Prefer jobs posted in the last 24–48 hours.** Early applicants get read before the pile builds. This is a *ranking* preference, not a filter: never pick a fresh weak fit over an older strong fit, and never come back with fewer jobs just because older ones weren't fresh. Always show the posted date in the report.

---

## 2. Verify every posting is OPEN before queuing it. No exceptions.
Fetch the actual posting and check:
- LinkedIn shows **"No longer accepting applications"** on closed jobs.
- 404s, "this job has expired" or redirects to a generic careers page mean it's closed.
- Can't verify it at all? Then it doesn't count. Find another.

Why: on an early run, closed postings slipped through and wasted a whole application session, along with CVs tailored for dead jobs.

---

## 3. Traps: read the whole posting before you add it
- **"2027 Graduate Programme" eligibility.** Many (especially banks and Big-4) are restricted to people *graduating in 2027* (e.g. "final-year students" or "graduating Jan–Aug 2027"). A 2026 graduate is often NOT eligible. Check the eligibility wording. Some say "graduating 2027 *or graduated 2026*", and those are fine.
- **Start date.** Most "2027" programmes start **September 2027**. If the owner wants to start soon, treat these as a labelled fallback ("starts Sept 2027"), not a default pick. No start date stated means treat it as an immediate start.
- **"Junior" titles that aren't junior.** Some firms' "Junior" or "Associate" roles ask for 3–4+ years of experience. The title lies; the requirements section doesn't. Experience "which can include work placement" means an internship counts.
- **Hidden language requirements:** e.g. "Technology Consultant Graduate" roles needing French/German/Spanish, or ops roles needing a Nordic language. Check before adding.
- **Degree gates:** "finance/accounting degree required", "engineering degree", "clinical qualification", "part-qualified actuary".
- **Licence / location:** "driver's licence required"; sites that aren't commutable; LinkedIn "Dublin" tags on jobs that are really in Kildare/Limerick.
- **Reposts:** a company can repost a role it already rejected you for, under a new LinkedIn id. Check by company + role before adding.
- **Contract vs permanent, and pay:** note FTC length; flag a posted salary band that's *above* the owner's minimum (see Salary below).
- **"One application only" programmes** (several Big-4 firms): choose the stream deliberately. Don't burn the one application on a weak-fit stream.
- **Internships** when the owner has already graduated: usually not eligible.

---

## 4. Reading the inbox (the Gmail sweep)
- Search the application email since the last run: each tracked company's name/domain, plus broad sweeps like `subject:(application OR interview OR assessment OR unfortunately) newer_than:7d`. Ignore LinkedIn social noise; DO read `jobs-noreply@linkedin.com` application confirmations.
- **Sender ≠ company.** Workday emails come from `<tenant>@myworkday.com`, and the tenant can be a parent or sister brand (e.g. a rejection for Company A arriving from Brand B's Workday). Match on the job title / requisition number, not just the sender.
- **Assessment invites are not interviews.** "Complete this online questionnaire/test within 5 days" goes to status `interview_scheduled` with a note saying it's an assessment, and the **follow-up date = the deadline**. Flag it at the top of the report.
- **Group mailboxes bounce.** Some companies' `recruitment@` addresses are Microsoft 365 groups that reject outside senders (bounce `550 5.7.193`). If a reply bounces, write to the named recruiter directly.
- **Recruiter questions** ("what are your salary expectations?", "are you still interested?") get a Gmail **draft** reply for the owner to review. **Never send.**
- When a status changes, add a dated note saying which email triggered it (`set_status --note`).
- **Timing:** most rejections arrive **within 7 days**; about **80% within 3 weeks**. After 3 weeks of silence, treat it as a no (`tracker_status` flags these). Don't chase cold applications more than once.
- If the Gmail connector fails (token expired), say so clearly and tell the owner to reconnect (claude.ai, then Customize, then Connectors, then Gmail; then `/mcp` in Claude Code). Next run, widen the sweep to cover the missed days.

---

## 5. Salary
- **If the posting states a salary or band, anchor to the posting.** Never volunteer the owner's lower minimum when the job advertises more. Flag this *before* they answer any salary question, on a form, in a phone screen or in an email.
- If a form forces a number and nothing is advertised: give a range whose bottom is the owner's minimum.
- Bonuses, pension % and benefits matter. When an offer comes, compare total package, not just base.
- Recruiters may say "that's below your expectations?" because of a number entered on a form. Confirm the band works if it does; don't let a careless form entry lose a role.

---

## 6. Honesty: the rule that protects every interview
- **Never upgrade verbs.** "Documented" ≠ "configured". "Edited" ≠ "built". "Proposed" ≠ "implemented". "Helped" ≠ "led". What's written in the CV gets asked about in interview.
- The **honesty rules in `profile.md` always beat job-description keyword matching.**
- Never invent metrics. Use only numbers already in the base CV.
- Keep application answers consistent. If an answer says "1 week notice", the next one can't say "2–3 days". Check earlier answers in the application notes.
- Internship dates matter. Don't call something "post-graduation experience" if it was during the degree.

---

## 7. Interviews: what worked
- **Ask what format to expect.** Not every panel is behavioural. Some are **approach-led**: "how would you check an AI's output?", "how would you automate this manual task?", "here's raw data from a database, what do you do first?". Prepare **scenario drills**, not only STAR stories.
- **State your own limit before they find it.** "Working level SQL: comfortable with selects, filters, joins and group by; I haven't done window functions or performance tuning yet." You can't be caught out on a limit you announced. Avoiding a weak area entirely looks worse than stating it precisely.
- **Name the gap, pivot, stop.** When you don't know something, say so, pivot to something real you built or did, then stop talking. Don't recite a definition you read 10 minutes ago; it sounds like bluffing.
- **Keep your single best concrete detail ready**, and include it every time that experience comes up (e.g. *the specific data problem you found and how you traced it*).
- Use exact posting vocabulary, and know your degree's real description (e.g. "quantitative", not "qualitative", if that's what it is).
- "Are you interviewing elsewhere?" A truthful "yes, I'm at second stage with another company" is leverage. Don't say no out of politeness.
- Phone screens with talent acquisition are **not** a formality. Salary, notice period and start date get settled there. Prepare for them.
- Two offers in flight: ask the first for 2–3 days and tell the other company the same day.
- After the interview, ask Claude to log what was asked (`notes` on the application). It sharpens the next round.

### Online assessments (the gate before most grad programmes)
Numerical reasoning, logical/inductive reasoning, situational judgement, game-based tests, recorded video interviews. See `my-job-hunt/interview-prep/aptitude_tests.md` for free practice sites and rules of thumb. Start practising before the invite arrives.

---

## 8. Documents and housekeeping
- **Word .docx is the master format.** Make a PDF only when a portal insists, then delete it afterwards (don't leave stray PDFs around).
- **Delete tailored CVs for jobs the owner dismisses.** The archive should only hold CVs that were (or will be) sent.
- **Cover letters:**
  - .docx in `cover-letters/`, with the header matching the CV header (name, contact line).
  - Open with a hook about the company (a recent strategy, product or news item), **never** "I am writing to apply for…".
  - Follow the writing style in `profile.md` (e.g. no dashes).
  - Ground claims in the real experience section of `profile.md`.
- **Application questions** ("why do you want to join our programme?"): research the company's *current* strategy or news first. A specific, recent fact beats generic praise.
- After the owner applies: `apply_lead <ids>` the same day so the dashboard and goal stay true.

---

## 9. Strategy, from what the data showed
- **Track response rate by role type.** In the original run, business-tech / systems / analyst roles got interviews; pure software-engineering and junior project-manager applications got none from ~17 tries. Lean into what responds (`/review` computes this).
- Recruiter interest came from finance/ops analyst roles even when applications to them were "reach" picks.
- ~5 well-chosen, freshly tailored applications per run beat 20 sprayed ones.
- A steady rhythm (a run every 2–3 days, plus a weekly review) beats bursts.
- **Other channels (from `docs/templates/`):**
  - recruitment-agency registration: one evening, 4–5 agencies;
  - referral outreach: 3–5 messages a week to alumni and early-careers recruiters;
  - a grad-programme deadline tracker, checked weekly.

---

## 10. Running the app from Claude (technical)
- Use the management commands listed in `CLAUDE.md` (`add_leads`, `save_tailoring`, `apply_lead`, `set_status`, `tracker_status`, `set_goal`). They apply the app's rules for you.
- Write JSON input files as UTF-8. On Windows, don't pass € signs or quotes inline in PowerShell; write them to a file.
- If `base_cv.docx` "can't be opened": it's probably open in Word (close it) or marked read-only (file Properties).
