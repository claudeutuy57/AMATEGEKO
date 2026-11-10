from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'preferred_language')
    fieldsets = UserAdmin.fieldsets + (
        ('Driving School Info', {
            'fields': ('role', 'phone_number', 'national_id', 'preferred_language', 'target_exam_date', 'avatar', 'bio'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Driving School Info', {
            'fields': ('role', 'phone_number', 'preferred_language'),
        }),
    )

