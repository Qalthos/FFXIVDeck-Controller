from functools import wraps
import json

from loguru import logger as log
import requests
from streamcontroller_plugin_tools import BackendBase
import websocket


INIT = {
    "Opcode": "init",
    "Version": "0.3.999",
    "Mode": "Developer",
}


class FFXIVDeckProxy(BackendBase):
    host: str = "127.0.0.1"
    port: int = 37984
    api_key: str = ""
    _connected: bool = False

    ws: websocket.WebSocket
    session: requests.Session

    def __init__(self):
        super().__init__()

        self.ws = websocket.WebSocket()
        self.session = requests.Session()

    def connect(self) -> None:
        url = f"ws://{self.host}:{self.port}/ws"
        log.debug(f"Connecting to {url}")
        self.ws.connect(url)

        payload = json.dumps(INIT)
        self.ws.send(payload)
        resp = self.ws.recv()
        log.debug(resp)

        reply = json.loads(resp)
        self.api_key = reply["apiKey"]
        self.session.headers["Authorization"] = f"Bearer {self.api_key}"
        self._connected = True

    def ensure_connect(func):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            if not self._connected:
                self.connect()
            try:
                return func(self, *args, **kwargs)
            except requests.exceptions.HTTPError as exc:
                self._connected = False
                self.api_key = ""

                # Try again
                self.connect()
                return func(self, *args, **kwargs)

        return wrapped

    # HTTP methods and properties
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}/"

    @ensure_connect
    def get_json(self, path: str):
        log.debug(f"Requesting {self.base_url}{path}")
        try:
            resp = self.session.get(self.base_url + path, timeout=2)
            log.debug(resp.text)
            log.debug(resp.status_code)
            resp.raise_for_status()
            try:
                return resp.json()
            except json.decoder.JSONDecodeError as exc:
                log.error(exc)
                raise
        except Exception as exc:
            log.error(exc)
            raise

    @ensure_connect
    def post(self, path: str, data: str = "") -> str:
        log.debug(f"Sending {data} to {self.base_url}{path}")
        try:
            resp = self.session.post(self.base_url + path, data=data.encode("utf8"), timeout=2)
            log.debug(resp.text)
            log.debug(resp.status_code)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:
            log.error(exc)
            raise

backend = FFXIVDeckProxy()
