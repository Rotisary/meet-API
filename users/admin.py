from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import UserCreationForm 
from .models import User, Profile, DoctorReview


class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'category', 'first_name', 'last_name', 'password1', 'password2')
        

class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'category', 'password1', 'password2', 'phone_number'),
        }),
    )


class NewUserAdmin(CustomUserAdmin):
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
admin.site.register(Profile, ProfileAdmin)
admin.site.register(DoctorReview, DoctorReviewAdmin)
