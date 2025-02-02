import json
import asyncio
import websockets

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.loop = asyncio.get_event_loop()

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)

    def send_message(self, msg):
        return self.loop.run_until_complete(self._send_message(msg))

    async def _send_message(self, msg):
        try:
            if self.websocket is None or self.websocket.closed:
                await self.connect()
            await self.websocket.send(json.dumps(msg))
            response = await self.websocket.recv()
            return response
        except websockets.exceptions.ConnectionClosed:
            return "Connection to WebSocket server closed"

# def create_websocket() -> WebSocketClient:
#     websocket_uri = "wss://socket.stage-aitanmall.tech:59001"
#     websocket = WebSocketClient(websocket_uri)
#     return websocket

# def connect_websocket(websocket:WebSocketClient):
#     if not isinstance(websocket, WebSocketClient):
#         raise Exception("Only websocket object can be used")
#     return websocket.connect()
    
# def send_message(websocket:WebSocketClient, message:dict):
#     if not isinstance(websocket, WebSocketClient):
#         raise Exception("Only websocket object can be used")
#     if not isinstance(message, dict):
#         raise Exception("Message need to be in form of dictionary. E.g: {'key':'value'/}")
#     return websocket.send_message(message)
# @app.route('/websocket', methods=['POST'])
# def trigger_websocket():
#     msg = request.json.get('message', '')  # Get the message from the request body
#     response = client.send_message(msg)
#     return jsonify({'response': response})

# if __name__ == '__main__':
#     app.run(port=5000)