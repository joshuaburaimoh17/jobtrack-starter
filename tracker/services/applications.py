"""Shared application logic, used by both the web views and management commands
(so Claude can do from the terminal exactly what the buttons do)."""
from datetime import date

from django.utils import timezone

from tracker.models import Application, JobLead


def mark_lead_applied(lead: JobLead, applied_on: date | None = None) -> tuple[Application, bool]:
    """Convert a lead into a tracked Application and link the two.

    Returns (application, created). If the lead already has an application,
    returns it with created=False and changes nothing.
    """
    if lead.application_id:
        return lead.application, False

    application = Application.objects.create(
        company=lead.company,
        role=lead.role,
        location=lead.location,
        salary_range=lead.salary_range,
        date_applied=applied_on or date.today(),
        status=Application.STATUS_APPLIED,
        status_updated_at=timezone.now(),
        job_url=lead.source_url,
        job_description=lead.job_description,
    )
    lead.application = application
    lead.status = JobLead.STATUS_APPLIED
    lead.save(update_fields=['application', 'status'])
    return application, True


def set_status(application: Application, new_status: str, note: str = '') -> bool:
    """Change an application's status the right way: status_updated_at only
    moves on a REAL change (follow-up logic depends on it), and an optional
    dated note is appended. Returns True if the status changed."""
    valid = {value for value, _ in Application.STATUS_CHOICES}
    if new_status not in valid:
        raise ValueError(f'Unknown status {new_status!r}. Valid: {sorted(valid)}')
    changed = new_status != application.status
    if changed:
        application.status = new_status
        application.status_updated_at = timezone.now()
    if note:
        line = f'[{date.today():%d %b %Y}] {note}'
        application.notes = f'{application.notes}\n{line}' if application.notes else line
    application.save()
    return changed
