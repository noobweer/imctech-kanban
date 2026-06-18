import uuid
import json
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
from ..services.ws_service import broadcast_board_event

router = Router(auth=JWTAuth())

def _serialize(schema_cls, obj):
    return json.loads(schema_cls.from_orm(obj).json())

@router.get("/{request_id}", response=MentorRequestOut)
def get_request(request, request_id: uuid.UUID):
    return get_mentor_request(request.user, request_id)

@router.post("/{request_id}/respond", response={200: dict})
def respond_request(request, request_id: uuid.UUID, payload: MentorRequestRespondIn):
    request_obj = get_object_or_404(TaskMentorRequest, id=request_id)
    is_first_response = request_obj.status == "open"
    updated_req, comment = respond_to_mentor_request(request.user, request_obj, payload.content)
    
    board_id = updated_req.task.column.board_id
    if is_first_response:
        broadcast_board_event(board_id, "mentor_request.started", _serialize(MentorRequestOut, updated_req), request.user.id)
    
    broadcast_board_event(board_id, "comment.created", _serialize(TaskCommentOut, comment), request.user.id)
    
    return 200, {
        "mentor_request": MentorRequestOut.from_orm(updated_req),
        "comment": TaskCommentOut.from_orm(comment)
    }

@router.post("/{request_id}/resolve", response=MentorRequestOut)
def resolve_request(request, request_id: uuid.UUID):
    request_obj = get_object_or_404(TaskMentorRequest, id=request_id)
    updated_req = resolve_mentor_request(request.user, request_obj)
    broadcast_board_event(updated_req.task.column.board_id, "mentor_request.resolved", _serialize(MentorRequestOut, updated_req), request.user.id)
    return updated_req

@router.post("/{request_id}/cancel", response=MentorRequestOut)
def cancel_request(request, request_id: uuid.UUID, payload: MentorRequestCancelIn):
    request_obj = get_object_or_404(TaskMentorRequest, id=request_id)
    updated_req = cancel_mentor_request(request.user, request_obj, payload.close_reason)
    broadcast_board_event(updated_req.task.column.board_id, "mentor_request.cancelled", _serialize(MentorRequestOut, updated_req), request.user.id)
    return updated_req
