import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class BoardStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    ARCHIVED = "archived", _("Archived")


class Board(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        related_name="boards",
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="boards",
        blank=True,
    )
    status = models.CharField(
        max_length=10,
        choices=BoardStatus.choices,
        default=BoardStatus.ACTIVE,
    )
    description = models.TextField(blank=True, null=True)
    tasks_total = models.IntegerField(default=0)
    tasks_done = models.IntegerField(default=0)
    progress_percent = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.tasks_total < 0:
            raise ValidationError(_("Total tasks cannot be negative."))
        if self.tasks_done < 0:
            raise ValidationError(_("Done tasks cannot be negative."))
        if self.tasks_done > self.tasks_total:
            raise ValidationError(_("Done tasks cannot exceed total tasks."))
        if not (0 <= self.progress_percent <= 100):
            raise ValidationError(_("Progress percentage must be between 0 and 100."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ColumnStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    ARCHIVED = "archived", _("Archived")


class ColumnKind(models.TextChoices):
    BOARD = "board", _("Board")
    BACKLOG = "backlog", _("Backlog")
    ARCHIVE = "archive", _("Archive")


class Column(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="columns",
    )
    name = models.CharField(max_length=255)
    kind = models.CharField(
        max_length=20,
        choices=ColumnKind.choices,
        default=ColumnKind.BOARD,
    )
    position = models.PositiveIntegerField()
    status = models.CharField(
        max_length=10,
        choices=ColumnStatus.choices,
        default=ColumnStatus.ACTIVE,
    )
    sum_tasks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]

    def clean(self):
        if self.sum_tasks < 0:
            raise ValidationError(_("Sum of tasks cannot be negative."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.board.name})"


class Invite(models.Model):
    """Invite link for a board. Soft-deleted via is_active=False."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="invites",
    )
    # null means Unlimited uses
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    expire_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_invites",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.max_uses is not None and self.max_uses == 0:
            raise ValidationError(_("max_uses cannot be 0. Use null for unlimited."))
        if self.max_uses is not None and self.used_count > self.max_uses:
            raise ValidationError(_("used_count cannot exceed max_uses."))

    def is_expired(self):
        return timezone.now() > self.expire_at

    def is_exhausted(self):
        """Returns True if invite has reached its usage limit."""
        return self.max_uses is not None and self.used_count >= self.max_uses

    def is_usable(self):
        """Returns True if invite can be used to join."""
        return self.is_active and not self.is_expired() and not self.is_exhausted()

    def __str__(self):
        return f"Invite {self.id} for {self.board.name}"



class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    column = models.ForeignKey(
        Column,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, default="")
    priority = models.PositiveIntegerField(default=0)  # 0..3
    deadline = models.DateTimeField(null=True, blank=True)
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assigned_tasks",
        blank=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_tasks",
    )
    position = models.PositiveIntegerField()
    tags = models.JSONField(default=list, blank=True)
    checklist = models.JSONField(default=list, blank=True)
    added_to_board_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "created_at"]

    def clean(self):
        if self.priority > 3:
            raise ValidationError(_("Priority must be between 0 and 3."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.column.name})"


class TaskComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_comments")
    content = models.TextField()
    links = models.JSONField(default=list, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["task", "created_at"]),
            models.Index(fields=["owner", "created_at"]),
            models.Index(fields=["task", "is_deleted"]),
        ]

    def __str__(self):
        return f"Comment {self.id} by {self.owner} on {self.task}"


class TaskCommentReadState(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comment_read_states")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_read_states")
    last_read_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("task", "user")
        indexes = [
            models.Index(fields=["task", "user"]),
            models.Index(fields=["user", "last_read_at"]),
        ]

    def __str__(self):
        return f"ReadState {self.id} for {self.user} on {self.task}"


class TaskMentorRequestType(models.TextChoices):
    HELP = "help", _("Help")
    REVIEW = "review", _("Review")


class TaskMentorRequestStatus(models.TextChoices):
    OPEN = "open", _("Open")
    IN_PROGRESS = "in_progress", _("In Progress")
    RESOLVED = "resolved", _("Resolved")
    CANCELLED = "cancelled", _("Cancelled")


class TaskMentorRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="mentor_requests")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_mentor_requests")
    request_type = models.CharField(max_length=20, choices=TaskMentorRequestType.choices)
    status = models.CharField(max_length=20, choices=TaskMentorRequestStatus.choices, default=TaskMentorRequestStatus.OPEN)
    message = models.TextField()
    
    started_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="started_mentor_requests")
    started_comment = models.ForeignKey(TaskComment, on_delete=models.SET_NULL, null=True, blank=True, related_name="started_mentor_requests")
    started_at = models.DateTimeField(null=True, blank=True)
    
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="closed_mentor_requests")
    closed_at = models.DateTimeField(null=True, blank=True)
    close_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["task"],
                condition=models.Q(status__in=[TaskMentorRequestStatus.OPEN, TaskMentorRequestStatus.IN_PROGRESS]),
                name="unique_active_mentor_request_per_task",
            )
        ]

    def __str__(self):
        return f"Request {self.id} for {self.task}"


class ActivityLog(models.Model):
    ACTION_TYPES = [
        ("task_created",      "Task Created"),
        ("task_moved",        "Task Moved"),
        ("task_archived",     "Task Archived"),
        ("task_restored",     "Task Restored"),
        ("task_assigned",     "Task Assigned"),
        ("task_unassigned",   "Task Unassigned"),
        ("task_deadline_set", "Task Deadline Set"),
        ("column_created",    "Column Created"),
        ("column_moved",      "Column Moved"),
        ("column_archived",   "Column Archived"),
        ("column_cleared",    "Column Cleared"),
        ("member_joined",     "Member Joined"),
        ("member_left",       "Member Left"),
        ("mentor_request_created", "Mentor Request Created"),
        ("mentor_request_started", "Mentor Request Started"),
        ("mentor_request_resolved", "Mentor Request Resolved"),
        ("mentor_request_cancelled", "Mentor Request Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activity_logs",
    )
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["board", "created_at"]),
            models.Index(fields=["board", "action_type"]),
        ]

    def __str__(self):
        return f"{self.action_type} by {self.actor} in {self.board.name}"
