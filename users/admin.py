from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):

    ordering = ["email"]

    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "password"
    ]

    fieldsets = (
        (None,
          {
              "fields": ("email", "password")
          }
          ),

        ("Personal Info", {
            "fields": (
                "first_name",
                "last_name",
                "phone_number",
                "profile_image"
                
            )
        }),

        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions"
            )
        }),

        ("Important dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "password1",
                "password2",
                "is_staff",
                "is_superuser"
            ),
        }),
    )



admin.site.register(User, CustomUserAdmin)