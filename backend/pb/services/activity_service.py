from pb.models import ActivityLog
from pb.middleware import get_current_user

def create_log(board, action_type, metadata=None):
    user = get_current_user()
    return ActivityLog.objects.create(
        board=board,
        actor=user,
        action_type=action_type,
        metadata=metadata or {}
    )
