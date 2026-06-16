from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
import uuid

def broadcast_board_event(board_id: uuid.UUID, event_type: str, payload: dict, actor_id: uuid.UUID = None):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    
    event_data = {
        "type": event_type,
        "board_id": str(board_id),
        "payload": payload,
        "actor_id": str(actor_id) if actor_id else None,
        "created_at": timezone.now().isoformat()
    }
    
    async_to_sync(channel_layer.group_send)(
        f"board_{board_id}",
        {
            "type": "board.message",
            "event": event_data
        }
    )
