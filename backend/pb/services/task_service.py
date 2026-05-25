from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Q

from ..models import Board, Column, ColumnKind, ColumnStatus, Task, TaskStatus
from ..schemas import TaskIn, TaskUpdateIn
from ..permissions import has_board_access
from .board_service import recalculate_board_progress

User = get_user_model()


def _clean_checklist(raw_checklist) -> list:
    clean = []
    for item in raw_checklist:
        item_dict = item.dict() if hasattr(item, "dict") else item
        if (
            isinstance(item_dict, dict)
            and "title" in item_dict
            and isinstance(item_dict["title"], str)
            and item_dict["title"].strip()
        ):
            clean.append({"title": item_dict["title"], "is_done": item_dict.get("is_done", False)})
    return clean


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


def list_tasks(board: Board, status=None, column_id=None, column_kind=None,
               priority=None, assignee=None, tag=None, search=None):
    tasks = Task.objects.filter(column__board=board)
    if status:
        tasks = tasks.filter(status=status)
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
    return tasks.distinct()


def list_backlog_tasks(board: Board, status=None, priority=None,
                       assignee=None, tag=None, search=None):
    tasks = Task.objects.filter(column__board=board, column__kind=ColumnKind.BACKLOG)
    if status:
        tasks = tasks.filter(status=status)
    if priority is not None:
        tasks = tasks.filter(priority=priority)
    if assignee:
        tasks = tasks.filter(assignees__username=assignee)
    if tag:
        tasks = tasks.filter(tags__contains=[tag])
    if search:
        tasks = tasks.filter(Q(title__icontains=search) | Q(content__icontains=search))
    return tasks.distinct()


def list_column_tasks(column: Column, status=None):
    tasks = column.tasks.all()
    if status:
        tasks = tasks.filter(status=status)
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
        clean_checklist = _clean_checklist(payload.checklist or [])

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

        recalculate_board_progress(board)
    return task


def update_task(task: Task, payload: TaskUpdateIn) -> Task:
    board = task.column.board
    with transaction.atomic():
        if payload.title is not None:
            task.title = payload.title
        if payload.content is not None:
            task.content = payload.content
        if payload.priority is not None:
            task.priority = payload.priority
        if payload.deadline is not None:
            task.deadline = payload.deadline
        if payload.status is not None:
            task.status = payload.status

        if payload.column_id is not None and payload.column_id != task.column.id:
            new_col = Column.objects.get(id=payload.column_id, board=board)
            task.column = new_col
            max_pos = new_col.tasks.aggregate(models.Max("position"))["position__max"] or 0
            task.position = max_pos + 1

        if payload.tags is not None:
            task.tags = [t for t in payload.tags if t]

        if payload.checklist is not None:
            task.checklist = _clean_checklist(payload.checklist)

        if payload.assignees is not None:
            assignees = _resolve_assignees(payload.assignees, board)
            task.assignees.set(assignees)

        task.save()
        recalculate_board_progress(board)
    return task


def archive_task(task: Task) -> Task:
    task.status = TaskStatus.ARCHIVED
    task.save()
    recalculate_board_progress(task.column.board)
    return task


def restore_task(task: Task) -> Task:
    task.status = TaskStatus.ACTIVE
    task.save()
    recalculate_board_progress(task.column.board)
    return task


def delete_task(task: Task) -> Task:
    task.status = TaskStatus.ARCHIVED
    task.save()
    recalculate_board_progress(task.column.board)
    return task
