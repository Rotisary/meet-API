from django.contrib import admin
from .models import IllnessDetail


class IllnessDetailAdmin(admin.ModelAdmin):
    list_display = ['patient', 'body_part', 'illness', 'age', 'created_at']
    search_fields = ['body_part', 'illness', 'patient__username']
    readonly_fields = ['created_at']


admin.site.register(IllnessDetail, IllnessDetailAdmin)
