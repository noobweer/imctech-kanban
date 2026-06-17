import uuid
from typing import List, Optional
from django.http import JsonResponse

from django.shortcuts import get_object_or_404
from ninja import Router, Query
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth

from ..models import Board, BoardStatus, Project, ColumnStatus, ColumnKind
from ..schemas import BoardIn, BoardOut, BoardUpdateIn, TaskOut, ColumnOut
from ..permissions import has_project_access, has_board_access, can_edit_board, is_student
from ..services import board_service, project_service, task_service, column_service

router = Router()


@router.get("/boards", response=List[BoardOut], auth=JWTAuth())
@paginate
def list_boards(request, status: Optional[BoardStatus] = Query(None)):
    return board_service.list_boards(request.auth, status=status)


@router.post("/boards", response={201: BoardOut}, auth=JWTAuth())
def create_board(request, payload: BoardIn):
    user = request.auth
    if is_student(user):
        return JsonResponse({"detail": "Student is not allowed to create projects or boards", "code": "STUDENT_ACTION_FORBIDDEN"}, status=403)
    if payload.project_id:
        project = get_object_or_404(Project, id=payload.project_id)
        if not has_project_access(user, project):
            return JsonResponse({"detail": "No access to this project"}, status=403)
    else:
        project = project_service.create_project(payload.name)
    board = board_service.create_board(user, payload, project)
    return 201, board


@router.get("/boards/{board_id}", response=BoardOut, auth=JWTAuth())
def retrieve_board(request, board_id: uuid.UUID):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        return JsonResponse({"detail": "No access to this board"}, status=403)
    return board


@router.patch("/boards/{board_id}", response=BoardOut, auth=JWTAuth())
def update_board(request, board_id: uuid.UUID, payload: BoardUpdateIn):
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(request.auth, board):
        return JsonResponse({"detail": "No permission to edit this board"}, status=403)
    return board_service.update_board(board, payload)


@router.delete("/boards/{board_id}", auth=JWTAuth())
def delete_board(request, board_id: uuid.UUID):
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(request.auth, board):
        return JsonResponse({"detail": "No permission to delete this board"}, status=403)
    board_service.archive_board(board)
    return {"success": True, "message": "Board archived successfully"}


@router.get("/boards/{board_id}/archive/tasks", response=List[TaskOut], auth=JWTAuth())
@paginate
def list_archive_tasks(
    request,
    board_id: uuid.UUID,
    priority: Optional[int] = Query(None),
    assignee: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        return JsonResponse({"detail": "No access to this board"}, status=403)
    return task_service.list_tasks(
        board, column_kind=ColumnKind.ARCHIVE,
        priority=priority, assignee=assignee, tag=tag, search=search,
    )


@router.get("/boards/{board_id}/archive/columns", response=List[ColumnOut], auth=JWTAuth())
@paginate
def list_archive_columns(
    request,
    board_id: uuid.UUID,
    kind: str = Query("board"),
):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        return JsonResponse({"detail": "No access to this board"}, status=403)
    return column_service.list_columns(board, status=ColumnStatus.ARCHIVED, kind=kind)


# --- Mentor Requests ---

from ..schemas import MentorRequestOut
from ..services.mentor_request_service import get_mentor_requests_for_board

@router.get("/boards/{board_id}/mentor-requests", response=List[MentorRequestOut], auth=JWTAuth())
@paginate
def list_board_mentor_requests(
    request,
    board_id: uuid.UUID,
    status: Optional[str] = Query(None),
    request_type: Optional[str] = Query(None),
    mine: Optional[bool] = Query(None)
):
    board = get_object_or_404(Board, id=board_id)
    try:
        return get_mentor_requests_for_board(
            user=request.auth,
            board=board,
            status_filter=status,
            request_type_filter=request_type,
            mine_filter=mine
        )
    except PermissionError as e:
        from ninja.errors import HttpError
        raise HttpError(403, str(e))
