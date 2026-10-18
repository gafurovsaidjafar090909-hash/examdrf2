
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

@admin.register(Account)
class AccountAdmin(UserAdmin):
    model = Account
    list_display = ('id', 'phone_number', 'is_staff', 'is_active')
    search_fields = ('phone_number',)
    ordering = ('id',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number',
                'password1',
                'password2',
                'is_staff',
                'is_superuser',
            ),
        }),
    )
