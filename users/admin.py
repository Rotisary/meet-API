from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class NewUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'category', 'date_joined', 'last_login')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(User, NewUserAdmin)
