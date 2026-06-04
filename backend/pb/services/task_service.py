from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Q

from ..models import Board, Column, ColumnKind, ColumnStatus, Task
from ..schemas import TaskIn, TaskPatchIn
from ..permissions import has_board_access
from .board_service import recalculate_board_progress
from .task_lifecycle import normalize_checklist_data, update_column_sum_tasks
from .activity_service import create_log
from django.utils import timezone

User = get_user_model()

def _set_board_timestamp(task, column, force_update=False):
    """
    Устанавливает дату попадания на доску.
    force_update=True используется для восстановления из архива.
    """
    if column.kind == ColumnKind.BOARD:
        if force_update or task.added_to_board_at is None:
            task.added_to_board_at = timezone.now()




def _resolve_assignees(usernames: list, board: Board) -> list:
    if not usernames:
        return []
    assignees = list(User.objects.filter(username__in=usernames))
    if len(assignees) != len(usernames):
        raise LookupError("One or more assignees not found.")
    for a in assignees:
        if not has_board_access(a, board):
            raise PermissionError(f"Assignee {a.username} has no access to board.")
    return assignees


def list_tasks(board: Board, column_id=None, column_kind=None,
               priority=None, assignee=None, tag=None, search=None,
               sort_by=None, deadline_filter=None):
    tasks = Task.objects.filter(column__board=board)
    if column_kind != ColumnKind.ARCHIVE:
        tasks = tasks.exclude(column__kind=ColumnKind.ARCHIVE)
    if column_id:
        tasks = tasks.filter(column_id=column_id)
    if column_kind:
        tasks = tasks.filter(column__kind=column_kind)
    if priority is not None:
        tasks = tasks.filter(priority=priority)
    if assignee:
        tasks = tasks.filter(assignees__username=assignee)
    if tag:
        tasks = tasks.filter(tags__contains=[tag])
    if search:
        tasks = tasks.filter(Q(title__icontains=search) | Q(content__icontains=search))
        
    if deadline_filter == "due_soon_or_overdue":
        now = timezone.now()
        due_soon_threshold = now + timezone.timedelta(days=3)
        tasks = tasks.filter(deadline__isnull=False, deadline__lte=due_soon_threshold)
        
    tasks = tasks.distinct()
    
    if sort_by == "-added_to_board_at":
        tasks = tasks.order_by(models.F('added_to_board_at').desc(nulls_last=True))
    elif sort_by == "added_to_board_at":
        tasks = tasks.order_by(models.F('added_to_board_at').asc(nulls_last=True))
        
    return tasks


def list_backlog_tasks(board: Board, priority=None,
                       assignee=None, tag=None, search=None):
    tasks = Task.objects.filter(column__board=board, column__kind=ColumnKind.BACKLOG)
    if priority is not None:
        tasks = tasks.filter(priority=priority)
    if assignee:
        tasks = tasks.filter(assignees__username=assignee)
    if tag:
        tasks = tasks.filter(tags__contains=[tag])
    if search:
        tasks = tasks.filter(Q(title__icontains=search) | Q(content__icontains=search))
    return tasks.distinct()


def list_column_tasks(column: Column):
    tasks = column.tasks.all()
    return tasks


def get_task(task_id) -> Task:
    return Task.objects.get(id=task_id)


def create_task(board: Board, user, payload: TaskIn) -> Task:
    with transaction.atomic():
        if payload.column_id:
            column = Column.objects.get(id=payload.column_id, board=board)
        else:
            column = Column.objects.filter(
                board=board, kind=ColumnKind.BACKLOG, status=ColumnStatus.ACTIVE
            ).first()
            if not column:
                column = Column.objects.create(
                    board=board,
                    name="Backlog",
                    kind=ColumnKind.BACKLOG,
                    status=ColumnStatus.ACTIVE,
                    position=1,
                )

        max_pos = column.tasks.aggregate(models.Max("position"))["position__max"] or 0
        assignees = _resolve_assignees(payload.assignees or [], board)
        
        # Clean out empty titles before normalization
        raw_checklist = []
        for item in (payload.checklist or []):
            item_dict = item.dict() if hasattr(item, "dict") else item
            if isinstance(item_dict, dict) and "title" in item_dict and isinstance(item_dict["title"], str) and item_dict["title"].strip():
                raw_checklist.append({"title": item_dict["title"].strip(), "is_done": item_dict.get("is_done", False)})

        clean_checklist = normalize_checklist_data(raw_checklist)

        task = Task.objects.create(
            column=column,
            title=payload.title,
            content=payload.content or "",
            priority=payload.priority or 0,
            deadline=payload.deadline,
            owner=user,
            position=max_pos + 1,
            tags=[t for t in payload.tags if t] if payload.tags else [],
            checklist=clean_checklist,
        )
        if assignees:
            task.assignees.set(assignees)

        _set_board_timestamp(task, column)
        task.save(update_fields=["added_to_board_at"])

        update_column_sum_tasks(column)
        recalculate_board_progress(board)
        
        create_log(
            board=board,
            action_type="task_created",
            metadata={
                "task_id": str(task.id),
                "task_title": task.title,
                "column_name": column.name,
            }
        )
    return task


def update_task(task: Task, payload: TaskPatchIn) -> Task:
    with transaction.atomic():
        deadline_changed = False
        if payload.title is not None:
            task.title = payload.title
        if payload.content is not None:
            task.content = payload.content
        if payload.priority is not None:
            task.priority = payload.priority
        if payload.deadline is not None:
            if task.deadline != payload.deadline:
                deadline_changed = True
            task.deadline = payload.deadline
        if payload.tags is not None:
            task.tags = [t for t in payload.tags if t]

        task.save()
        
        if deadline_changed:
            create_log(
                board=task.column.board,
                action_type="task_deadline_set",
                metadata={
                    "task_id": str(task.id),
                    "task_title": task.title,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                }
            )
    return task


