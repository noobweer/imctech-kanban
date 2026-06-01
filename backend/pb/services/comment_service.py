import uuid
from typing import List, Optional
from django.utils import timezone
from django.db.models import Max
from django.shortcuts import get_object_or_404

from ..models import Task, Board, TaskComment, TaskCommentReadState
from ..permissions import (
    can_read_task_comments,
    can_create_task_comment,
    can_edit_task_comment,
    can_delete_task_comment,
    has_board_access,
)


def list_task_comments(user, task: Task) -> List[TaskComment]:
    if not can_read_task_comments(user, task):
        raise PermissionError("BOARD_ACCESS_DENIED")

    return list(task.comments.filter(is_deleted=False))


def create_task_comment(user, task: Task, content: str, links: Optional[List[str]] = None) -> TaskComment:
    if not can_create_task_comment(user, task):
        raise PermissionError("COMMENT_CREATE_FORBIDDEN")

    if not content or not content.strip():
        raise ValueError("COMMENT_CONTENT_REQUIRED")

    comment = TaskComment.objects.create(
        task=task,
        owner=user,
        content=content.strip(),
        links=links or []
    )

    # Update read state for the author
    mark_comments_as_read(user, task)

    return comment


def update_task_comment(user, comment: TaskComment, content: Optional[str] = None, links: Optional[List[str]] = None) -> TaskComment:
    if comment.is_deleted:
        raise ValueError("COMMENT_NOT_FOUND")

    if not can_edit_task_comment(user, comment):
        raise PermissionError("COMMENT_EDIT_FORBIDDEN")

    if content is not None:
        if not content or not content.strip():
            raise ValueError("COMMENT_CONTENT_REQUIRED")
        comment.content = content.strip()

    if links is not None:
        comment.links = links

    comment.save()
    return comment


def soft_delete_task_comment(user, comment: TaskComment) -> None:
    if comment.is_deleted:
        return

    if not can_delete_task_comment(user, comment):
        raise PermissionError("COMMENT_DELETE_FORBIDDEN")

    comment.is_deleted = True
    comment.deleted_at = timezone.now()
    comment.save()


def mark_comments_as_read(user, task: Task) -> TaskCommentReadState:
    if not can_read_task_comments(user, task):
        raise PermissionError("BOARD_ACCESS_DENIED")

    state, created = TaskCommentReadState.objects.update_or_create(
        task=task,
        user=user,
        defaults={"last_read_at": timezone.now()}
    )
    return state


def get_task_comment_state(user, task: Task) -> dict:
    if not can_read_task_comments(user, task):
        raise PermissionError("BOARD_ACCESS_DENIED")

    # To avoid N+1 when called from get_board_comments_states (if prefetched),
    # we filter in Python if possible, but for simplicity let's rely on Django cache or manager
    # Since we need to work with both single task and list of tasks, we do it safely:
    all_comments = task.comments.all()
    active_comments = [c for c in all_comments if not c.is_deleted]
    comments_count = len(active_comments)

    if comments_count == 0:
        return {
            "task_id": task.id,
            "comments_count": 0,
            "has_comments": False,
            "has_unread_comments": False,
            "last_comment_at": None,
            "comments_state": "none"
        }

    last_comment_at = max(c.created_at for c in active_comments)
    
    # Get read state for this user
    all_read_states = task.comment_read_states.all()
    read_state = next((rs for rs in all_read_states if rs.user_id == user.id), None)

    if not read_state:
        has_others_comments = any(c.owner_id != user.id for c in active_comments)
        has_unread = has_others_comments
    else:
        has_unread = any(
            c.created_at > read_state.last_read_at and c.owner_id != user.id
            for c in active_comments
        )

    comments_state = "unread" if has_unread else "read"

    return {
        "task_id": task.id,
        "comments_count": comments_count,
        "has_comments": True,
        "has_unread_comments": has_unread,
        "last_comment_at": last_comment_at,
        "comments_state": comments_state
    }


def get_board_comments_states(user, board: Board, task_ids: Optional[List[uuid.UUID]] = None) -> List[dict]:
    if not has_board_access(user, board):
        raise PermissionError("BOARD_ACCESS_DENIED")

    # Efficient fetching
    qs = Task.objects.filter(column__board=board)
    if task_ids is not None:
        qs = qs.filter(id__in=task_ids)

    qs = qs.prefetch_related("comments", "comment_read_states")
    
    states = []
    for task in qs:
        states.append(get_task_comment_state(user, task))

    return states
