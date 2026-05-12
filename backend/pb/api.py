from typing import List, Optional
import uuid

from django.shortcuts import get_object_or_404
from django.db.models import Q
from ninja import Router, Query
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth

from .models import Project, Board, BoardStatus
from .schemas import ProjectIn, ProjectOut, BoardIn, BoardOut, BoardUpdateIn
from .permissions import (
    has_project_access,
    can_edit_project,
    has_board_access,
    can_edit_board,
)

router = Router(tags=["Projects & Boards"])


# --- Project Endpoints ---


@router.get("/projects", response=List[ProjectOut], auth=JWTAuth())
@paginate
def list_projects(request):
    user = request.auth
    if user.is_staff or user.is_superuser:
        return Project.objects.all()
    return Project.objects.filter(Q(boards__owner=user) | Q(boards__members=user)).distinct()


@router.post("/projects", response={201: ProjectOut}, auth=JWTAuth())
def create_project(request, payload: ProjectIn):
    project = Project.objects.create(name=payload.name)
    return 201, project


@router.get("/projects/{project_id}", response=ProjectOut, auth=JWTAuth())
def retrieve_project(request, project_id: uuid.UUID):
    user = request.auth
    project = get_object_or_404(Project, id=project_id)
    if not has_project_access(user, project):
        return router.api.create_response(request, {"detail": "No access to this project"}, status=403)
    return project


@router.patch("/projects/{project_id}", response=ProjectOut, auth=JWTAuth())
def update_project(request, project_id: uuid.UUID, payload: ProjectIn):
    user = request.auth
    project = get_object_or_404(Project, id=project_id)
    if not can_edit_project(user, project):
        return router.api.create_response(request, {"detail": "No permission to edit this project"}, status=403)

    project.name = payload.name
    project.save()
    return project


@router.delete("/projects/{project_id}", auth=JWTAuth())
def delete_project(request, project_id: uuid.UUID):
    user = request.auth
    project = get_object_or_404(Project, id=project_id)
    if not can_edit_project(user, project):
        return router.api.create_response(request, {"detail": "No permission to delete this project"}, status=403)

    if project.boards.exists():
        return router.api.create_response(
            request,
            {"detail": "Cannot delete project with associated boards. Delete boards first."},
            status=400,
        )
    project.delete()
    return {"success": True}


# --- Board Endpoints ---


@router.get("/boards", response=List[BoardOut], auth=JWTAuth())
@paginate
def list_boards(request, status: Optional[BoardStatus] = Query(None)):
    user = request.auth
    if user.is_staff or user.is_superuser:
        boards = Board.objects.all()
    else:
        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    if status:
        boards = boards.filter(status=status)
    return boards


@router.post("/boards", response={201: BoardOut}, auth=JWTAuth())
def create_board(request, payload: BoardIn):
    user = request.auth
    project = None
    if payload.project_id:
        project = get_object_or_404(Project, id=payload.project_id)
        if not has_project_access(user, project):
            return router.api.create_response(request, {"detail": "No access to this project"}, status=403)
    else:
        # Create a new project if project_id is not provided
        # Use same name as board for simplicity as requested (no projects in UI)
        project = Project.objects.create(name=payload.name)

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
    board.save()
    return 201, board


@router.get("/boards/{board_id}", response=BoardOut, auth=JWTAuth())
def retrieve_board(request, board_id: uuid.UUID):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(user, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)
    return board


@router.patch("/boards/{board_id}", response=BoardOut, auth=JWTAuth())
def update_board(request, board_id: uuid.UUID, payload: BoardUpdateIn):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to edit this board"}, status=403)

    if payload.name is not None:
        board.name = payload.name
    if payload.description is not None:
        board.description = payload.description
    if payload.status is not None:
        board.status = payload.status
    board.save()
    return board


@router.delete("/boards/{board_id}", auth=JWTAuth())
def delete_board(request, board_id: uuid.UUID):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to delete this board"}, status=403)

    # Safe deletion strategy: archive the board
    board.status = BoardStatus.ARCHIVED
    board.save()
    return {"success": True, "message": "Board archived successfully"}
