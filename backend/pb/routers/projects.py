import uuid
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth

from ..models import Project
from ..schemas import ProjectIn, ProjectOut
from ..permissions import has_project_access, can_edit_project, is_student
from ..services import project_service

router = Router()


@router.get("/projects", response=List[ProjectOut], auth=JWTAuth())
@paginate
def list_projects(request):
    return project_service.list_projects(request.auth)


@router.post("/projects", response={201: ProjectOut}, auth=JWTAuth())
def create_project(request, payload: ProjectIn):
    if is_student(request.auth):
        return router.api.create_response(request, {"detail": "Student is not allowed to create projects or boards", "code": "STUDENT_ACTION_FORBIDDEN"}, status=403)
    project = project_service.create_project(payload.name)
    return 201, project


@router.get("/projects/{project_id}", response=ProjectOut, auth=JWTAuth())
def retrieve_project(request, project_id: uuid.UUID):
    project = get_object_or_404(Project, id=project_id)
    if not has_project_access(request.auth, project):
        return router.api.create_response(request, {"detail": "No access to this project"}, status=403)
    return project


@router.patch("/projects/{project_id}", response=ProjectOut, auth=JWTAuth())
def update_project(request, project_id: uuid.UUID, payload: ProjectIn):
    project = get_object_or_404(Project, id=project_id)
    if not can_edit_project(request.auth, project):
        return router.api.create_response(request, {"detail": "No permission to edit this project"}, status=403)
    return project_service.update_project(project, payload.name)


@router.delete("/projects/{project_id}", auth=JWTAuth())
def delete_project(request, project_id: uuid.UUID):
    project = get_object_or_404(Project, id=project_id)
    if not can_edit_project(request.auth, project):
        return router.api.create_response(request, {"detail": "No permission to delete this project"}, status=403)
    try:
        project_service.delete_project(project)
    except ValueError as e:
        return router.api.create_response(request, {"detail": str(e)}, status=400)
    return {"success": True}
