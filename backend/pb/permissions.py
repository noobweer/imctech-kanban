from django.db.models import Q


def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser


def get_user_role(user) -> str | None:
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", None)


def is_mentor(user) -> bool:
    if is_staff_or_superuser(user):
        return False
    return get_user_role(user) == "mentor"


def is_student(user) -> bool:
    if is_staff_or_superuser(user):
        return False
    return get_user_role(user) == "student"


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
    if project.boards.filter(owner=user).exists():
        return True
    return is_mentor(user) and project.boards.filter(members=user).exists()


def can_edit_board(user, board):
    if is_staff_or_superuser(user):
        return True
    if board.owner == user:
        return True
    return is_mentor(user) and board.members.filter(id=user.id).exists()


def can_edit_column(user, column):
    return can_edit_board(user, column.board)


def can_modify_task(user, task) -> bool:
    if is_staff_or_superuser(user):
        return True
    if is_mentor(user):
        return False
    return has_board_access(user, task.column.board)


def can_create_task(user, board) -> bool:
    if is_staff_or_superuser(user):
        return True
    if is_mentor(user):
        return False
    return has_board_access(user, board)
