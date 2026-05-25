from django.db.models import Q

from ..models import Project


def list_projects(user):
    if user.is_staff or user.is_superuser:
        return Project.objects.all()
    return Project.objects.filter(Q(boards__owner=user) | Q(boards__members=user)).distinct()


def create_project(name: str) -> Project:
    return Project.objects.create(name=name)


def get_project(project_id) -> Project:
    return Project.objects.get(id=project_id)


def update_project(project: Project, name: str) -> Project:
    project.name = name
    project.save()
    return project


def delete_project(project: Project) -> None:
    if project.boards.exists():
        raise ValueError("Cannot delete project with associated boards. Delete boards first.")
    project.delete()
