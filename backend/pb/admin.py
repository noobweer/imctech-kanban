from django.contrib import admin
from .models import Project, Board, Column, Invite, Task, TaskComment, TaskCommentReadState


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
        "kind",
        "position",
        "status",
        "sum_tasks",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "board__name")
    list_filter = ("status", "kind", "created_at", "board")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("board",)


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "board",
        "max_uses",
        "used_count",
        "expire_at",
        "is_active",
        "created_by",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "expire_at", "created_at", "board")
    search_fields = ("id", "board__name", "created_by__username")
    readonly_fields = ("id", "used_count", "created_at", "updated_at")
    raw_id_fields = ("board", "created_by")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "column",
        "owner",
        "priority",
        "deadline",
        "position",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "priority",
        "deadline",
        "created_at",
        "column",
        "owner",
    )
    search_fields = ("title", "content", "owner__username", "column__name")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("column", "owner")
    filter_horizontal = ("assignees",)


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "owner", "is_deleted", "created_at", "updated_at")
    list_filter = ("is_deleted", "created_at", "updated_at", "task__column__board")
    search_fields = ("content", "owner__username", "task__title")
    readonly_fields = ("id", "created_at", "updated_at", "deleted_at")
    raw_id_fields = ("task", "owner")


@admin.register(TaskCommentReadState)
class TaskCommentReadStateAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "user", "last_read_at", "updated_at")
    list_filter = ("last_read_at", "updated_at", "task__column__board")
    search_fields = ("task__title", "user__username")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("task", "user")
