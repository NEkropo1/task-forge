from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from forge.models import Worker


# Register your models here.
@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("about",)
    fieldsets = UserAdmin.fieldsets + (
        (("Additional info", {"fields": (
            "salary",
            "about",
            "hire_date",
            "position",
            "status",
            "team",
        )}),)
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "salary",
                        "about",
                        "hire_date"
                        "position",
                        "status",
                        "team",
                    )
                },
            ),
        )
    )
