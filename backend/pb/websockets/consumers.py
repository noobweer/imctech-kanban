import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ..permissions import has_board_access
from ..models import Board

@database_sync_to_async
def check_board_access(user, board_id):
    if user.is_anonymous:
        return False
    try:
        board = Board.objects.get(id=board_id)
        return has_board_access(user, board)
    except Board.DoesNotExist:
        return False

class BoardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.board_id = self.scope['url_route']['kwargs']['board_id']
        self.room_group_name = f'board_{self.board_id}'
        self.user = self.scope.get('user')

        has_access = await check_board_access(self.user, self.board_id)
        print(f"WS Consumer: User={self.user}, Board={self.board_id}, HasAccess={has_access}")
        if not has_access:
            print("WS Consumer: Closing connection due to lack of access")
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def board_message(self, event):
        payload = event['event']
        await self.send(text_data=json.dumps(payload))
