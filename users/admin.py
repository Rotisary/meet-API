from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, DoctorReview, APIUser


class NewUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'category', 'date_joined', 'last_login')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ('writer', 'doctor', 'stars', 'created_at')
    search_fields = ('writer__username', 'doctor__user__username')
    readonly_fields = ('created_at', )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'patient_type', 'created_at')
    search_fields = ('user__username', )
    readonly_fields = ('created_at', )


    # filter_horizontal = ()
    # list_filter = ()
    # ordering = ()


admin.site.register(User, NewUserAdmin)
admin.site.register(APIUser)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(DoctorReview, DoctorReviewAdmin)
