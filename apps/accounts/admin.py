from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, Permission, RolePermission

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'is_verified', 'custom_role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('company', 'industry', 'phone', 'country', 'is_verified', 'custom_role', 'failed_login_attempts', 'is_locked')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(RolePermission)
