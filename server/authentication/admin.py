from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account

@admin.register(Account)
class AccountAdmin(UserAdmin):
    """
    This class customizes the admin panel for viewing, filtering, creating, and editing accounts.
    """
    search_fields = ('username','email', 'first_name', 'last_name',)
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
    readonly_fields = ('id', 'date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('id', 'username', 'email', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Activity', {'fields': ('date_joined', 'last_login')})
    )
    # fields that will be displayed when creating an account from the admin panel
    add_fieldsets = (
        (None, {
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')}
         ),
    )

