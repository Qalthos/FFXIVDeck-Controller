from functools import wraps
import json
import threading
import time

from loguru import logger as log
import requests
from streamcontroller_plugin_tools import BackendBase
import websocket


INIT = {
    "Opcode": "init",
    "Version": "0.3.999",
    "Mode": "Developer",
}


class XIVDeckProxy(BackendBase):
    host: str = "127.0.0.1"
    port: int = 37984
    api_key: str = ""
    _connected: bool = False

    session: requests.Session

    def __init__(self):
        super().__init__()

        self.session = requests.Session()

    def connect(self) -> None:
        url = f"ws://{self.host}:{self.port}/ws"
        log.debug(f"Connecting to {url}")
        ws = websocket.WebSocketApp(
            url,
            on_open=self.ws_open,
            on_message=self.ws_msg,
            on_close=self.ws_close,
        )
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()

    def disconnect(self) -> None:
        self.api_key = ""
        self._connected = False

    # websocket callbacks
    def ws_open(self, ws: websocket.WebSocket) -> None:
        payload = json.dumps(INIT)
        ws.send(payload)

    def ws_msg(self, ws: websocket.WebSocket, msg: str) -> None:
        log.debug(f"Recieved websocket message {msg}")
        match json.loads(msg):
            case {"messageType": "initReply", "apiKey": api_key, "version": version}:
                log.debug(f"Setting API key to {api_key}")
                self.api_key = api_key
                self.session.headers["Authorization"] = f"Bearer {self.api_key}"
                self._connected = True
            case _:
                log.debug(f"Unhandled message: {msg}")

    def ws_close(self, ws: websocket.WebSocket) -> None:
        self.disconnect()
        log.debug("Websocket has closed")

    def ensure_connect(func):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            if not self._connected:
                self.connect()
                while not self._connected:
                    time.sleep(0.1)
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
            resp = self._request(path)
            try:
                return json.loads(resp)
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
            return self._request(path, data=data, method="POST")
        except Exception as exc:
            log.error(exc)
            raise

    def _request(self, path: str, data: str = "", method: str = "GET") -> str:
        log.debug(f"API key: {self.api_key}")
        log.debug(self.session.headers)
        resp = self.session.request(
            method=method,
            url=self.base_url + path,
            data=data.encode("utf8"),
            timeout=2
        )
        log.debug(f"Returned {resp.status_code}: {resp.text!r}")
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            self.disconnect()
            raise

        return resp.text


backend = XIVDeckProxy()
