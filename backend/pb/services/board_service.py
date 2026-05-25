from django.db.models import Q
from django.db import transaction

from ..models import Board, BoardStatus, Column, ColumnKind, ColumnStatus, Project, Task, TaskStatus
from ..schemas import BoardIn, BoardUpdateIn


def list_boards(user, status=None):
    if user.is_staff or user.is_superuser:
        boards = Board.objects.all()
    else:
        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
    if status:
        boards = boards.filter(status=status)
    return boards


def create_board(user, payload: BoardIn, project: Project) -> Board:
    with transaction.atomic():
        board = Board.objects.create(
            name=payload.name,
            description=payload.description,
            project=project,
            owner=user,
            status=payload.status,
            tasks_total=payload.tasks_total,
            tasks_done=payload.tasks_done,
            progress_percent=payload.progress_percent,
        )
        board.members.add(user)

        for i, col_data in enumerate(payload.columns):
            Column.objects.create(
                board=board,
                name=col_data.name,
                position=col_data.position if col_data.position is not None else i + 1,
            )
    return board


def get_board(board_id) -> Board:
    return Board.objects.get(id=board_id)


def update_board(board: Board, payload: BoardUpdateIn) -> Board:
    if payload.name is not None:
        board.name = payload.name
    if payload.description is not None:
        board.description = payload.description
    if payload.status is not None:
        board.status = payload.status
    board.save()
    return board


def archive_board(board: Board) -> Board:
    board.status = BoardStatus.ARCHIVED
    board.save()
    return board


def recalculate_board_progress(board: Board) -> None:
    """Recalculate board tasks_total, tasks_done, progress_percent from active board-column tasks."""
    active_tasks = Task.objects.filter(
        column__board=board,
        column__kind=ColumnKind.BOARD,
        status=TaskStatus.ACTIVE,
    )
    total = active_tasks.count()
    done = active_tasks.filter(column__name__iexact="done").count()

    board.tasks_total = total
    board.tasks_done = done
    board.progress_percent = int((done / total) * 100) if total > 0 else 0
    board.save(update_fields=["tasks_total", "tasks_done", "progress_percent"])
