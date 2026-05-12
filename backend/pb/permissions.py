from django.db.models import Q


def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser


def has_board_access(user, board):
    if is_staff_or_superuser(user):
        return True
    return board.owner == user or board.members.filter(id=user.id).exists()


def has_project_access(user, project):
    if is_staff_or_superuser(user):
        return True
    # User has access to project if they have access to at least one board in it
    return project.boards.filter(Q(owner=user) | Q(members=user)).exists()


def can_edit_project(user, project):
    if is_staff_or_superuser(user):
        return True
    # User can edit a project if they are owner of at least one board in it
    return project.boards.filter(owner=user).exists()


def can_edit_board(user, board):
    if is_staff_or_superuser(user):
        return True
    return board.owner == user


def can_edit_column(user, column):
    if is_staff_or_superuser(user):
        return True
    return column.board.owner == user
