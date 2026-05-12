from django.contrib import admin
from .models import Project, Board, Column


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "project",
        "owner",
        "status",
        "tasks_total",
        "tasks_done",
        "progress_percent",
        "created_at",
    )
    search_fields = ("name", "owner__username")
    list_filter = ("status", "created_at")
    raw_id_fields = (
        "owner",
        "project",
    )  # Use raw_id_fields for FK to User and Project to avoid huge dropdowns
    filter_horizontal = ("members",)  # For ManyToMany field
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "board",
        "position",
        "status",
        "sum_tasks",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "board__name")
    list_filter = ("status", "created_at", "board")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("board",)
