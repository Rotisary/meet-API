from django.contrib import admin
from .models import Illness


class IllnessAdmin(admin.ModelAdmin):
    list_display = ['patient', 'body_part', 'specific_illness', 'age', 'created_at']
    search_fields = ['body_part', 'illness', 'patient__username']
    readonly_fields = ['created_at']


admin.site.register(Illness, IllnessAdmin)
