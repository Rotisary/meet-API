from django.contrib import admin
from .models import Complaint, Appointment, Symptom


class SymptomAdmin(admin.ModelAdmin):
    list_display = ['Name', 'ID']
    search_fields = ['Name', 'ID']


class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['patient', 'sex', 'year_of_birth', 'age_group', 'created_at']
    search_fields = ['body_part', 'illness', 'patient__username']
    readonly_fields = ['created_at']


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['owner', 'patient', 'date_of_appointment', 'time_of_appointment', 'created_at']
    search_fields = ['owner', 'patient']
    readonly_fields = ['created_at']


admin.site.register(Symptom, SymptomAdmin)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(Appointment, AppointmentAdmin)
