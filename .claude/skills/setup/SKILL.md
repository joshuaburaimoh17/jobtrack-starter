---
name: setup
description: First-run setup for JobTrack. Installs the app, creates the owner's login, reads their CV to map its headings, interviews them to write profile.md, sets their goal, checks their Gmail connection, does a test CV tailoring and gives them a tour. Use when the owner types /setup, says "set up JobTrack", or when profile.md / venv / db.sqlite3 is missing. Safe to re-run: it skips what is already done.
---

# /setup: make this JobTrack yours

The owner is a recent graduate who may not be confident with terminals. Be friendly and plain-spoken. **Explain each step in one line before doing it.** Do as much as possible yourself and only ask them for what you genuinely can't do. Re-running is safe: check each step and skip what's already done.

`PY` = `venv\Scripts\python.exe` on Windows, `venv/bin/python` on Mac/Linux. All commands run from the repo root.

## Step 1: Check the tools
- Python 3.12+: try `python --version`, then `py -3 --version` (Windows), then `python3 --version` (Mac).
  - Missing or too old? Stop and explain: install from python.org. **On Windows, tick "Add python.exe to PATH" on the first installer screen.** Then close and reopen the terminal and run `claude` again, then `/setup`.
- Git: `git --version` (it should exist, since they cloned the repo).

## Step 2: Install the app
1. If `venv/` doesn't exist: `python -m venv venv` (use whichever Python command worked).
2. `PY -m pip install -r requirements.txt`
3. If `.env` doesn't exist: copy `.env.example` to `.env` and replace `SECRET_KEY=change-me` with a fresh value from `PY -c "import secrets; print(secrets.token_urlsafe(50))"`.
4. `PY manage.py migrate`
5. `PY manage.py test tracker`. It should pass. If it fails, fix it before going on.

## Step 3: Their login for the website
The app has a login screen. Ask what **username** they'd like. You can't type a password for them, and shouldn't see it. Tell them:
> Open a **second** terminal window in this same folder and run:
> `venv\Scripts\python.exe manage.py createsuperuser` (Mac: `venv/bin/python manage.py createsuperuser`)
> Enter your username, skip the email if you like (press Enter), then choose a password. Nothing shows while you type the password; that's normal. Tell me when it's done.

Check it worked: `PY manage.py shell -c "from django.contrib.auth.models import User; print(list(User.objects.values_list('username', flat=True)))"`.
(Forgotten password later: `PY manage.py changepassword <username>`.)

## Step 4: Their CV
1. Check `cvs/base_cv.docx` exists. If not, ask them to copy their CV into the `cvs` folder and rename it `base_cv.docx`.
   - **Only a PDF?** Have them open it in Word (free Word online works), check the layout survived, then *Save As* .docx. A PDF can't be tailored while keeping its formatting.
   - **Made in Canva / Google Docs?** Download it as .docx.
2. Run `PY manage.py cv_sections --all`. This lists every paragraph with its Word style.
3. From that list, identify **every section heading** (short lines like "Profile", "EXPERIENCE", "Technical Skills:", often a Heading style or bold). Work out which one holds:
   - the **summary** (Profile / About me / Personal statement), if any;
   - the **skills**;
   - the **experience** (Work Experience / Experience / Employment). Projects can count as experience if they have no work section.
4. Show them what you found and **ask them to confirm** ("Your CV has these sections: … I'll tailor Profile, Technical Skills and Experience. Right?").
5. **Problems to catch:**
   - If the output says the CV has **tables**, or obvious headings are missing from the list, the CV uses tables, columns or text boxes. Text inside those can't be tailored. Explain this simply and offer two options:
     - (a) tailor only the sections that are normal paragraphs;
     - (b) you help them rebuild the CV as a simple one-column document. That's usually better for ATS filters anyway.
   - Two sections with the identical heading text: ask them to rename one.
6. Write the `cv:` part of the yaml block (Step 5 creates the file if it doesn't exist yet), then run `PY manage.py cv_sections`. It must print all three sections with the right text. Fix the mapping until it does.

## Step 5: Interview them for profile.md
Use `profile.example.md` as the structure. Ask in **4–5 grouped rounds**, not 30 single questions, and offer examples. Read their CV first, so you can pre-fill and just confirm (name, degree, university, grade, experience).

1. **About you:** name, where you live, degree/grade/graduation year, right to work, driving licence, and the **email you apply from** (it must be the Gmail connected to Claude).
2. **What you want:**
   - target roles, and roles to avoid;
   - locations and the furthest commute you'd do, plus remote/hybrid;
   - minimum salary;
   - start date: now / 2026, or are Sept-2027 programmes OK?;
   - how many jobs per search run (default 5).
3. **Your experience, the true version:** go through each job/project on their CV. Ask what they *actually* did, versus what a CV might inflate. These become the honesty rules. Ask directly: "Is there anything on your CV you'd be nervous being asked about in detail?"
4. **Skills, honestly:** strong / working level / learning, with concrete ceilings (e.g. SQL: joins yes, window functions no).
5. **Writing style:** any phrases or punctuation they hate (e.g. dashes), how formal, Irish/UK or US spelling.

Write `profile.md`: the human sections in full, plus the yaml block with `name`, `cv` (from Step 4) and `honesty_rules` (the 2–5 most important rules). Show them a short summary and tell them they can edit it any time, by hand or by asking you.

## Step 6: Their goal and support files
1. Ask: "How many applications are you aiming for, by when?" (Suggest about 100 over 3 months if they're unsure.) Then run `PY manage.py set_goal <n> --start <today> --end <date>`.
2. If `my-job-hunt/` doesn't exist, copy `docs/templates/` into `my-job-hunt/`: the grad-programme tracker, interview prep (STAR bank, aptitude tests), agency pack and referral outreach. Tell them in one line what each is for.

## Step 7: Check Gmail is connected
Run a small Gmail search with the Gmail connector tool (`search_threads`, e.g. query `newer_than:2d`, a few results).
- **It works:** confirm the mailbox is the application email from their profile. If it's a different account, they need to switch it (below).
- **No Gmail tool, or an auth error:** explain:
  > Go to **claude.ai/customize/connectors** (claude.ai, then **Customize**, then **Connectors**), click **Gmail**, then **Connect**, and sign in with the Gmail you use for job applications. Then come back here, type `/mcp`, and authenticate Gmail if it's listed as needing it. Restart `claude` if it still doesn't show.

  Then test again. If it still fails, carry on; everything else works without Gmail, and `/job-search` will just skip the inbox step until it's fixed.

## Step 8: A test tailoring (so they see it work)
1. Create one example lead with `add_leads` (write a UTF-8 JSON file with a realistic graduate job matching their target roles, company "Example Ltd", `source_url` omitted).
2. Tailor it yourself, following the rules in `/job-search` step 6.
3. Run `save_tailoring <id> <file>`, and tell them the path of the .docx so they can open it in Word and see their own formatting kept.
4. Then delete the example: remove the lead (`PY manage.py shell -c "from tracker.models import JobLead; JobLead.objects.filter(company='Example Ltd').delete()"`) and the .docx file.

## Step 9: Start the app and give the tour
1. Start the server in the background: `PY manage.py runserver`. Tell them to open **http://127.0.0.1:8000** and log in.
2. Give a short tour based on `docs/FEATURES.md`: the pages (Dashboard, Job Queue, Applications, Analytics, CV Archive) and the 6–8 most useful things to say to you, especially **"run job search"**, **"I applied to …"** and **"mock interview me for …"**.
3. Tell them how to come back:
   > Each time: open a terminal in this folder, type `claude`, and say what you want. To see the website, say "start the app".
4. Mention they can change anything about the app by asking you (README → *Changing it yourself*).
5. Offer to run their first `/job-search` now.

## Finishing
Summarise what's set up in a short checklist (✅ app installed, ✅ login, ✅ CV mapped, ✅ profile, ✅ goal, ✅/❌ Gmail). Name anything still to do.
