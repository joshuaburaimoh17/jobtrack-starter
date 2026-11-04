# JobTrack: instructions for Claude

This is the owner's personal job-search tracker: a local Django app plus Claude Code skills. It is **theirs**. They can ask you to change anything about it, and you should help them do it safely.

## Read these first
- **`profile.md`**: who the owner is, what they want, their honest experience, honesty rules and writing style. **Read it before any job search, CV tailoring, cover letter, application answer or interview prep.** If it doesn't exist, setup hasn't been run: suggest `/setup`.
- **`docs/FEATURES.md`**: everything the app and you can do. Use it to answer "what can this do?"
- **`docs/PLAYBOOK.md`**: hard-won job-search know-how (search filters, traps, inbox reading, salary, interviews). Follow it on every job search.

## Skills
- `/setup`: first-run install and personalisation (also re-runnable to fix things).
- `/job-search [N]`: the main loop: Gmail sweep, then find N verified-open jobs, then tailor a CV for each. Also triggered by "run job search".
- `/review`: a retro on all applications so far: what's working and what to change.

## Running things
All commands run from the repo root. `PY` means the venv's Python:
- Windows: `venv\Scripts\python.exe`
- Mac/Linux: `venv/bin/python`

| Task | Command |
|---|---|
| Start the app (run in background) | `PY manage.py runserver`, then http://127.0.0.1:8000 |
| See every application + lead | `PY manage.py tracker_status` |
| Add leads from a JSON file | `PY manage.py add_leads <file.json>` |
| Show the base CV sections | `PY manage.py cv_sections` (`--all` lists every paragraph) |
| Store a tailored CV + build the .docx | `PY manage.py save_tailoring <lead_id> <file.json>` |
| Mark lead(s) applied (= the Apply button) | `PY manage.py apply_lead <lead_id> [...]` |
| Dismiss lead(s) + delete their tailored CVs | `PY manage.py dismiss_lead <lead_id> [...]` |
| Change an application's status | `PY manage.py set_status <app_id> <status> --note "..." [--follow-up YYYY-MM-DD]` |
| Set the dashboard goal | `PY manage.py set_goal <n> --start YYYY-MM-DD --end YYYY-MM-DD` |
| Run the tests | `PY manage.py test tracker` |
| Wipe all applications + leads | `PY manage.py clear_placeholder_data --yes` (ask first!) |

**Prefer these commands over writing ad-hoc ORM scripts.** They apply the app's rules, e.g. `status_updated_at` only moves on a real status change. For anything else, write the Python to a temp `.py` file and run `PY manage.py shell -c "exec(open(r'<file>', encoding='utf-8').read())"`. On Windows, PowerShell mangles quotes and € signs in inline `-c` strings. Write JSON input files as UTF-8.

## How the code is laid out
- `tracker/models.py`: `Application` (jobs applied to), `JobLead` (jobs found, not yet applied), `GoalSetting` (singleton, always use `.load()`).
- `tracker/views.py` + `tracker/urls.py` + `tracker/templates/tracker/`: pages. Tailwind via CDN, Chart.js on Analytics. No build step.
- `tracker/services/applications.py`: `mark_lead_applied`, `set_status`. Shared by views and commands.
- `tracker/services/cv_tailor.py`: reads `cvs/base_cv.docx` sections by the heading map in `profile.md`, rebuilds the .docx keeping formatting (line *i* of new text goes into paragraph *i*), archives to `cvs/applications/<Month YYYY>/`.
- `tracker/profile.py`: parses the ```yaml block in `profile.md`.
- `tracker/management/commands/`: the commands above.
- Note: the in-app Dismiss button only changes the status. The `dismiss_lead` command also deletes the lead's tailored CVs.
- `.claude/skills/`: the skills. `docs/`: features + playbook. `docs/templates/`: starting files for `my-job-hunt/`.

## Rules when changing the code
1. **Make a save point first** for anything bigger than a one-liner: `git add -A && git commit -m "Before <change>"`. Then the owner can always undo with `git reset --hard HEAD~1` (explain this to them in plain words).
2. After any change, run `PY manage.py test tracker` and fix failures before saying it's done.
3. Model change means `PY manage.py makemigrations tracker`, then `PY manage.py migrate`. Never edit an applied migration.
4. **Never commit or upload** `profile.md`, `.env`, `db.sqlite3` or anything in `cvs/` or `my-job-hunt/`. They're gitignored; keep it that way. If the owner wants the code on their own GitHub, check `git status` shows none of them first.
5. Keep it simple and local. It's a single-user app on their own laptop; don't add hosting, Docker or accounts unless asked.
6. The owner may be learning. Explain what you changed in plain English, and offer to show the diff.

## Behaviour rules (apply to everything)
- **Gmail: drafts only, never send** an email on the owner's behalf.
- **Never invent** experience, skills, tools, metrics or qualifications. `profile.md` honesty rules override job-description keyword matching every time.
- **Salary:** if a posting advertises a figure, anchor to the posting, never to a lower default. Flag it before they answer a salary question.
- **Verify a posting is open** before suggesting it (see the PLAYBOOK).
- Follow `profile.md` writing style in anything written for them.
