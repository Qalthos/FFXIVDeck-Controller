import json

from loguru import log
import websocket


INIT = {
    "Opcode": "init",
    "Version": "0.3.999",
    "Mode": "Developer",
}


class FFXIVDeckProxy:
    host: str = "127.0.0.1"
    port: int = 37984
    api_key: str = ""
    ws: websocket.WebSocket

    def __init__(self):
        self.ws = websocket.WebSocket()

    def connect(self) -> None:
        url = f"ws://{self.host}:{self.port}"
        log.debug(f"Connecting to {url}")
        self.ws.connect(url)

        payload = json.dumps(INIT)
        self.ws.send(payload)
        resp = self.ws.recv()
        log.debug(resp)

        reply = json.loads(resp)
        self.api_key = reply["apiKey"]

    @property
    def is_connected(self) -> bool:
        return self.ws.connected
