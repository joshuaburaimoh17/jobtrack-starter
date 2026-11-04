# JobTrack

**Your own job-search assistant.** It's a small website on your laptop that tracks every job you find and apply to, plus Claude, which does the legwork. Claude:
- **finds** graduate/junior jobs that fit you, and checks each one is still open;
- **tailors your CV** for each job, keeping your CV's formatting;
- **reads your inbox** for replies and updates your tracker (rejections, interviews, assessments);
- **writes** cover letters, application answers and reply drafts, in your style and only with true claims;
- **preps you** for interviews: mock interviews, cheat sheets, a STAR story bank;
- **shows you** what's working: response rates, analytics, a goal tracker.

It was built for (and used through) a real 2026 graduate job hunt that ended in an offer. Everything learned along the way is in [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md). Everything it can do is in [`docs/FEATURES.md`](docs/FEATURES.md).

Everything personal (your CV, profile, applications, emails) **stays on your laptop**. None of it is ever uploaded.

---

## What you need
- **A paid Claude plan (Pro or above).** Claude Code and the Gmail connection need it.
- **A laptop** (Windows or Mac) and about **45 minutes** for the first setup.
- **Your CV as a Word file (.docx).** Only have a PDF? Open it in Word (free Word online works), check it looks right, then *Save As* .docx.
- **The Gmail account you apply for jobs with.**

---

## Setup, step by step (one time only)

> **New to terminals, Python or Git? Follow [`SETUP_GUIDE.md`](SETUP_GUIDE.md) instead.** It explains every click, assuming nothing. The steps below are the short version.

### 1. Get Claude Pro
Go to **claude.ai**, sign up (or log in), and upgrade to **Pro**.

### 2. Connect your Gmail to Claude
On claude.ai: **Customize → Connectors → Gmail → Connect** (direct link: claude.ai/customize/connectors). Sign in with **the Gmail you use for job applications**, because that's where recruiters reply.

### 3. Install Python
Download it from **python.org/downloads** and run the installer.
> ⚠️ **Windows: on the very first installer screen, tick "Add python.exe to PATH"** before clicking Install. This is the step people most often miss. If you forgot, run the installer again and choose *Modify*.

### 4. Install Git
- **Windows:** download from **git-scm.com** and click *Next* through everything (the defaults are fine).
- **Mac:** open Terminal and type `git --version`. If it isn't installed, your Mac offers to install it; say yes.

### 5. Install Claude Code
Open a terminal:
- **Windows:** press Start, type **PowerShell**, open it.
- **Mac:** press Cmd+Space, type **Terminal**, open it.

Paste the install command for your system (from **docs.claude.com → Claude Code → Setup**) and press Enter. At the time of writing:
- Windows (PowerShell): `irm https://claude.ai/install.ps1 | iex`
- Mac: `curl -fsSL https://claude.ai/install.sh | bash`

Close the terminal, open a new one, type `claude` and press Enter. A browser window opens. **Log in with your Claude account from step 1.** Then type `/exit` to leave Claude for now.

### 6. Download JobTrack
In the terminal, type these one line at a time :
```
cd Documents
git clone https://github.com/joshuaburaimoh17/jobtrack-starter jobtrack
cd jobtrack
```
You now have a `jobtrack` folder inside Documents.

### 7. Add your CV
Copy your CV (.docx) into the **`cvs`** folder inside `jobtrack`, and rename it **`base_cv.docx`**.

### 8. Run setup
In the same terminal (inside the `jobtrack` folder), type:
```
claude
```
then:
```
/setup
```
Claude takes it from here. It's a conversation of about 15–20 minutes. Approve its actions when it asks. It will:
- install everything the app needs;
- help you create your login. You'll type your own password in a second terminal window;
- **read your CV** and confirm its sections with you;
- ask what jobs you want, where, your minimum salary, your real experience (so it never exaggerates), and your writing style. It saves all this to `profile.md`;
- set your application goal;
- check your Gmail connection;
- do a practice CV tailoring so you can see it work;
- start the website and give you a tour.

### 9. Open the website
Go to **http://127.0.0.1:8000** in your browser and log in. 🎉

---

## Everyday use
1. Open a terminal and go to the folder: `cd Documents\jobtrack` (Mac: `cd Documents/jobtrack`).
2. Type `claude`.
3. Say what you want, in plain English:
   - **"run job search"**: checks your inbox, then finds and tailors 5 new jobs (or "run job search 10").
   - **"I applied to 1, 2 and 4"**: marks them applied.
   - **"Acme rejected me"** / **"I have an interview with Globex on Tuesday"**
   - **"write a cover letter for the Acme job"**
   - **"mock interview me for the Globex job"**
   - **"review my applications"**: what's working and what to change.
   - **"start the app"**: then open http://127.0.0.1:8000.
   - **"what can you do?"**: the full list is in [`docs/FEATURES.md`](docs/FEATURES.md).

A good rhythm: a job search every 2–3 days, apply the same day, and a `/review` once a week.

Claude **never sends emails for you**. Replies to recruiters are left as drafts in your Gmail for you to check and send.

---

## Changing it yourself
This copy is **yours**. Want a new column, a different page, UK jobs as well, a dark theme? Just ask Claude:
> "Add a field for who referred me to each application and show it on the application page."

Claude knows how the app is built (it reads `CLAUDE.md`), saves a checkpoint before big changes, and runs the tests afterwards.

**If a change breaks something:** tell Claude "undo that last change". Or go back to the last checkpoint yourself with `git reset --hard HEAD~1` (this only undoes code changes; your applications, CV and profile are never affected).

Your changes only affect your copy. Nobody else's JobTrack changes.

---

## Your private files
These are never uploaded anywhere (they're excluded from git):

| File | What |
|---|---|
| `profile.md` | Who you are and what you want. Claude reads it before everything. Edit freely. |
| `cvs/base_cv.docx` | Your master CV. |
| `cvs/applications/` | Every tailored CV, by month. |
| `cover-letters/` | Cover letters. |
| `my-job-hunt/` | Grad-programme deadlines, STAR stories, agency and referral notes. |
| `db.sqlite3` | Your applications and leads. |
| `.env` | Secret settings. |

**Back up `db.sqlite3`, `profile.md` and `cvs/` now and then**, e.g. copy them to OneDrive or iCloud.

---

## Troubleshooting
| Problem | Fix |
|---|---|
| `python` is not recognised | Python isn't on PATH. Re-run the Python installer, choose *Modify*, and tick "Add to PATH". Then open a new terminal. |
| `claude` is not recognised | Close and reopen the terminal. If it still fails, re-run the Claude Code install command. |
| Claude can't see your Gmail | claude.ai → Customize → Connectors → Gmail: connect it (the right account!). Then type `/mcp` in Claude Code, and restart `claude`. |
| Website won't load | Ask Claude to "start the app", then go to http://127.0.0.1:8000. |
| Forgot your website password | Ask Claude: "reset my JobTrack password". |
| CV tailoring says it can't find a heading | Your CV changed, or uses tables/text boxes. Tell Claude "I updated my base CV". |
| Lots of "allow this command?" prompts | Normal at first. Choose "Yes, and don't ask again" for JobTrack's own commands. |

---

*Built with Django + Claude Code. Tests: `venv\Scripts\python.exe manage.py test tracker`.*
