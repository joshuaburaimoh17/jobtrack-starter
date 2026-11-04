# What JobTrack can do

JobTrack has two halves:
- **the app**: a website on your own laptop (http://127.0.0.1:8000) that tracks everything;
- **Claude**: Claude Code in this folder, which does the legwork. It finds jobs, reads your inbox, tailors CVs and writes drafts.

They share the same database, so anything Claude does shows up in the app, and the other way round.

---

## The app, page by page

### Dashboard
- **Stat cards:** total applications, applications in the last 7 days, leads waiting in your queue, offers.
- **Goal tracker:** a progress bar toward your target, e.g. "42 / 100 applications, Nov–Feb". Only applications inside the goal window count. Change it by asking Claude ("set my goal to 120 by end of February") or in `/admin/`.
- **Status breakdown** and your **5 most recent applications**.

### Job Queue: jobs you've found but not applied to yet ("leads")
- Tabs: **New**, **Ready to Apply**, **Applied**, **Dismissed**.
- **⚠ orange flag:** the job might be US-only (it says "must be based in…", names a US state, etc.).
- **+ Add Job:** paste in a job you found yourself (company, role, location, salary, description, link).
- Open a lead to see the full description and these buttons:
  - **Tailor CV:** rewrites your CV for this job (see below).
  - **Mark Ready:** moves it to the Ready tab.
  - **Dismiss:** you're not applying (Claude won't suggest it again).
  - **Apply / Mark Applied:** press this **after** you've actually applied. It turns the lead into a tracked Application and copies everything across.

### CV tailoring
- Starts from **your** `cvs/base_cv.docx` and rewrites three sections for the specific job: summary, skills and experience. It mirrors the job description's keywords for ATS filters, reorders your skills most-relevant-first, and reshapes bullet points.
- **Never invents anything.** Your honesty rules in `profile.md` always win.
- **Your formatting is kept:** same fonts, layout and headings. Only the words change.
- **Diff view:** side-by-side, original vs tailored, with every change highlighted. It also shows a list of *what changed and why*.
- **Download Tailored CV:** a ready-to-send .docx.
- Two ways to run it:
  - **free:** ask Claude ("tailor my CV for lead 4"). `/job-search` does this automatically for every job it finds;
  - **in-app button:** needs a pay-per-use Anthropic API key in `.env`. Optional.

### Applications: jobs you've applied to
- Search by company/role, filter by status, sort by date/company/status.
- Statuses: Applied → In Review → Interview Scheduled → Interview Done → Offer / Rejected / Withdrawn.
- Each application stores the job link, the job description (handy for interview prep), notes, contact name and a **follow-up date**.
- When a status changes, the app records **when** it changed. That's how Claude spots "applied 3+ weeks ago with no reply".

### Analytics
- **Applications per week** (last 12 weeks) bar chart.
- **Status doughnut:** where all your applications currently sit.
- **Response rate:** the % of applications that got any reply.
- **Applications per Month table:** applied, change vs the previous month, per day, responses, interviews, offers, rejections, response rate.

### CV Archive
Every tailored CV is saved automatically into `cvs/applications/<Month YYYY>/`. This page lists them by month, newest first, with download links. It's handy when a recruiter rings about a job from six weeks ago and you need the exact CV you sent.

### Admin (`/admin/`)
Django's built-in back office: edit any record directly, and change the goal.

---

## Things you can just ask Claude

Open a terminal in this folder, type `claude`, then say any of these in plain English:

| Say… | What happens |
|---|---|
| **"run job search"** / `/job-search 10` | Checks Gmail for replies and updates your applications. Finds N (default from your profile) **verified-open** jobs that fit your profile, adds them to the queue, and tailors a CV for each. Then it reports. |
| **"I applied to all of them"** / "I applied to Acme and Globex" | Marks those leads applied (same as the Apply button). |
| **"Acme rejected me"** / "I have an interview with Globex on Tuesday at 2" | Updates the status, adds a dated note, and sets the follow-up date. |
| **"check my email"** | Just the Gmail sweep, no new jobs. |
| **"tailor my CV for lead 4"** | Tailors and saves the .docx. Then you can see the diff in the app. |
| **"write a cover letter for lead 4"** | A .docx cover letter in `cover-letters/`, in your writing style, matching your CV header. |
| **"answer this application question: …"** | A written answer grounded in your real experience and the company's current news/strategy. |
| **"draft a reply to this recruiter"** | A Gmail **draft** you review and send yourself. Claude never sends email. |
| **"mock interview me for the Globex job"** | Interview practice with feedback, using the job description and your real experience. |
| **"make me a cheat sheet for my Globex interview"** | One page: the role, the company, likely questions, your best stories. |
| **"make a PDF of my Acme CV"** | Only for portals that insist on PDF (Word .docx is the master copy). |
| **"review my applications"** / `/review` | A retro: response rate by role type, how fast rejections come, what's working and what to change. |
| **"set my goal to 100 applications by end of March"** | Updates the dashboard goal. |
| **"what's in my queue?"** / "how many have I applied to?" | Reads the database and tells you. |
| **"start the app"** | Starts the website so you can open http://127.0.0.1:8000. |
| **"add Cork to my locations"** / "stop showing me sales roles" | Updates `profile.md`. |
| **"I updated my base CV"** | Re-checks your CV headings still match. |
| **"change the app so…"** | Changes the app itself (see the README, *Changing it yourself*). |

---

## Your files (all private, never uploaded)
- `profile.md`: who you are and what you want. Claude reads it before everything.
- `cvs/base_cv.docx`: your master CV.
- `cvs/applications/`: every tailored CV.
- `cover-letters/`: cover letters Claude writes.
- `my-job-hunt/`: your grad-programme deadline tracker, interview STAR stories, outreach notes (copied from `docs/templates/` at setup).
- `db.sqlite3`: the database (applications, leads, goal).
- `.env`: secret settings.
