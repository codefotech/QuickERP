import json
from channels.generic.websocket import AsyncWebsocketConsumer


class RouterDataConsumer(AsyncWebsocketConsumer):
    roomGroupName = "group_chat_gfg"

    async def connect(self):
        await self.channel_layer.group_add(
            self.roomGroupName ,
            self.channel_name
        )
        await self.accept()
    async def disconnect(self , close_code):
        await self.channel_layer.group_discard(
            self.roomGroupName ,
            self.channel_layer
        )
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        await self.channel_layer.group_send(
            self.roomGroupName,{
                "type" : "sendMessage" ,
                "message" : message ,
                "username" : username ,
            })
    async def sendMessage(self , event) :
        message = event["message"]
        username = event["username"]
        await self.send(text_data = json.dumps({"message":message ,"username":username}))


class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            decoded_string = self.scope.get('query_string').decode('utf-8')  # Decode the bytes string
            key_value_parts = decoded_string.split('=')
            self.user_id = key_value_parts[1]
            self.roomGroupName = f"group_chat_gfg_{self.user_id}"  # Use the user ID to create a unique group name
            await self.channel_layer.group_add(
                self.roomGroupName,
                self.channel_name
            )
            print('ok')
            await self.accept()

        except Exception as e:
            error_message = f"An error occurred router 103.20.242.22: {e}"
            await self.send(text_data=json.dumps({'error': error_message}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.roomGroupName,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        await self.channel_layer.group_send(
            self.roomGroupName, {
                "type": "sendMessage",
                "message": message,
                "username": username,
            })

    async def sendMessage(self, event):
        message = event["message"]
        username = event["username"]
        await self.send(text_data=json.dumps({"message": message, "username": username}))
