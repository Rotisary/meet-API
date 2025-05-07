from django.contrib import admin
from .models import Complaint, Meet, Appointment, Symptom


class SymptomAdmin(admin.ModelAdmin):
    list_display = ['Name', 'ID']
    search_fields = ['Name', 'ID']


class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['patient', 'sex', 'year_of_birth', 'age_group', 'created_at']
    search_fields = ['symptoms__Name', 'patient__username', 'treated_by__user__username']
    readonly_fields = ['created_at']
    list_select_related = ['patient', 'treated_by']


class MeetAdmin(admin.ModelAdmin):
    list_display = ['ID', 'doctor', 'patient', 'created_at']
    search_fields = ['ID', 'doctor__user__username', 'patient__username']
    readonly_fields = ['created_at']
    list_select_related = ['doctor', 'patient']


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['owner', 'patient', 'date_of_appointment', 'time_of_appointment', 'created_at']
    search_fields = ['owner__user__username', 'patient__username']
    readonly_fields = ['created_at']


admin.site.register(Symptom, SymptomAdmin)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Meet, MeetAdmin)
