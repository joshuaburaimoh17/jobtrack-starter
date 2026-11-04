# JobTrack: the complete setup guide

This guide assumes **nothing**. If you've never used a terminal, never installed Python and never heard of Git, that's fine. Follow the steps in order and don't skip any. Each step tells you what you should see when it worked.

**Time:** about 1 hour the first time (most of it is installers and a chat with Claude).
**After that:** about 2 minutes to start it each time.

---

## What you're setting up

JobTrack is your own job-search assistant. It has two parts:

1. **A small website that runs only on your laptop.** It tracks every job you find, every job you apply to, your progress toward a goal, and stats on what's working. Nobody else can see it.
2. **Claude**, running in a terminal next to it, which does the legwork:
   - finds graduate/junior jobs that suit **you**, and checks each is still open;
   - rewrites **your** CV for each job, keeping your CV's design;
   - reads **your** Gmail for replies (rejections, interview invites, online tests) and updates your tracker;
   - writes cover letters, application answers and reply drafts (it never sends anything itself);
   - runs mock interviews and makes interview cheat sheets.

Everything personal (your CV, your details, your applications) stays on your laptop and is never uploaded.

---

## Before you start: checklist

- [ ] A **laptop**: Windows 10/11 or a Mac (macOS 13 or newer).
- [ ] About **1 hour** and a decent internet connection.
- [ ] Your **CV**, ideally as a Word file (`.docx`). A PDF is OK too; Step 7 shows you how to convert it.
- [ ] The **email account you apply for jobs with**. It must be a **Gmail / Google** account for the inbox features. (If you apply with Outlook/Hotmail, everything else still works; Claude just can't read your replies.)
- [ ] Money for **Claude Pro** (a monthly subscription; see claude.ai for the current price). The free plan does **not** include Claude Code, which this needs.

---

## A few words you'll see

- **Terminal:** a window where you type commands instead of clicking. On Windows it's called **PowerShell** (or Terminal); on a Mac it's called **Terminal**. It looks scary but you'll only type a few things.
- **Command:** a line of text you type into the terminal and then press **Enter** to run. In this guide, commands look like this:
  ```
  example command
  ```
  Copy the command exactly, paste it into the terminal, press **Enter**.
- **Pasting into a terminal:**
  - Windows: **Ctrl + V** (or right-click inside the window);
  - Mac: **Cmd + V**.
- **Folder:** same thing as a directory. Your `Documents` folder is one.
- **Claude Code:** Claude, running inside a terminal, able to work with files on your laptop. You talk to it in normal English.

> **Rule of thumb:** if a step shows red error text, **don't panic and don't keep going.** Check the **Troubleshooting** section at the bottom first, or copy the error and ask Claude (once installed) or Joshua.

---

# Part A: Accounts (on the Claude website)

## Step 1: Get Claude Pro
1. Go to **https://claude.ai** in your browser.
2. Sign up, or log in if you already have an account. Use an email you'll keep.
3. Upgrade to **Pro**: click your name / the menu at the bottom left, then **Upgrade** or **Plans**, then choose **Pro** and pay.

✅ **Worked if:** your account shows **Pro**.

## Step 2: Connect your Gmail to Claude
This lets Claude read job replies in your inbox and leave reply **drafts** for you. Claude asks before it would ever send anything, and JobTrack is set up to never send.

1. Still on claude.ai, go to **https://claude.ai/customize/connectors**. You can also click **Customize**, then **Connectors**.
2. Find **Gmail** and click **Connect**.
3. A Google window opens. **Choose the Gmail account you apply for jobs with.** This matters: it's where recruiters reply. Allow the permissions it asks for.

✅ **Worked if:** Gmail shows as **connected**.

> Your university email might be a Google account, but universities sometimes block connectors. If it won't connect, use your personal Gmail, and use that same Gmail for job applications from now on.

---

# Part B: Install the tools (one time only)

You'll install three things: **Python** (runs the website), **Git** (downloads JobTrack) and **Claude Code**.

## Step 3: Install Python

### Windows
1. Go to **https://www.python.org/downloads/** and click the big yellow **Download Python 3.x** button.
2. Open the downloaded file (in your Downloads folder).
3. ⚠️ **IMPORTANT: on the very first screen, tick the box at the bottom that says "Add python.exe to PATH".** This is the single most common mistake. Don't miss it.
4. Click **Install Now**. Wait for it to finish, then click **Close**.

### Mac
1. Go to **https://www.python.org/downloads/** and click **Download Python 3.x**.
2. Open the downloaded `.pkg` file and click **Continue / Agree / Install** through the installer.

### Check it worked
Open a terminal:
- **Windows:** press the **Start** button, type **PowerShell**, and click **Windows PowerShell**.
- **Mac:** press **Cmd + Space**, type **Terminal**, and press **Enter**.

Type this and press Enter (Windows):
```
python --version
```
On a Mac, type this instead:
```
python3 --version
```
✅ **Worked if:** it prints something like `Python 3.13.1`. **Any version 3.12 or higher is fine.**

❌ On Windows, if the **Microsoft Store opens** or it says *not recognized*: see Troubleshooting.

Leave the terminal open.

## Step 4: Install Git

### Windows
1. Go to **https://git-scm.com/downloads/win** and download the installer (64-bit, "Git for Windows Setup").
2. Run it and click **Next** on every screen. The default options are all fine. Then **Install**, then **Finish**.

### Mac
In Terminal, type:
```
git --version
```
If Git isn't installed, your Mac shows a pop-up offering to install the "command line developer tools". Click **Install**, wait (it can take 5–10 minutes), then run `git --version` again.

✅ **Worked if:** a **new** terminal window (close the old one and open a fresh one) prints something like `git version 2.47.0` when you type `git --version`.

## Step 5: Install Claude Code
In your terminal, paste the command for your system and press **Enter**.

**Windows (PowerShell):**
```
irm https://claude.ai/install.ps1 | iex
```
**Mac (Terminal):**
```
curl -fsSL https://claude.ai/install.sh | bash
```
It may sit quietly for a minute while it downloads. That's normal. Wait until you can type again.

Then:
1. **Close the terminal and open a new one** (so it notices the new install).
2. Type `claude --version` and press Enter. ✅ It should print a version number, like `2.1.211 (Claude Code)`.
3. Type `claude` and press Enter.
4. Follow the prompts. A **browser window opens** to log in. Choose to log in with your **Claude account (the Pro subscription from Step 1)**, not an API key, and approve.
5. Back in the terminal, Claude may ask a few first-time questions (theme, etc.). Pick anything.
6. Type `/exit` and press Enter to leave Claude for now.

✅ **Worked if:** `claude` opened, you logged in, and you exited.

---

# Part C: Get JobTrack

## Step 6: Download JobTrack
In the terminal, run these **one at a time** (press Enter after each):

```
cd Documents
```
This moves the terminal "into" your Documents folder.

```
git clone https://github.com/joshuaburaimoh17/jobtrack-starter jobtrack
```
This downloads JobTrack into a new folder called `jobtrack` inside Documents.

```
cd jobtrack
```
This moves the terminal into that folder. **All JobTrack commands must be run from inside this folder.**

✅ **Worked if:** you now have a folder **Documents → jobtrack**. To see it in your normal file browser, type `explorer .` (Windows) or `open .` (Mac). Note the dot.

---

# Part D: Your CV

## Step 7: Put your CV in the right place

JobTrack needs your CV as a **Word file (`.docx`)**, because it edits the text while keeping your design.

**If your CV is a PDF, Canva or Google Doc, convert it first:**
- **Google Docs:** File, then Download, then **Microsoft Word (.docx)**.
- **Canva:** Share, then Download, then file type **DOCX** (if offered). Otherwise download a PDF and convert it as below.
- **PDF:** open **https://www.office.com** (free with your college/Microsoft account), upload the PDF, open it in **Word**, check it looks right, then File, then **Save a copy / Download as .docx**.

After converting, open the .docx and **check it looks right**. Fix anything that moved.

**Tip for best results:** CVs with a simple **one-column layout** work best. Text inside **tables, text boxes or multi-column designs** can't be tailored. If your CV is like that, Claude will notice during setup and can help you rebuild it as a clean one-column CV, which also gets through employers' automatic CV filters (ATS) better.

**Now:**
1. Open the **Documents → jobtrack → cvs** folder.
2. Copy your CV into it.
3. Rename it to exactly: **`base_cv.docx`**

> ⚠️ **Windows trap:** Windows often hides the `.docx` ending. If you rename it to `base_cv.docx` while the ending is hidden, it secretly becomes `base_cv.docx.docx` and setup won't find it. To be safe, in File Explorer click **View**, then **Show**, then tick **File name extensions**, then rename the file so it reads exactly `base_cv.docx`.

✅ **Worked if:** the `cvs` folder contains `base_cv.docx` (and a `README.md`, which is fine).

---

# Part E: Make it yours

## Step 8: Think about your answers (2 minutes)
Setup is a chat where Claude asks you questions. It goes faster if you've thought about:
- **What jobs?** e.g. graduate business analyst, data analyst, IT support, grad programmes. And what you **don't** want (sales? pure coding?).
- **Where?** Which cities, how far you'd commute, and whether hybrid or remote is OK.
- **Minimum salary** you'd accept.
- **Start date:** ASAP, or would you wait for a September 2027 graduate programme?
- **Your real experience:** for each job on your CV, what did **you** actually do? Is anything on your CV a bit exaggerated? (Be honest. This stops Claude making claims you'd get caught out on in an interview.)
- **Goal:** how many applications, by when? (e.g. 100 in 3 months.)
- **Writing style:** anything you hate in cover letters (e.g. "I am writing to apply…")?

## Step 9: Run setup
In the terminal (still inside the `jobtrack` folder; check the line shows `jobtrack`), type:
```
claude
```
When Claude opens, type:
```
/setup
```
and press Enter.

Claude now guides you through everything in a chat. It takes about 15–20 minutes.

**Things to know during setup:**
- Claude will often ask **permission** before running a command ("Do you want to proceed?"). That's a safety feature. For JobTrack's own commands, choose **Yes** (or **"Yes, and don't ask again"** for commands it repeats).
- At one point it asks you to **create your website login**. You'll open a **second terminal window**, type a command it gives you, choose a username and **type a password**.
  - The password **doesn't show while you type**, not even dots. That's normal; just type it and press Enter.
  - **Opening a second terminal in the right folder:** in File Explorer, open **Documents → jobtrack**. On Windows 11, right-click an empty space and choose **Open in Terminal**. On Windows 10, type `powershell` in the address bar and press Enter. On a Mac, open a new Terminal window and type `cd Documents/jobtrack`.
- It reads your CV and shows you the sections it found. **Check they're right.**
- It asks the questions from Step 8.
- It checks your Gmail connection, does a **practice CV tailoring** (open the file it shows you; it's your CV with your design), then starts the website and gives you a tour.

✅ **Worked if:** at the end Claude shows a checklist with ✅ for app, login, CV, profile and goal (and hopefully Gmail).

## Step 10: Open your website
In your browser, go to:
```
http://127.0.0.1:8000
```
(That address means "this laptop". It only works on your own machine, while JobTrack is running.)

Log in with the username and password from setup. 🎉 **You're set up.**

---

# Part F: Using it

## Starting JobTrack each time
1. Open a terminal (Step 3 shows how).
2. Go to the folder:
   - Windows: `cd Documents\jobtrack`
   - Mac: `cd Documents/jobtrack`
3. Type `claude`.
4. Talk to it. To see the website, say **"start the app"** and go to http://127.0.0.1:8000.

## Your first job search
Say:
```
run job search
```
Claude will:
1. check your Gmail for replies;
2. find 5 jobs that fit you, checking each is still open;
3. add them to the **Job Queue** on your website;
4. make a tailored CV for each.

It then shows you a table: company, role, why it fits, and where the CV is.

**Then:**
1. Apply to the jobs yourself. Each tailored CV is in **Documents → jobtrack → cvs → applications → (this month)**, or download it from the website.
2. Tell Claude **"I applied to 1, 2 and 4"** (or press **Apply** on each job in the website). This keeps your tracker and stats accurate.

## Useful things to say
| Say | What happens |
|---|---|
| `run job search` / `run job search 10` | Inbox check, then N new jobs with tailored CVs |
| `I applied to all of them` | Marks them as applied |
| `Acme rejected me` / `I have an interview with Globex on Tuesday at 2pm` | Updates your tracker |
| `write a cover letter for the Acme job` | A Word cover letter, in your style |
| `answer this application question: …` | A written answer based on your real experience |
| `draft a reply to the recruiter at Globex` | A Gmail draft you check and send yourself |
| `mock interview me for the Globex job` | Interview practice with feedback |
| `review my applications` | What's working and what to change |
| `what can you do?` | The full list |

**Good rhythm:** a job search every 2–3 days, apply the same day, and `review my applications` once a week.

## Changing the app
It's **your** copy. You can ask Claude to change anything: "add a field for who referred me", "make it look darker", "also search for jobs in Cork". Claude saves a checkpoint first, so you can always say **"undo that last change"**.

---

# Part G: Keep your stuff safe
These are **yours** and never leave your laptop:

| File/folder in `jobtrack` | What it is |
|---|---|
| `profile.md` | Your details and preferences. Edit any time, or ask Claude to. |
| `cvs/base_cv.docx` | Your master CV. |
| `cvs/applications/` | Every tailored CV, by month. |
| `db.sqlite3` | All your applications and jobs. |
| `cover-letters/` | Your cover letters. |
| `my-job-hunt/` | Your interview stories, grad-programme deadlines, notes. |

**Back these up** now and then: copy them to OneDrive, Google Drive or iCloud. If your laptop dies, they're gone otherwise.

Updated your CV? Replace `cvs/base_cv.docx`, then tell Claude **"I updated my base CV"**.

---

# Troubleshooting

| Problem | What to do |
|---|---|
| **`python` opens the Microsoft Store**, or says *not recognized* (Windows) | Python isn't installed with PATH. Re-run the Python installer from python.org: choose **Modify**, then **Next**, tick **"Add Python to environment variables"**, then **Install**. **Close and reopen** the terminal. If the Store still opens: Start, then type **"Manage app execution aliases"**, and turn **off** the two "python" entries. |
| **`'irm' is not recognized`** | You're in Command Prompt, not PowerShell. Open **PowerShell** (Start, type PowerShell) and try again. |
| **`The token '&&' is not a valid statement separator`** | You pasted a Command Prompt command into PowerShell. Use the PowerShell command from Step 5. |
| **`claude` is not recognized / command not found** | Close the terminal and open a **new** one. Still failing? Run the Step 5 install command again, then open a new terminal. |
| **`git` is not recognized** | Install Git (Step 4), then open a **new** terminal. |
| **`fatal: destination path 'jobtrack' already exists`** | You already downloaded it. Just run `cd jobtrack`. |
| **Setup can't find your CV** | Check the file is in `jobtrack\cvs\` and is named exactly `base_cv.docx`, not `base_cv.docx.docx` (see the Windows trap in Step 7). |
| **Claude can't see your Gmail** | Go to https://claude.ai/customize/connectors and check Gmail is connected **with the right account**. Then in Claude Code type `/mcp` and press Enter (authenticate Gmail if it asks), then type `/exit` and run `claude` again. |
| **The website says "This site can't be reached"** | JobTrack isn't running. In Claude, say **"start the app"**, then refresh the page. |
| **Forgot your website password** | Tell Claude: **"reset my JobTrack password"**. |
| **Lots of "Do you want to proceed?" prompts** | Normal at first. For JobTrack's own commands choose **"Yes, and don't ask again"**. |
| **Something else / a red error** | Copy the error text and paste it to Claude with "I got this error while doing step X". It can usually fix it. Otherwise message Joshua. |

---

*Questions or stuck? Ask Claude first (it knows this project). Then ask Joshua.*
