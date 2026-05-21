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


class Column(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="columns",
    )
    name = models.CharField(max_length=255)
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
