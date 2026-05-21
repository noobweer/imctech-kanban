from typing import List, Optional, Union
import uuid

from django.shortcuts import get_object_or_404
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from ninja import Router, Query
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth

from .models import Project, Board, BoardStatus, Column, ColumnStatus, ColumnKind, Invite, Task, TaskStatus
from .schemas import (
    ProjectIn,
    ProjectOut,
    BoardIn,
    BoardOut,
    BoardUpdateIn,
    ColumnIn,
    ColumnOut,
    ColumnUpdateIn,
    ColumnMoveIn,
    InviteIn,
    InvitePatchIn,
    InviteOut,
    InvitePublicOut,
    MemberOut,
    TaskIn,
    TaskUpdateIn,
    TaskOut,
)
from .permissions import (
    has_project_access,
    can_edit_project,
    has_board_access,
    can_edit_board,
    can_edit_column,
)

router = Router(tags=["Projects & Boards"])


def recalculate_board_progress(board: Board):
    """Recalculate board tasks_total, tasks_done, progress_percent based on active tasks in board columns."""
    active_tasks = Task.objects.filter(
        column__board=board,
        column__kind=ColumnKind.BOARD,
        status=TaskStatus.ACTIVE
    )
    total = active_tasks.count()
    done = active_tasks.filter(column__name__iexact="done").count()
    
    board.tasks_total = total
    board.tasks_done = done
    board.progress_percent = int((done / total) * 100) if total > 0 else 0
    board.save(update_fields=["tasks_total", "tasks_done", "progress_percent"])


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

        # Create columns if provided
        for i, col_data in enumerate(payload.columns):
            Column.objects.create(
                board=board,
                name=col_data.name,
                position=col_data.position if col_data.position is not None else i + 1,
            )

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


# --- Column Endpoints ---


@router.get("/boards/{board_id}/columns", response=List[ColumnOut], auth=JWTAuth())
@paginate
def list_columns(request, board_id: uuid.UUID, status: Optional[ColumnStatus] = Query(None), kind: str = Query("board")):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(user, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)

    columns = board.columns.all()
    if status:
        columns = columns.filter(status=status)
    if kind and kind != "all":
        columns = columns.filter(kind=kind)
    return columns


@router.post("/boards/{board_id}/columns", response={201: ColumnOut}, auth=JWTAuth())
def create_column(request, board_id: uuid.UUID, payload: ColumnIn):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to edit this board"}, status=403)

    with transaction.atomic():
        if payload.position is None:
            max_pos = board.columns.aggregate(models.Max("position"))["position__max"] or 0
            position = max_pos + 1
        else:
            position = payload.position
            # Shift existing columns
            board.columns.filter(position__gte=position).update(position=models.F("position") + 1)

        column = Column.objects.create(
            board=board,
            name=payload.name,
            position=position,
        )
    return 201, column


@router.post("/boards/{board_id}/columns/defaults", response={201: List[ColumnOut]}, auth=JWTAuth())
def create_default_columns(request, board_id: uuid.UUID):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to edit this board"}, status=403)

    if board.columns.exists():
        return router.api.create_response(
            request,
            {"detail": "Board already has columns. Cannot create defaults."},
            status=400,
        )

    defaults = [
        {"name": "To Do", "position": 1},
        {"name": "In Progress", "position": 2},
        {"name": "Done", "position": 3},
    ]

    with transaction.atomic():
        columns = [Column.objects.create(board=board, **default) for default in defaults]

    return 201, columns


@router.get("/columns/{column_id}", response=ColumnOut, auth=JWTAuth())
def retrieve_column(request, column_id: uuid.UUID):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not has_board_access(user, column.board):
        return router.api.create_response(request, {"detail": "No access to this column"}, status=403)
    return column


@router.patch("/columns/{column_id}", response=ColumnOut, auth=JWTAuth())
def update_column(request, column_id: uuid.UUID, payload: ColumnUpdateIn):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(user, column):
        return router.api.create_response(request, {"detail": "No permission to edit this column"}, status=403)

    if payload.name is not None:
        column.name = payload.name
    if payload.status is not None:
        column.status = payload.status
    column.save()
    return column


@router.post("/columns/{column_id}/move", response=ColumnOut, auth=JWTAuth())
def move_column(request, column_id: uuid.UUID, payload: ColumnMoveIn):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(user, column):
        return router.api.create_response(request, {"detail": "No permission to move this column"}, status=403)

    old_position = column.position
    new_position = payload.position

    if old_position == new_position:
        return column

    with transaction.atomic():
        if new_position > old_position:
            # Moving down: shift items between old and new up
            column.board.columns.filter(position__gt=old_position, position__lte=new_position).update(
                position=models.F("position") - 1
            )
        else:
            # Moving up: shift items between new and old down
            column.board.columns.filter(position__gte=new_position, position__lt=old_position).update(
                position=models.F("position") + 1
            )

        column.position = new_position
        column.save()

    return column


@router.post("/columns/{column_id}/archive", response=ColumnOut, auth=JWTAuth())
def archive_column(request, column_id: uuid.UUID):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(user, column):
        return router.api.create_response(request, {"detail": "No permission to archive this column"}, status=403)

    column.status = ColumnStatus.ARCHIVED
    column.save()
    return column


@router.delete("/columns/{column_id}", auth=JWTAuth())
def delete_column(request, column_id: uuid.UUID):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(user, column):
        return router.api.create_response(request, {"detail": "No permission to delete this column"}, status=403)

    # Soft delete strategy: archive the column
    column.status = ColumnStatus.ARCHIVED
    column.save()
    return {"success": True, "message": "Column archived successfully"}


# ---------------------------------------------------------------------------
# --- Invite Endpoints ---
# ---------------------------------------------------------------------------


@router.get("/boards/{board_id}/invites", response=List[InviteOut], auth=JWTAuth(), tags=["Invites"])
def list_board_invites(request, board_id: uuid.UUID):
    """List all invite history for a board. Owner/staff only."""
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to view invites"}, status=403)
    return list(board.invites.select_related("board", "created_by").all())


@router.get("/boards/{board_id}/invites/current", response=InviteOut, auth=JWTAuth(), tags=["Invites"])
def get_current_invite(request, board_id: uuid.UUID):
    """Get current active invite for a board. Owner/staff only."""
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to view invites"}, status=403)
    invite = board.invites.filter(is_active=True).select_related("board", "created_by").first()
    if not invite:
        return router.api.create_response(request, {"detail": "No active invite found for this board"}, status=404)
    return invite


@router.post("/boards/{board_id}/invites", response={201: InviteOut}, auth=JWTAuth(), tags=["Invites"])
def create_invite(request, board_id: uuid.UUID, payload: InviteIn):
    """Create a new invite, deactivating existing active ones. Owner/staff only."""
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to create invites"}, status=403)

    # Validate expires_in_days
    if payload.expires_in_days <= 0:
        return router.api.create_response(request, {"detail": "expires_in_days must be positive"}, status=400)

    # Validate max_uses
    if payload.max_uses is not None and payload.max_uses <= 0:
        return router.api.create_response(request, {"detail": "max_uses must be a positive number or null (Unlimited)"}, status=400)

    with transaction.atomic():
        # Deactivate all existing active invites for this board
        board.invites.filter(is_active=True).update(is_active=False)

        invite = Invite.objects.create(
            board=board,
            max_uses=payload.max_uses,
            used_count=0,
            expire_at=timezone.now() + timedelta(days=payload.expires_in_days),
            is_active=True,
            created_by=user,
        )

    return 201, invite


@router.get("/invites/{invite_id}", auth=JWTAuth(), tags=["Invites"])
def get_invite(request, invite_id: uuid.UUID):
    """Get invite details. Owner/staff get full info; others get safe public info."""
    user = request.auth
    invite = get_object_or_404(Invite.objects.select_related("board", "created_by"), id=invite_id)

    if can_edit_board(user, invite.board):
        return InviteOut.from_orm(invite)
    # Any authenticated user can see public info to decide whether to join
    return InvitePublicOut.from_orm(invite)


@router.patch("/invites/{invite_id}", response=InviteOut, auth=JWTAuth(), tags=["Invites"])
def patch_invite(request, invite_id: uuid.UUID, payload: InvitePatchIn):
    """Update invite settings. Owner/staff only."""
    user = request.auth
    invite = get_object_or_404(Invite.objects.select_related("board", "created_by"), id=invite_id)
    if not can_edit_board(user, invite.board):
        return router.api.create_response(request, {"detail": "No permission to update this invite"}, status=403)

    # max_uses validation
    if payload.max_uses is not None:
        if payload.max_uses == 0:
            return router.api.create_response(request, {"detail": "max_uses cannot be 0. Use null for unlimited."}, status=400)
        if payload.max_uses < invite.used_count:
            return router.api.create_response(
                request,
                {"detail": f"max_uses ({payload.max_uses}) cannot be less than used_count ({invite.used_count})"},
                status=400,
            )
        invite.max_uses = payload.max_uses
    elif "max_uses" in payload.model_fields_set:
        # explicitly set to null → Unlimited
        invite.max_uses = None

    # expire_at handling — supports expires_in_days OR explicit expire_at
    if payload.expires_in_days is not None:
        if payload.expires_in_days <= 0:
            return router.api.create_response(request, {"detail": "expires_in_days must be positive"}, status=400)
        invite.expire_at = timezone.now() + timedelta(days=payload.expires_in_days)
    elif payload.expire_at is not None:
        if payload.is_active is not False and payload.expire_at <= timezone.now():
            return router.api.create_response(request, {"detail": "expire_at must be in the future for an active invite"}, status=400)
        invite.expire_at = payload.expire_at

    if payload.is_active is not None:
        invite.is_active = payload.is_active

    invite.save()
    return invite


@router.delete("/invites/{invite_id}", auth=JWTAuth(), tags=["Invites"])
def deactivate_invite(request, invite_id: uuid.UUID):
    """Soft-deactivate an invite (is_active = False). Owner/staff only."""
    user = request.auth
    invite = get_object_or_404(Invite.objects.select_related("board"), id=invite_id)
    if not can_edit_board(user, invite.board):
        return router.api.create_response(request, {"detail": "No permission to deactivate this invite"}, status=403)

    invite.is_active = False
    invite.save()
    return {"success": True, "message": "Invite deactivated"}


@router.post("/invites/{invite_id}/join", auth=JWTAuth(), tags=["Invites"])
def join_board_via_invite(request, invite_id: uuid.UUID):
    """Join a board using an invite link. Any authenticated user."""
    user = request.auth
    invite = get_object_or_404(Invite.objects.select_related("board"), id=invite_id)
    board = invite.board

    # Validate invite usability
    if not invite.is_active:
        return router.api.create_response(request, {"detail": "This invite is no longer active"}, status=400)
    if invite.is_expired():
        return router.api.create_response(request, {"detail": "This invite has expired"}, status=400)
    if invite.is_exhausted():
        return router.api.create_response(request, {"detail": "This invite has reached its maximum number of uses"}, status=400)

    # Check if user is already owner or member
    if board.owner == user:
        return router.api.create_response(
            request,
            {"detail": "You are already the owner of this board"},
            status=200,
        )
    if board.members.filter(id=user.id).exists():
        return router.api.create_response(
            request,
            {"detail": "You are already a member of this board"},
            status=200,
        )

    with transaction.atomic():
        board.members.add(user)
        # Increment used_count only for new joins
        Invite.objects.filter(id=invite.id).update(used_count=models.F("used_count") + 1)

    return {"success": True, "message": f"You have joined the board '{board.name}'"}


# ---------------------------------------------------------------------------
# --- Members Endpoints ---
# ---------------------------------------------------------------------------


@router.get("/boards/{board_id}/members", response=List[MemberOut], auth=JWTAuth(), tags=["Members"])
def list_board_members(request, board_id: uuid.UUID):
    """List all members (including owner) of a board."""
    from django.contrib.auth.models import User
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(user, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)

    result = []

    # Include owner first
    owner = board.owner
    try:
        owner_profile = owner.profile
        owner_name = owner_profile.name
        owner_role = owner_profile.role
    except Exception:
        owner_name = owner.username
        owner_role = ""
    result.append(MemberOut(
        username=owner.username,
        name=owner_name,
        role=owner_role,
        is_owner=True,
    ))

    # Include all members (excluding owner to avoid duplicate)
    for member in board.members.select_related("profile").exclude(id=owner.id):
        try:
            profile = member.profile
            m_name = profile.name
            m_role = profile.role
        except Exception:
            m_name = member.username
            m_role = ""
        result.append(MemberOut(
            username=member.username,
            name=m_name,
            role=m_role,
            is_owner=False,
        ))

    return result


@router.delete("/boards/{board_id}/members/{username}", auth=JWTAuth(), tags=["Members"])
def remove_member(request, board_id: uuid.UUID, username: str):
    """Remove a member from a board. Owner/staff only. Cannot remove the board owner."""
    from django.contrib.auth.models import User
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to remove members"}, status=403)

    target_user = get_object_or_404(User, username=username)

    if board.owner == target_user:
        return router.api.create_response(request, {"detail": "Cannot remove the board owner"}, status=400)

    if not board.members.filter(id=target_user.id).exists():
        return router.api.create_response(
            request,
            {"detail": f"User '{username}' is not a member of this board"},
            status=404,
        )

    board.members.remove(target_user)
    return {"success": True, "message": f"User '{username}' has been removed from the board"}


@router.post("/boards/{board_id}/leave", auth=JWTAuth(), tags=["Members"])
def leave_board(request, board_id: uuid.UUID):
    """Leave a board. Current user must be a member. Owner cannot leave."""
    user = request.auth
    board = get_object_or_404(Board, id=board_id)

    if board.owner == user:
        return router.api.create_response(
            request,
            {"detail": "Owner cannot leave the board. Transfer ownership first."},
            status=400,
        )

    if not board.members.filter(id=user.id).exists():
        return router.api.create_response(
            request,
            {"detail": "You are not a member of this board"},
            status=400,
        )

    board.members.remove(user)
    return {"success": True, "message": f"You have left the board '{board.name}'"}


# ---------------------------------------------------------------------------
# --- Task Endpoints ---
# ---------------------------------------------------------------------------

@router.get("/boards/{board_id}/tasks", response=List[TaskOut], auth=JWTAuth(), tags=["Tasks"])
@paginate
def list_tasks(
    request, 
    board_id: uuid.UUID,
    status: Optional[TaskStatus] = Query(None),
    column_id: Optional[uuid.UUID] = Query(None),
    column_kind: Optional[str] = Query(None),
    priority: Optional[int] = Query(None),
    assignee: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(user, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)

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


@router.get("/boards/{board_id}/backlog/tasks", response=List[TaskOut], auth=JWTAuth(), tags=["Tasks"])
@paginate
def list_backlog_tasks(
    request,
    board_id: uuid.UUID,
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[int] = Query(None),
    assignee: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(user, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)

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


@router.get("/columns/{column_id}/tasks", response=List[TaskOut], auth=JWTAuth(), tags=["Tasks"])
@paginate
def list_column_tasks(request, column_id: uuid.UUID, status: Optional[TaskStatus] = Query(None)):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not has_board_access(user, column.board):
        return router.api.create_response(request, {"detail": "No access to this column"}, status=403)

    tasks = column.tasks.all()
    if status:
        tasks = tasks.filter(status=status)
    return tasks


@router.get("/tasks/{task_id}", response=TaskOut, auth=JWTAuth(), tags=["Tasks"])
def get_task(request, task_id: uuid.UUID):
    user = request.auth
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(user, task.column.board):
        return router.api.create_response(request, {"detail": "No access to this task"}, status=403)
    return task


@router.post("/boards/{board_id}/tasks", response={201: TaskOut}, auth=JWTAuth(), tags=["Tasks"])
def create_board_task(request, board_id: uuid.UUID, payload: TaskIn):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(user, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)

    with transaction.atomic():
        if payload.column_id:
            column = get_object_or_404(Column, id=payload.column_id, board=board)
        else:
            column = Column.objects.filter(board=board, kind=ColumnKind.BACKLOG, status=ColumnStatus.ACTIVE).first()
            if not column:
                column = Column.objects.create(
                    board=board,
                    name="Backlog",
                    kind=ColumnKind.BACKLOG,
                    status=ColumnStatus.ACTIVE,
                    position=1
                )
        
        max_pos = column.tasks.aggregate(models.Max("position"))["position__max"] or 0
        
        assignees = []
        if payload.assignees:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            assignees = list(User.objects.filter(username__in=payload.assignees))
            if len(assignees) != len(payload.assignees):
                return router.api.create_response(request, {"detail": "One or more assignees not found"}, status=400)
            for a in assignees:
                if not has_board_access(a, board):
                    return router.api.create_response(request, {"detail": f"Assignee {a.username} has no access to board"}, status=400)
                    
        clean_checklist = []
        if payload.checklist:
            for item in payload.checklist:
                item_dict = item.dict() if hasattr(item, "dict") else item
                if isinstance(item_dict, dict) and "title" in item_dict and isinstance(item_dict["title"], str) and item_dict["title"].strip():
                    clean_checklist.append({"title": item_dict["title"], "is_done": item_dict.get("is_done", False)})
                
        task = Task.objects.create(
            column=column,
            title=payload.title,
            content=payload.content or "",
            priority=payload.priority or 0,
            deadline=payload.deadline,
            owner=user,
            position=max_pos + 1,
            tags=[t for t in payload.tags if t] if payload.tags else [],
            checklist=clean_checklist
        )
        
        if assignees:
            task.assignees.set(assignees)
            
        recalculate_board_progress(board)
        
    return 201, task


@router.post("/columns/{column_id}/tasks", response={201: TaskOut}, auth=JWTAuth(), tags=["Tasks"])
def create_column_task(request, column_id: uuid.UUID, payload: TaskIn):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not has_board_access(user, column.board):
        return router.api.create_response(request, {"detail": "No access to this column"}, status=403)

    payload.column_id = column.id
    return create_board_task(request, column.board.id, payload)


@router.patch("/tasks/{task_id}", response=TaskOut, auth=JWTAuth(), tags=["Tasks"])
def update_task(request, task_id: uuid.UUID, payload: TaskUpdateIn):
    user = request.auth
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board
    
    if not has_board_access(user, board):
        return router.api.create_response(request, {"detail": "No permission to edit this task"}, status=403)

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
            new_col = get_object_or_404(Column, id=payload.column_id, board=board)
            task.column = new_col
            max_pos = new_col.tasks.aggregate(models.Max("position"))["position__max"] or 0
            task.position = max_pos + 1

        if payload.tags is not None:
            task.tags = [t for t in payload.tags if t]
            
        if payload.checklist is not None:
            clean_checklist = []
            for item in payload.checklist:
                item_dict = item.dict() if hasattr(item, "dict") else item
                if isinstance(item_dict, dict) and "title" in item_dict and isinstance(item_dict["title"], str) and item_dict["title"].strip():
                    clean_checklist.append({"title": item_dict["title"], "is_done": item_dict.get("is_done", False)})
            task.checklist = clean_checklist
            
        if payload.assignees is not None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            assignees = list(User.objects.filter(username__in=payload.assignees))
            if len(assignees) != len(payload.assignees):
                return router.api.create_response(request, {"detail": "One or more assignees not found"}, status=400)
            for a in assignees:
                if not has_board_access(a, board):
                    return router.api.create_response(request, {"detail": f"Assignee {a.username} has no access to board"}, status=400)
            task.assignees.set(assignees)
            
        task.save()
        recalculate_board_progress(board)

    return task


@router.post("/tasks/{task_id}/archive", response=TaskOut, auth=JWTAuth(), tags=["Tasks"])
def archive_task(request, task_id: uuid.UUID):
    user = request.auth
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(user, task.column.board):
        return router.api.create_response(request, {"detail": "No access to this task"}, status=403)

    task.status = TaskStatus.ARCHIVED
    task.save()
    recalculate_board_progress(task.column.board)
    return task


@router.post("/tasks/{task_id}/restore", response=TaskOut, auth=JWTAuth(), tags=["Tasks"])
def restore_task(request, task_id: uuid.UUID):
    user = request.auth
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(user, task.column.board):
        return router.api.create_response(request, {"detail": "No access to this task"}, status=403)

    task.status = TaskStatus.ACTIVE
    task.save()
    recalculate_board_progress(task.column.board)
    return task


@router.delete("/tasks/{task_id}", auth=JWTAuth(), tags=["Tasks"])
def delete_task(request, task_id: uuid.UUID):
    user = request.auth
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(user, task.column.board):
        return router.api.create_response(request, {"detail": "No access to this task"}, status=403)

    task.status = TaskStatus.ARCHIVED
    task.save()
    recalculate_board_progress(task.column.board)
    return {"success": True, "message": "Task archived"}
