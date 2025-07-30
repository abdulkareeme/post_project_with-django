from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser as User

# Register your models here.
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('get_full_name', 'email', 'is_staff')

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'full name'

# admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)