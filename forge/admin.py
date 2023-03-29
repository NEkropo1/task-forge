from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from forge.models import Worker, Position, TaskType, Project


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
                        "hire_date",
                        "position",
                        "status",
                        "team",
                    )
                },
            ),
        )
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'is_completed', 'start_date', 'deadline')
    list_filter = ('manager', 'is_completed')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'
    fieldsets = (
        (None, {'fields': ('name', 'description', 'manager')}),
        ('Dates', {'fields': ('start_date', 'deadline', 'is_completed')}),
    )

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
