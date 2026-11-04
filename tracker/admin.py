from django.contrib import admin

from .models import Application, GoalSetting, JobLead


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['role', 'company', 'status', 'date_applied', 'follow_up_date']


@admin.register(JobLead)
class JobLeadAdmin(admin.ModelAdmin):
    list_display = ['role', 'company', 'location', 'status', 'date_found']


@admin.register(GoalSetting)
class GoalSettingAdmin(admin.ModelAdmin):
    list_display = ['target', 'window_start', 'window_end']

    def has_add_permission(self, request):
        # Singleton — GoalSetting.load() always uses pk=1, block extra rows.
        return not GoalSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
