from django.db import transaction, models
from ..models import Board, Column, ColumnKind, ColumnStatus, Task
from .board_service import recalculate_board_progress
from .task_lifecycle import update_column_sum_tasks

def get_or_create_archive_column(board: Board) -> Column:
    column = Column.objects.filter(
        board=board, kind=ColumnKind.ARCHIVE, status=ColumnStatus.ACTIVE
    ).first()
    if column:
        return column
    
    with transaction.atomic():
        column, created = Column.objects.get_or_create(
            board=board,
            kind=ColumnKind.ARCHIVE,
            status=ColumnStatus.ACTIVE,
            defaults={
                "name": "Archive",
                "position": 1,
            }
        )
        return column

def archive_task(task: Task) -> Task:
    if task.column.kind == ColumnKind.ARCHIVE:
        return task

    board = task.column.board
    archive_col = get_or_create_archive_column(board)
    source_col = task.column

    with transaction.atomic():
        # Move to archive
        task.column = archive_col
        max_pos = archive_col.tasks.aggregate(models.Max("position"))["position__max"] or 0
        task.position = max_pos + 1
        task.save(update_fields=["column", "position"])

        # Recalculate positions in source column
        source_tasks = source_col.tasks.order_by("position")
        for idx, t in enumerate(source_tasks, start=1):
            if t.position != idx:
                t.position = idx
                t.save(update_fields=["position"])

        update_column_sum_tasks(source_col)
        update_column_sum_tasks(archive_col)
        recalculate_board_progress(board)
    
    return task

def restore_task(task: Task, target_column_id, position=None) -> Task:
    if task.column.kind != ColumnKind.ARCHIVE:
        raise ValueError("Task is not in archive")

    target_column = Column.objects.get(id=target_column_id)
    if target_column.board != task.column.board:
        raise ValueError("Target column belongs to a different board")
    if target_column.status != ColumnStatus.ACTIVE:
        raise ValueError("Target column is archived")
    if target_column.kind not in [ColumnKind.BOARD, ColumnKind.BACKLOG]:
        raise ValueError("Target column must be board or backlog")

    archive_col = task.column
    board = target_column.board

    with transaction.atomic():
        task.column = target_column
        target_tasks = list(target_column.tasks.exclude(id=task.id).order_by("position"))
        
        if position is None:
            max_pos = target_column.tasks.aggregate(models.Max("position"))["position__max"] or 0
            task.position = max_pos + 1
            task.save(update_fields=["column", "position"])
        else:
            task.position = position
            task.save(update_fields=["column", "position"])
            target_tasks.insert(position - 1, task)
            for idx, t in enumerate(target_tasks, start=1):
                if t.position != idx:
                    t.position = idx
                    t.save(update_fields=["position"])

        # Recalculate positions in archive column
        archive_tasks = archive_col.tasks.exclude(id=task.id).order_by("position")
        for idx, t in enumerate(archive_tasks, start=1):
            if t.position != idx:
                t.position = idx
                t.save(update_fields=["position"])

        update_column_sum_tasks(archive_col)
        update_column_sum_tasks(target_column)
        recalculate_board_progress(board)
    
    return task

def archive_column(column: Column) -> Column:
    if column.kind in [ColumnKind.BACKLOG, ColumnKind.ARCHIVE]:
        raise ValueError("Cannot archive backlog or archive columns")
    if column.status == ColumnStatus.ARCHIVED:
        return column

    board = column.board
    with transaction.atomic():
        column.status = ColumnStatus.ARCHIVED
        column.save(update_fields=["status"])

        # Recalculate positions of active columns of the same kind
        active_cols = Column.objects.filter(
            board=board, kind=column.kind, status=ColumnStatus.ACTIVE
        ).order_by("position")
        for idx, c in enumerate(active_cols, start=1):
            if c.position != idx:
                c.position = idx
                c.save(update_fields=["position"])

        recalculate_board_progress(board)

    return column

def restore_column(column: Column) -> Column:
    if column.status == ColumnStatus.ACTIVE:
        return column

    board = column.board
    with transaction.atomic():
        column.status = ColumnStatus.ACTIVE
        
        max_pos = Column.objects.filter(
            board=board, kind=column.kind, status=ColumnStatus.ACTIVE
        ).aggregate(models.Max("position"))["position__max"] or 0
        column.position = max_pos + 1
        column.save(update_fields=["status", "position"])

        recalculate_board_progress(board)

    return column

def clear_column(column: Column) -> dict:
    if column.status != ColumnStatus.ACTIVE:
        raise ValueError("Column is not active")
    if column.kind not in [ColumnKind.BOARD, ColumnKind.BACKLOG]:
        raise ValueError("Cannot clear archive column")

    board = column.board
    archive_col = get_or_create_archive_column(board)

    with transaction.atomic():
        tasks_to_move = list(column.tasks.order_by("position"))
        count = len(tasks_to_move)
        if count == 0:
            return {
                "success": True,
                "archived_tasks_count": 0,
                "affected_column_ids": [str(column.id), str(archive_col.id)]
            }

        max_pos = archive_col.tasks.aggregate(models.Max("position"))["position__max"] or 0
        
        for idx, t in enumerate(tasks_to_move, start=1):
            t.column = archive_col
            t.position = max_pos + idx
            t.save(update_fields=["column", "position"])

        update_column_sum_tasks(column)
        update_column_sum_tasks(archive_col)
        recalculate_board_progress(board)

    return {
        "success": True,
        "archived_tasks_count": count,
        "affected_column_ids": [str(column.id), str(archive_col.id)]
    }
