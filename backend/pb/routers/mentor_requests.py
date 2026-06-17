import uuid
from typing import Optional
from ninja import Router
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth

from ..models import TaskMentorRequest
from ..schemas import MentorRequestRespondIn, MentorRequestCancelIn, MentorRequestOut, TaskCommentOut
from ..services.mentor_request_service import (
    get_mentor_request,
    respond_to_mentor_request,
    resolve_mentor_request,
    cancel_mentor_request,
)

router = Router(auth=JWTAuth())


@router.get("/{request_id}", response=MentorRequestOut)
def get_request(request, request_id: uuid.UUID):
    """
    Get a single mentor request by id.
    """
    return get_mentor_request(request.user, request_id)


@router.post("/{request_id}/respond", response={200: dict})
def respond_request(request, request_id: uuid.UUID, payload: MentorRequestRespondIn):
    """
    Mentor responds to a request.
    This creates a comment and sets the request to 'in_progress'.
    Returns the updated request and the created comment.
    """
    request_obj = get_object_or_404(TaskMentorRequest, id=request_id)
    updated_req, comment = respond_to_mentor_request(request.user, request_obj, payload.content)
    
    # We serialize manually or use schemas. We can return dict for simplicity
    from ..schemas import MentorRequestOut, TaskCommentOut
    return 200, {
        "mentor_request": MentorRequestOut.from_orm(updated_req),
        "comment": TaskCommentOut.from_orm(comment)
    }


@router.post("/{request_id}/resolve", response=MentorRequestOut)
def resolve_request(request, request_id: uuid.UUID):
    """
    Author marks request as resolved.
    """
    request_obj = get_object_or_404(TaskMentorRequest, id=request_id)
    return resolve_mentor_request(request.user, request_obj)


@router.post("/{request_id}/cancel", response=MentorRequestOut)
def cancel_request(request, request_id: uuid.UUID, payload: MentorRequestCancelIn):
    """
    Cancel a request without a resolution.
    """
    request_obj = get_object_or_404(TaskMentorRequest, id=request_id)
    return cancel_mentor_request(request.user, request_obj, payload.close_reason)
