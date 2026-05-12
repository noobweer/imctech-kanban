import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
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
