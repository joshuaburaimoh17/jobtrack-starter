"""CV tailoring: read the base CV, rewrite three sections for a job, rebuild the .docx.

Which headings count as "summary", "skills" and "experience" comes from the
owner's profile.md (see tracker/profile.py), so this works with any CV layout
whose section headings are ordinary paragraphs (not text boxes or table cells).

Two ways tailoring happens:
  * In the app: the "Tailor CV" button calls tailor_cv_for_lead(), which needs
    ANTHROPIC_API_KEY in .env (pay-per-use API).
  * In Claude Code (no API key): the /job-search skill writes the tailored text
    itself, stores it on the lead with save_tailoring(), then calls
    archive_tailored_docx(). Same result, same files.
"""
import difflib
import json
import os
import re
from copy import deepcopy
from datetime import date
from io import BytesIO
from pathlib import Path

from django.conf import settings
from docx import Document
from docx.text.paragraph import Paragraph as DocxParagraph

from tracker.profile import cv_config

SECTION_KEYS = ('summary', 'skills', 'experience')


class CVStructureError(Exception):
    """The base CV doesn't contain the headings profile.md says it should."""


# ── Reading the CV ────────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    """Heading comparison that ignores case, spacing and a trailing colon."""
    return re.sub(r'\s+', ' ', text).strip().rstrip(':').strip().casefold()


def _open_base_cv(cv=None):
    cv = cv or cv_config()
    path = Path(cv['path'])
    if not path.exists():
        raise CVStructureError(
            f'No base CV found at {path}. Put your CV there as a .docx '
            '(or change cv.path in profile.md).'
        )
    return Document(str(path)), cv


def _section_paragraphs(doc, cv) -> dict:
    """Map each tailorable key -> list of its NON-EMPTY body paragraphs.

    Blank spacer paragraphs are left out so they keep their place in the layout.
    Raises CVStructureError if a configured heading isn't in the document.
    """
    all_headings = {_norm(h) for h in cv['headings']}
    wanted = {_norm(cv[k]): k for k in SECTION_KEYS if cv.get(k)}

    found: dict[str, list] = {}
    current = None
    for para in doc.paragraphs:
        text = para.text.strip()
        if _norm(text) in all_headings and text:
            current = wanted.get(_norm(text))
            if current:
                found[current] = []
            continue
        if current and text:
            found[current].append(para)

    missing = [cv[k] for k in SECTION_KEYS if cv.get(k) and k not in found]
    if missing:
        present = [p.text.strip() for p in doc.paragraphs
                   if p.text.strip() and len(p.text.strip()) < 40][:25]
        raise CVStructureError(
            f'Could not find heading(s) {missing} in {cv["path"].name}. '
            f'Check the cv: section of profile.md matches your CV exactly. '
            f'Short lines found in the CV (likely headings): {present}. '
            'If your headings are inside a table or text box, they cannot be read; '
            'move them to normal paragraphs.'
        )
    return found


def read_base_sections() -> dict:
    """{'summary': str, 'skills': str, 'experience': str} from the base CV.
    Keys for sections not configured in profile.md come back as ''."""
    doc, cv = _open_base_cv()
    found = _section_paragraphs(doc, cv)
    return {k: '\n'.join(p.text.strip() for p in found.get(k, [])) for k in SECTION_KEYS}


# ── Writing the CV ────────────────────────────────────────────────────────────

def _replace_para_text(para, new_text: str) -> None:
    """Keep the first run's formatting (font, bold, size) and swap the text."""
    if not para.runs:
        para.add_run(new_text)
        return
    para.runs[0].text = new_text
    for run in para.runs[1:]:
        run.text = ''


def _replace_section(content_paras: list, new_lines: list) -> None:
    """Line i of the new text goes into paragraph i, so it inherits that
    paragraph's style. Extra lines copy the last paragraph's style; surplus old
    paragraphs are removed."""
    if not content_paras:
        return
    new_lines = [line for line in new_lines if line.strip()]
    if not new_lines:
        return

    n_old = len(content_paras)
    n_new = len(new_lines)

    for i in range(min(n_old, n_new)):
        _replace_para_text(content_paras[i], new_lines[i])

    for para in reversed(content_paras[n_new:]):
        para._element.getparent().remove(para._element)

    if n_new > n_old:
        anchor = content_paras[n_old - 1]
        for line in new_lines[n_old:]:
            new_elem = deepcopy(anchor._element)
            anchor._element.addnext(new_elem)
            new_para = DocxParagraph(new_elem, anchor._parent)
            _replace_para_text(new_para, line)
            anchor = new_para


def _build_tailored_doc(tailored_data: dict):
    doc, cv = _open_base_cv()
    found = _section_paragraphs(doc, cv)
    for key in SECTION_KEYS:
        if key in found and tailored_data.get(key):
            _replace_section(found[key], tailored_data[key].split('\n'))
    return doc


def build_tailored_docx(lead) -> tuple:
    """Build the tailored CV in memory from the lead's stored tailoring.

    Returns (BytesIO, filename). Raises ValueError if the lead has no stored
    tailoring data.
    """
    if not lead.cv_tailored_json:
        raise ValueError('No tailored CV data stored for this lead.')

    doc = _build_tailored_doc(json.loads(lead.cv_tailored_json))

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    company_slug = re.sub(r'[^\w]', '_', lead.company)[:30]
    role_slug = re.sub(r'[^\w]', '_', lead.role)[:30]
    filename = f"{company_slug}_{role_slug}_{date.today()}.docx"
    return buffer, filename


def archive_tailored_docx(lead) -> Path:
    """Save a copy of the tailored CV under CV_APPLICATIONS_PATH/<Month YYYY>/.

    Separate from the on-demand download in build_tailored_docx(), which keeps
    working purely from cv_tailored_json even if this write fails.
    """
    buffer, filename = build_tailored_docx(lead)
    month_dir = Path(settings.CV_APPLICATIONS_PATH) / date.today().strftime('%B %Y')
    month_dir.mkdir(parents=True, exist_ok=True)
    dest = month_dir / filename
    dest.write_bytes(buffer.getvalue())
    return dest


def save_tailoring(lead, tailored: dict, changes_made: str) -> None:
    """Store tailored text on a lead so the app's diff view and download work.

    `tailored` has any of 'summary' / 'skills' / 'experience' (missing keys keep
    the original text). Used by the in-app button AND by Claude in-session.
    """
    original = read_base_sections()
    merged = {k: (tailored.get(k) or original[k]) for k in SECTION_KEYS}
    lead.cv_original_text = '\n'.join(original[k] for k in SECTION_KEYS if original[k])
    lead.cv_tailored_text = '\n'.join(merged[k] for k in SECTION_KEYS if merged[k])
    lead.cv_changes = changes_made
    lead.cv_tailored_json = json.dumps(dict(merged, changes_made=changes_made))
    lead.save(update_fields=['cv_original_text', 'cv_tailored_text', 'cv_changes', 'cv_tailored_json'])


def compute_diff(original_text: str, tailored_text: str) -> list:
    orig_lines = original_text.splitlines()
    tail_lines = tailored_text.splitlines()
    matcher = difflib.SequenceMatcher(None, orig_lines, tail_lines)
    result = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for o, t in zip(orig_lines[i1:i2], tail_lines[j1:j2]):
                result.append(((o, 'same'), (t, 'same')))
        elif tag == 'replace':
            orig_chunk = orig_lines[i1:i2]
            tail_chunk = tail_lines[j1:j2]
            for k in range(max(len(orig_chunk), len(tail_chunk))):
                o = orig_chunk[k] if k < len(orig_chunk) else ''
                t = tail_chunk[k] if k < len(tail_chunk) else ''
                result.append(((o, 'removed' if o else 'same'), (t, 'added' if t else 'same')))
        elif tag == 'delete':
            for o in orig_lines[i1:i2]:
                result.append(((o, 'removed'), ('', 'same')))
        elif tag == 'insert':
            for t in tail_lines[j1:j2]:
                result.append((('', 'same'), (t, 'added')))
    return result


# ── In-app tailoring via the Anthropic API (optional) ─────────────────────────

TAILORING_RULES = """\
1. Rewrite the summary from scratch for this specific role and company: name the company, the type of work, and the candidate's most relevant experience. 3-4 sentences. It must be meaningfully different from the input, not a few words swapped.
2. Mirror the exact language and keywords from the job description throughout. ATS systems scan for exact keyword matches.
3. Reorder the skills so the most relevant come first, both the lines and the items within each line.
4. Rewrite experience bullet points to emphasise what is most relevant to this role. Use action verbs. Keep numbers that already exist; never invent metrics. Mirror job-description language where it fits naturally.
5. NEVER invent skills, qualifications, employers, tools or experience that are not already in the CV. Never upgrade what the candidate did (e.g. "documented" must not become "built" or "configured").
6. Keep the same line structure as the original: same number of lines in the same order for skills and experience, header lines (job titles, employers, dates) unchanged, and the same line format (e.g. "Category:  a, b, c", bullets starting with "-" or "•").
7. In changes_made, be specific about what you changed and why, e.g. "Moved SQL to the front of Technical skills because the role is data-heavy; added 'stakeholder reporting' to the second bullet of the most recent job to match the JD."
"""


def _call_claude(original: dict, job_description: str, role: str, company: str,
                 honesty_rules: str = '') -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    sections = '\n\n'.join(
        f'CURRENT {k.upper()}:\n{v}' for k, v in original.items() if v
    )
    keys = ', '.join(f'"{k}": "..."' for k, v in original.items() if v)
    honesty = f'\nCANDIDATE-SPECIFIC HONESTY RULES (override everything else):\n{honesty_rules}\n' if honesty_rules else ''
    prompt = f"""You are a professional CV writer and ATS optimisation expert. Tailor this graduate's CV for one specific job so it passes ATS filters and stands out to hiring managers. Make meaningful, substantive changes.

JOB ROLE: {role}
COMPANY: {company}

JOB DESCRIPTION:
{job_description[:4000]}

{sections}

RULES:
{TAILORING_RULES}{honesty}
Return ONLY valid JSON with no markdown fences, no preamble:
{{{keys}, "changes_made": "..."}}"""

    message = client.messages.create(
        model=os.environ.get('CLAUDE_MODEL', 'claude-opus-5-5'),
        max_tokens=4096,
        messages=[{'role': 'user', 'content': prompt}],
    )
    raw = message.content[0].text.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


def tailor_cv_for_lead(lead) -> None:
    """In-app button: tailor via the API and store the result on the lead."""
    if not settings.ANTHROPIC_API_KEY:
        raise RuntimeError(
            'No ANTHROPIC_API_KEY in .env. Either add one, or ask Claude Code '
            '"tailor my CV for lead %d" (free with your Claude plan).' % lead.pk
        )
    from tracker.profile import load_settings

    original = read_base_sections()
    tailored = _call_claude(
        original=original,
        job_description=lead.job_description,
        role=lead.role,
        company=lead.company,
        honesty_rules=str(load_settings().get('honesty_rules') or ''),
    )
    save_tailoring(lead, tailored, tailored.get('changes_made', ''))
