"""Reads the owner's profile.md — the one file that makes this JobTrack *yours*.

profile.md is plain markdown for humans and Claude, with ONE fenced ```yaml block
holding the settings the app itself needs (mainly the CV heading map). Everything
else in the file (targets, honesty rules, writing style) is read by Claude, not code.

If profile.md doesn't exist yet (before /setup has run), sensible defaults are used.
"""
import re
from pathlib import Path

import yaml
from django.conf import settings


DEFAULT_CV = {
    'path': 'cvs/base_cv.docx',
    # Which heading in YOUR CV holds each tailorable part. Set any to null if
    # your CV doesn't have that section — it will be left untouched.
    'summary': 'Professional Summary',
    'skills': 'Skills',
    'experience': 'Work Experience',
    # Every section heading in the CV, in order. Used to know where a section ends.
    'headings': [
        'Professional Summary',
        'Work Experience',
        'Projects',
        'Skills',
        'Education',
        'Achievements',
    ],
}

_YAML_BLOCK = re.compile(r'```ya?ml\s*\n(.*?)```', re.DOTALL)


class ProfileError(Exception):
    """profile.md exists but can't be understood."""


def profile_path() -> Path:
    return Path(settings.PROFILE_PATH)


def _read_yaml_block(text: str) -> dict:
    match = _YAML_BLOCK.search(text)
    if not match:
        return {}
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        raise ProfileError(f'The yaml block in profile.md is not valid YAML: {e}') from e
    if not isinstance(data, dict):
        raise ProfileError('The yaml block in profile.md must be a set of "key: value" settings.')
    return data


def load_settings() -> dict:
    """The parsed yaml block from profile.md ({} if there is no profile yet).
    Read fresh every time (it's tiny), so edits apply without a restart."""
    path = profile_path()
    if not path.exists():
        return {}
    return _read_yaml_block(path.read_text(encoding='utf-8'))


def cv_config() -> dict:
    """CV settings from profile.md merged over the defaults."""
    cv = dict(DEFAULT_CV)
    cv.update((load_settings().get('cv') or {}))

    headings = [h for h in (cv.get('headings') or []) if h]
    # The three tailorable sections must always count as headings.
    for key in ('summary', 'skills', 'experience'):
        if cv.get(key) and cv[key] not in headings:
            headings.append(cv[key])
    cv['headings'] = headings

    if not any(cv.get(k) for k in ('summary', 'skills', 'experience')):
        raise ProfileError('profile.md cv: at least one of summary / skills / experience must be set.')

    path = Path(cv['path'])
    cv['path'] = path if path.is_absolute() else Path(settings.BASE_DIR) / path
    return cv
