from datetime import date, datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ApplicationForm, JobLeadForm
from .models import Application, GoalSetting, JobLead

_VALID_SORT_KEYS = {'date_applied', '-date_applied', 'company', 'status'}


def _status_counts():
    """Counts for every Application status, zero-filled, in STATUS_CHOICES order."""
    raw = dict(
        Application.objects.values('status')
        .annotate(n=Count('id'))
        .values_list('status', 'n')
    )
    return [
        {'status': value, 'label': label, 'count': raw.get(value, 0)}
        for value, label in Application.STATUS_CHOICES
    ]


# ── Dashboard ─────────────────────────────────────────────────────────────────

def dashboard(request):
    today = date.today()
    status_counts = _status_counts()
    offers = next(
        (s['count'] for s in status_counts if s['status'] == Application.STATUS_OFFER), 0
    )

    goal = GoalSetting.load()
    goal_count = Application.objects.filter(
        date_applied__gte=goal.window_start,
        date_applied__lte=goal.window_end,
    ).count()
    goal_percent = min(100, round(goal_count / goal.target * 100)) if goal.target else 0
    goal_label = f"{goal.window_start:%b}–{goal.window_end:%b} {goal.window_end.year} target"

    return render(request, 'tracker/dashboard.html', {
        'total': Application.objects.count(),
        'last_7_days': Application.objects.filter(
            date_applied__gte=today - timedelta(days=7)
        ).count(),
        'leads_in_queue': JobLead.objects.filter(
            status__in=[JobLead.STATUS_NEW, JobLead.STATUS_READY]
        ).count(),
        'offers': offers,
        'status_counts': status_counts,
        'recent_applications': Application.objects.all()[:5],
        'goal': goal,
        'goal_count': goal_count,
        'goal_percent': goal_percent,
        'goal_label': goal_label,
    })


def analytics(request):
    total = Application.objects.count()
    status_counts = _status_counts()

    responded = Application.objects.exclude(status=Application.STATUS_APPLIED).count()
    response_rate = round(responded / total * 100) if total else 0

    # Applications per week, last 12 ISO weeks, zero-filled
    today = date.today()
    this_week_start = today - timedelta(days=today.weekday())
    week_starts = [this_week_start - timedelta(weeks=i) for i in range(11, -1, -1)]

    weekly_raw = {
        row['week'].date() if hasattr(row['week'], 'date') else row['week']: row['n']
        for row in (
            Application.objects.filter(date_applied__gte=week_starts[0])
            .annotate(week=TruncWeek('date_applied'))
            .values('week')
            .annotate(n=Count('id'))
        )
    }
    weekly_labels = [w.strftime('%b %d') for w in week_starts]
    weekly_counts = [weekly_raw.get(w, 0) for w in week_starts]

    chart_data = {
        'weekly_labels': weekly_labels,
        'weekly_counts': weekly_counts,
        'status_labels': [s['label'] for s in status_counts],
        'status_values': [s['count'] for s in status_counts],
    }

    return render(request, 'tracker/analytics.html', {
        'total': total,
        'response_rate': response_rate,
        'responded': responded,
        'status_counts': status_counts,
        'chart_data': chart_data,
        'monthly_rows': _monthly_rows(today),
    })


_INTERVIEW_STATUSES = (
    Application.STATUS_INTERVIEW_SCHEDULED,
    Application.STATUS_INTERVIEW_DONE,
    Application.STATUS_OFFER,
)


def _monthly_rows(today):
    """One row per month with applications, newest first. Outcome columns use
    each application's *current* status, so older months fill in over time."""
    rows = (
        Application.objects
        .annotate(month=TruncMonth('date_applied'))
        .values('month')
        .annotate(
            applied=Count('id'),
            responded=Count('id', filter=~Q(status=Application.STATUS_APPLIED)),
            interviews=Count('id', filter=Q(status__in=_INTERVIEW_STATUSES)),
            offers=Count('id', filter=Q(status=Application.STATUS_OFFER)),
            rejected=Count('id', filter=Q(status=Application.STATUS_REJECTED)),
        )
        .order_by('month')
    )
    rows = [
        dict(row, month=row['month'].date() if hasattr(row['month'], 'date') else row['month'])
        for row in rows
    ]
    this_month = today.replace(day=1)
    if rows and rows[-1]['month'] < this_month:
        rows.append(dict(month=this_month, applied=0, responded=0,
                         interviews=0, offers=0, rejected=0))

    result = []
    previous = None
    for row in rows:
        month = row['month']
        is_current = (month.year, month.month) == (today.year, today.month)
        if is_current:
            days = today.day
        else:
            next_month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
            days = (next_month - month).days
        applied = row['applied']
        result.append(dict(
            row,
            month=month,
            is_current=is_current,
            per_day=round(applied / days, 1),
            response_rate=round(row['responded'] / applied * 100) if applied else 0,
            # A part-month against a full month would always look like a drop.
            change=None if previous is None or is_current else applied - previous,
        ))
        previous = applied
    result.reverse()
    return result


# ── Applications ─────────────────────────────────────────────────────────────


def application_list(request):
    qs = Application.objects.all()

    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    sort = request.GET.get('sort', '-date_applied').strip()

    if search:
        qs = qs.filter(Q(company__icontains=search) | Q(role__icontains=search))
    if status_filter:
        qs = qs.filter(status=status_filter)
    if sort in _VALID_SORT_KEYS:
        qs = qs.order_by(sort)

    return render(request, 'tracker/application_list.html', {
        'applications': qs,
        'search': search,
        'status_filter': status_filter,
        'sort': sort,
        'status_choices': Application.STATUS_CHOICES,
        'total': qs.count(),
    })


def application_add(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.status_updated_at = timezone.now()
            application.save()
            messages.success(request, 'Application added.')
            return redirect('tracker:application_list')
    else:
        form = ApplicationForm(initial={'date_applied': date.today()})
    return render(request, 'tracker/application_form.html', {'form': form})


def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)
    return render(request, 'tracker/application_detail.html', {
        'application': application,
        'status_choices': Application.STATUS_CHOICES,
    })


def application_edit(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if request.method == 'POST':
        old_status = application.status
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save(commit=False)
            if application.status != old_status:
                application.status_updated_at = timezone.now()
            application.save()
            messages.success(request, 'Application updated.')
            return redirect('tracker:application_detail', pk=pk)
    else:
        form = ApplicationForm(instance=application)
    return render(request, 'tracker/application_form.html', {
        'form': form,
        'application': application,
    })


def application_delete(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Application deleted.')
        return redirect('tracker:application_list')
    return render(request, 'tracker/application_confirm_delete.html', {
        'application': application,
    })


@require_POST
def update_status(request, pk):
    from .services.applications import set_status

    application = get_object_or_404(Application, pk=pk)
    try:
        set_status(application, request.POST.get('status', ''))
        messages.success(request, f'Status updated to {application.get_status_display()}.')
    except ValueError:
        messages.error(request, 'Unknown status.')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('tracker:application_detail', pk=pk)


# ── Job Queue ─────────────────────────────────────────────────────────────────

_TAB_STATUS = {
    'new': JobLead.STATUS_NEW,
    'ready': JobLead.STATUS_READY,
    'applied': JobLead.STATUS_APPLIED,
    'dismissed': JobLead.STATUS_DISMISSED,
}


def job_queue(request):
    from .services.utils import has_location_mismatch

    tab = request.GET.get('tab', 'new')
    if tab not in _TAB_STATUS:
        tab = 'new'

    leads = JobLead.objects.filter(status=_TAB_STATUS[tab])
    flagged_pks = {lead.pk for lead in leads if has_location_mismatch(lead)}

    tabs = [
        ('new', 'New', JobLead.objects.filter(status=JobLead.STATUS_NEW).count()),
        ('ready', 'Ready to Apply', JobLead.objects.filter(status=JobLead.STATUS_READY).count()),
        ('applied', 'Applied', JobLead.objects.filter(status=JobLead.STATUS_APPLIED).count()),
        ('dismissed', 'Dismissed', JobLead.objects.filter(status=JobLead.STATUS_DISMISSED).count()),
    ]

    return render(request, 'tracker/job_queue.html', {
        'leads': leads,
        'tab': tab,
        'tabs': tabs,
        'flagged_pks': flagged_pks,
    })


def job_lead_detail(request, pk):
    from .services.utils import has_location_mismatch

    lead = get_object_or_404(JobLead, pk=pk)
    diff = None
    if lead.cv_original_text and lead.cv_tailored_text:
        from .services.cv_tailor import compute_diff
        diff = compute_diff(lead.cv_original_text, lead.cv_tailored_text)
    return render(request, 'tracker/job_lead_detail.html', {
        'lead': lead,
        'is_flagged': has_location_mismatch(lead),
        'diff': diff,
    })


@require_POST
def dismiss_lead(request, pk):
    lead = get_object_or_404(JobLead, pk=pk)
    lead.status = JobLead.STATUS_DISMISSED
    lead.save()
    messages.success(request, 'Lead dismissed.')
    return redirect('tracker:job_queue')


@require_POST
def mark_ready(request, pk):
    lead = get_object_or_404(JobLead, pk=pk)
    lead.status = JobLead.STATUS_READY
    lead.save()
    messages.success(request, 'Lead marked as ready to apply.')
    return redirect('tracker:job_lead_detail', pk=pk)


@require_POST
def mark_applied(request, pk):
    """Convert a lead into a tracked Application and link the two."""
    from .services.applications import mark_lead_applied

    lead = get_object_or_404(JobLead, pk=pk)
    application, created = mark_lead_applied(lead)
    if not created:
        messages.info(request, 'This lead already has a linked application.')
    else:
        messages.success(request, f'Application created for {lead.role} at {lead.company}.')
    return redirect('tracker:application_detail', pk=application.pk)


def add_job(request):
    if request.method == 'POST':
        form = JobLeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            messages.success(request, 'Job lead added.')
            return redirect('tracker:job_lead_detail', pk=lead.pk)
    else:
        form = JobLeadForm()
    return render(request, 'tracker/add_job.html', {'form': form})


# ── CV Tailoring ──────────────────────────────────────────────────────────────

@require_POST
def tailor_cv_view(request, pk):
    lead = get_object_or_404(JobLead, pk=pk)
    try:
        from .services.cv_tailor import archive_tailored_docx, tailor_cv_for_lead
        tailor_cv_for_lead(lead)
        try:
            archive_tailored_docx(lead)
            messages.success(request, 'CV tailored successfully.')
        except Exception as archive_error:
            messages.warning(request, f'CV tailored, but saving a copy to the archive failed: {archive_error}')
    except Exception as e:
        messages.error(request, f'CV tailoring failed: {e}')
    return redirect('tracker:job_lead_detail', pk=pk)


def download_cv(request, pk):
    lead = get_object_or_404(JobLead, pk=pk)

    if lead.cv_tailored_json:
        from .services.cv_tailor import build_tailored_docx
        try:
            buffer, filename = build_tailored_docx(lead)
        except Exception as e:
            messages.error(request, f'Could not generate the tailored CV: {e}')
            return redirect('tracker:job_lead_detail', pk=pk)
        return FileResponse(buffer, as_attachment=True, filename=filename)

    messages.error(request, 'No tailored CV available — run Tailor CV first.')
    return redirect('tracker:job_lead_detail', pk=pk)


def _parse_month_dir(month_name: str):
    try:
        return datetime.strptime(month_name, '%B %Y')
    except ValueError:
        return None


def cv_archive(request):
    root = Path(settings.CV_APPLICATIONS_PATH)
    all_dirs = [d for d in root.iterdir() if d.is_dir()] if root.exists() else []
    # Only "<Month YYYY>" folders belong here; any other folder you keep in
    # cvs/applications/ is ignored by this page.
    month_dirs = [(d, _parse_month_dir(d.name)) for d in all_dirs]
    month_dirs = [(d, key) for d, key in month_dirs if key is not None]
    month_dirs.sort(key=lambda pair: pair[1], reverse=True)
    month_dirs = [d for d, _ in month_dirs]

    months = [
        {
            'name': month_dir.name,
            'files': sorted((f.name for f in month_dir.iterdir() if f.is_file()), reverse=True),
        }
        for month_dir in month_dirs
    ]
    return render(request, 'tracker/cv_archive.html', {'months': months})


def download_archived_cv(request, month, filename):
    root = Path(settings.CV_APPLICATIONS_PATH).resolve()
    path = (root / month / filename).resolve()
    if root not in path.parents or not path.is_file():
        raise Http404
    return FileResponse(open(path, 'rb'), as_attachment=True, filename=filename)
