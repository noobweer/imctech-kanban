import uuid
from django.db import transaction
from django.contrib.auth import get_user_model
from ..models import Task, Column, Board, ColumnKind
from ..permissions import has_board_access
from .board_service import recalculate_board_progress
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


def normalize_checklist_data(raw_checklist: list) -> list:
    """Normalize checklist to ensure id, title, is_done, position exist."""
    normalized = []
    if not isinstance(raw_checklist, list):
        return normalized

    for index, item in enumerate(raw_checklist):
        if not isinstance(item, dict):
            # If we happen to get schema objects here somehow, convert to dict
            if hasattr(item, "dict"):
                item = item.dict()
            else:
                continue
                
        normalized_item = {
            "id": str(item.get("id")) if item.get("id") else str(uuid.uuid4()),
            "title": str(item.get("title", "")),
            "is_done": bool(item.get("is_done", False)),
            "position": int(item.get("position")) if item.get("position") is not None else index + 1
        }
        normalized.append(normalized_item)
    return normalized


def normalize_checklist(task: Task) -> list:
    """Normalize task's checklist and return the list. Does NOT save the task."""
    normalized = normalize_checklist_data(task.checklist)
    task.checklist = normalized
    return normalized


def add_checklist_item(task: Task, title: str) -> Task:
    checklist = normalize_checklist(task)
    if not title.strip():
        raise ValueError("Checklist item title cannot be empty.")
    max_pos = max([item["position"] for item in checklist], default=0)
    new_item = {
        "id": str(uuid.uuid4()),
        "title": title.strip(),
        "is_done": False,
        "position": max_pos + 1
    }
    checklist.append(new_item)
    task.checklist = checklist
    task.save(update_fields=["checklist", "updated_at"])
    return task


def patch_checklist_item(task: Task, item_id: str, title: str = None, is_done: bool = None) -> Task:
    checklist = normalize_checklist(task)
    found = False
    for item in checklist:
        if item["id"] == item_id:
            found = True
            if title is not None:
                if not title.strip():
                    raise ValueError("Checklist item title cannot be empty.")
                item["title"] = title.strip()
            if is_done is not None:
                item["is_done"] = is_done
            break
    if not found:
        raise LookupError("CHECKLIST_ITEM_NOT_FOUND")
    task.checklist = checklist
    task.save(update_fields=["checklist", "updated_at"])
    return task


def toggle_checklist_item(task: Task, item_id: str) -> Task:
    checklist = normalize_checklist(task)
    found = False
    for item in checklist:
        if item["id"] == item_id:
            found = True
            item["is_done"] = not item.get("is_done", False)
            break
    if not found:
        raise LookupError("CHECKLIST_ITEM_NOT_FOUND")
    task.checklist = checklist
    task.save(update_fields=["checklist", "updated_at"])
    return task


def delete_checklist_item(task: Task, item_id: str) -> Task:
    checklist = normalize_checklist(task)
    new_checklist = [item for item in checklist if item["id"] != item_id]
    if len(new_checklist) == len(checklist):
        raise LookupError("CHECKLIST_ITEM_NOT_FOUND")
    
    # Re-normalize positions
    for idx, item in enumerate(new_checklist):
        item["position"] = idx + 1
        
    task.checklist = new_checklist
    task.save(update_fields=["checklist", "updated_at"])
    return task


def reorder_checklist(task: Task, ordered_item_ids: list) -> Task:
    checklist = normalize_checklist(task)
    current_ids = {item["id"] for item in checklist}
    if set(ordered_item_ids) != current_ids or len(ordered_item_ids) != len(current_ids):
        raise ValueError("CHECKLIST_REORDER_INVALID")
    
    id_to_item = {item["id"]: item for item in checklist}
    new_checklist = []
    for idx, item_id in enumerate(ordered_item_ids):
        item = id_to_item[item_id]
        item["position"] = idx + 1
        new_checklist.append(item)
        
    task.checklist = new_checklist
    task.save(update_fields=["checklist", "updated_at"])
    return task


def assign_task(task: Task, username: str) -> Task:
    board = task.column.board
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise LookupError("ASSIGNEE_NOT_FOUND")
        
    if not has_board_access(user, board):
        raise PermissionError("ASSIGNEE_NOT_BOARD_MEMBER")
        
    from ..permissions import is_mentor
    if is_mentor(user):
        raise PermissionError("MENTOR_CANNOT_BE_ASSIGNED")
        
    task.assignees.add(user)
    create_log(
        board=board,
        action_type="task_assigned",
        metadata={
            "task_id": str(task.id),
            "task_title": task.title,
            "username": user.username,
        }
    )
    return task


def unassign_task(task: Task, username: str) -> Task:
    try:
        user = task.assignees.get(username=username)
    except User.DoesNotExist:
        raise LookupError("ASSIGNEE_NOT_FOUND")
        
    task.assignees.remove(user)
    create_log(
        board=task.column.board,
        action_type="task_unassigned",
        metadata={
            "task_id": str(task.id),
            "task_title": task.title,
            "username": user.username,
        }
    )
    return task


def update_column_sum_tasks(column: Column):
    column.sum_tasks = column.tasks.count()
    column.save(update_fields=["sum_tasks"])


def move_task(task: Task, target_column_id: uuid.UUID, position: int) -> dict:
    board = task.column.board
    
    with transaction.atomic():
        source_col = task.column
        try:
            target_col = Column.objects.select_for_update().get(id=target_column_id, board=board)
        except Column.DoesNotExist:
            raise LookupError("TASK_MOVE_INVALID")
            
        if source_col.status == 'archived' or target_col.status == 'archived':
            raise ValueError("COLUMN_ARCHIVED")
            
        if target_col.kind == 'archive':
            raise ValueError("ARCHIVE_COLUMN_MOVE_DENIED")
            
        if position < 1:
            position = 1
            
        if source_col.id == target_col.id:
            if task.position == position:
                return {"task": task, "affected_column_ids": [str(source_col.id)], "reordered_tasks": {}}
                
            active_tasks = list(source_col.tasks.exclude(id=task.id).order_by('position'))
            
            if position > len(active_tasks) + 1:
                position = len(active_tasks) + 1
                
            active_tasks.insert(position - 1, task)
            
            reordered_tasks = {}
            for idx, t in enumerate(active_tasks):
                t.position = idx + 1
                reordered_tasks[str(t.id)] = t.position
                
            Task.objects.bulk_update(active_tasks, ["position"])
            task.position = position
            
            return {"task": task, "affected_column_ids": [str(source_col.id)], "reordered_tasks": reordered_tasks}
            
        else:
            source_tasks = list(source_col.tasks.exclude(id=task.id).order_by('position'))
            target_tasks = list(target_col.tasks.order_by('position'))
            
            reordered_tasks = {}
            for idx, t in enumerate(source_tasks):
                t.position = idx + 1
                reordered_tasks[str(t.id)] = t.position
            if source_tasks:
                Task.objects.bulk_update(source_tasks, ["position"])
                
            if position > len(target_tasks) + 1:
                position = len(target_tasks) + 1
                
            task.column = target_col
            target_tasks.insert(position - 1, task)
            
            for idx, t in enumerate(target_tasks):
                t.position = idx + 1
                reordered_tasks[str(t.id)] = t.position
                
            _set_board_timestamp(task, target_col)
            task.save(update_fields=["column", "position", "updated_at", "added_to_board_at"])
            target_tasks_without_self = [t for t in target_tasks if t.id != task.id]
            if target_tasks_without_self:
                Task.objects.bulk_update(target_tasks_without_self, ["position"])
            
            update_column_sum_tasks(source_col)
            update_column_sum_tasks(target_col)
            
            recalculate_board_progress(board)
            
            create_log(
                board=board,
                action_type="task_moved",
                metadata={
                    "task_id": str(task.id),
                    "task_title": task.title,
                    "from_column": source_col.name,
                    "to_column": target_col.name
                }
            )
            
            return {
                "task": task,
                "affected_column_ids": [str(source_col.id), str(target_col.id)],
                "reordered_tasks": reordered_tasks
            }
