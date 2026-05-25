from django.contrib.auth import get_user_model

from ..models import Board
from ..schemas import MemberOut

User = get_user_model()


def list_members(board: Board) -> list:
    result = []
    owner = board.owner
    try:
        owner_profile = owner.profile
        owner_name = owner_profile.name
        owner_role = owner_profile.role
    except Exception:
        owner_name = owner.username
        owner_role = ""

    result.append(MemberOut(username=owner.username, name=owner_name, role=owner_role, is_owner=True))

    for member in board.members.select_related("profile").exclude(id=owner.id):
        try:
            profile = member.profile
            m_name = profile.name
            m_role = profile.role
        except Exception:
            m_name = member.username
            m_role = ""
        result.append(MemberOut(username=member.username, name=m_name, role=m_role, is_owner=False))

    return result


def remove_member(board: Board, username: str) -> None:
    target = User.objects.filter(username=username).first()
    if target is None:
        raise User.DoesNotExist(f"User '{username}' not found.")
    if board.owner == target:
        raise ValueError("Cannot remove the board owner.")
    if not board.members.filter(id=target.id).exists():
        raise LookupError(f"User '{username}' is not a member of this board.")
    board.members.remove(target)


def leave_board(board: Board, user) -> None:
    if board.owner == user:
        raise ValueError("Owner cannot leave the board. Transfer ownership first.")
    if not board.members.filter(id=user.id).exists():
        raise ValueError("You are not a member of this board.")
    board.members.remove(user)
