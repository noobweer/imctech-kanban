from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from ..models import Board, Task, ActivityLog, ColumnKind, ColumnStatus

def get_progress(board: Board) -> dict:
    columns = board.columns.filter(
        kind=ColumnKind.BOARD,
        status=ColumnStatus.ACTIVE
    ).order_by("position")

    total_tasks = 0
    column_data = []

    for col in columns:
        active_count = col.tasks.count()
        total_tasks += active_count
        column_data.append({
            "id": col.id,
            "name": col.name,
            "task_count": active_count,
            "percent": 0
        })

    if total_tasks > 0:
        for col in column_data:
            col["percent"] = int(round((col["task_count"] / total_tasks) * 100, 0))

    return {
        "total_tasks": total_tasks,
        "columns": column_data
    }

def get_activity(board: Board, period: str = "weekly") -> dict:
    end_date = timezone.now()
    if period == "weekly":
        # Get start of the week (assuming week starts on Monday)
        days_since_monday = end_date.weekday()
        start_date = (end_date - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        # All time
        start_date = board.created_at

    logs = list(ActivityLog.objects.filter(
        board=board,
        created_at__gte=start_date,
        created_at__lte=end_date
    ).select_related('actor'))

    # Build matrix
    active_columns = list(board.columns.filter(
        kind=ColumnKind.BOARD,
        status=ColumnStatus.ACTIVE
    ).order_by("position"))
    
    col_names = [c.name for c in active_columns]

    members_data = {}
    for member in board.members.all():
        members_data[member.username] = {
            "username": member.username,
            "name": getattr(member, 'profile', None) and getattr(member.profile, 'name', None) or member.username,
            "tasks": {}
        }

    # "Done" logic: find final moved to Done
    done_tasks = {} # task_id -> {actor, is_done}
    for log in logs:
        if log.action_type == "task_moved":
            task_id = log.metadata.get("task_id")
            to_col = log.metadata.get("to_column")
            from_col = log.metadata.get("from_column")
            actor = log.actor.username if log.actor else None
            
            if to_col == "Done":
                done_tasks[task_id] = {"actor": actor, "is_done": True}
            elif from_col == "Done" and to_col != "Done":
                if task_id in done_tasks:
                    done_tasks[task_id]["is_done"] = False

    # Current task distribution for users
    for col in active_columns:
        if col.name == "Done":
            continue
        
        for task in col.tasks.all():
            for assignee in task.assignees.all():
                if assignee.username in members_data:
                    members_data[assignee.username]["tasks"][col.name] = members_data[assignee.username]["tasks"].get(col.name, 0) + 1

    # Add done tasks to the actor who moved them, or assignees if you prefer? 
    # Usually "activity" means who did the action. Let's assign Done to the actor.
    for task_id, data in done_tasks.items():
        if data["is_done"] and data["actor"] in members_data:
            members_data[data["actor"]]["tasks"]["Done"] = members_data[data["actor"]]["tasks"].get("Done", 0) + 1

    # Format output
    result_members = []
    for username, data in members_data.items():
        total = sum(data["tasks"].values())
        user_cols = []
        for col_name in col_names:
            c_count = data["tasks"].get(col_name, 0)
            c_perc = int(round((c_count / total) * 100, 0)) if total > 0 else 0
            # Need to find column_id
            c_id = next((c.id for c in active_columns if c.name == col_name), None)
            user_cols.append({
                "column_id": c_id,
                "column_name": col_name,
                "task_count": c_count,
                "percent": c_perc
            })
        
        result_members.append({
            "username": username,
            "name": data["name"],
            "columns": user_cols
        })

    return {
        "period": period,
        "week_start": start_date.strftime("%Y-%m-%d"),
        "week_end": end_date.strftime("%Y-%m-%d"),
        "members": result_members
    }


def get_deadlines(board: Board) -> dict:
    now = timezone.now()
    due_soon_threshold = now + timedelta(days=4)

    tasks = Task.objects.filter(
        column__board=board,
        column__kind=ColumnKind.BOARD,
        deadline__isnull=False
    ).select_related("column").prefetch_related("assignees")

    overdue = []
    due_soon = []

    for task in tasks:
        if task.deadline <= now:
            overdue.append(task)
        elif task.deadline <= due_soon_threshold:
            due_soon.append(task)

    overdue.sort(key=lambda t: t.deadline)
    due_soon.sort(key=lambda t: t.deadline)

    def _format(t):
        return {
            "id": t.id,
            "title": t.title,
            "deadline": t.deadline,
            "column": t.column.name,
            "assignees": [a.username for a in t.assignees.all()],
            "priority": t.priority,
            "added_to_board_at": t.added_to_board_at,
        }

    return {
        "overdue": [_format(t) for t in overdue],
        "due_soon": [_format(t) for t in due_soon]
    }
