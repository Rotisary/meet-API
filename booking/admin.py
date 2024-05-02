from django.contrib import admin
from .models import Illness, Appointment


class IllnessAdmin(admin.ModelAdmin):
    list_display = ['patient', 'body_part', 'specific_illness', 'age', 'created_at']
    search_fields = ['body_part', 'illness', 'patient__username']
    readonly_fields = ['created_at']


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['owner', 'patient', 'date_of_appointment', 'time_of_appointment', 'created_at']
    search_fields = ['owner', 'patient']
    readonly_fields = ['created_at']


admin.site.register(Illness, IllnessAdmin)
admin.site.register(Appointment, AppointmentAdmin)
