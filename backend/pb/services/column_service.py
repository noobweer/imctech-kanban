from django.db import models, transaction

from ..models import Board, Column, ColumnStatus
from ..schemas import ColumnIn, ColumnUpdateIn


def list_columns(board: Board, status=None, kind: str = "board"):
    columns = board.columns.all()
    if status:
        columns = columns.filter(status=status)
    if kind and kind != "all":
        columns = columns.filter(kind=kind)
    return columns


def create_column(board: Board, payload: ColumnIn) -> Column:
    with transaction.atomic():
        if payload.position is None:
            max_pos = board.columns.aggregate(models.Max("position"))["position__max"] or 0
            position = max_pos + 1
        else:
            position = payload.position
            board.columns.filter(position__gte=position).update(position=models.F("position") + 1)

        column = Column.objects.create(
            board=board,
            name=payload.name,
            position=position,
        )
    return column


def create_default_columns(board: Board) -> list:
    if board.columns.exists():
        raise ValueError("Board already has columns. Cannot create defaults.")

    defaults = [
        {"name": "To Do", "position": 1},
        {"name": "In Progress", "position": 2},
        {"name": "Done", "position": 3},
    ]
    with transaction.atomic():
        columns = [Column.objects.create(board=board, **d) for d in defaults]
    return columns


def get_column(column_id) -> Column:
    return Column.objects.get(id=column_id)


def update_column(column: Column, payload: ColumnUpdateIn) -> Column:
    if payload.name is not None:
        column.name = payload.name
    if payload.status is not None:
        column.status = payload.status
    column.save()
    return column


def move_column(column: Column, new_position: int) -> Column:
    old_position = column.position
    if old_position == new_position:
        return column

    with transaction.atomic():
        if new_position > old_position:
            column.board.columns.filter(
                position__gt=old_position, position__lte=new_position
            ).update(position=models.F("position") - 1)
        else:
            column.board.columns.filter(
                position__gte=new_position, position__lt=old_position
            ).update(position=models.F("position") + 1)

        column.position = new_position
        column.save()
    return column


def archive_column(column: Column) -> Column:
    column.status = ColumnStatus.ARCHIVED
    column.save()
    return column
