from typing import NotRequired, TypedDict


class Opcode(TypedDict):
    Opcode: str


class InitOpcode(Opcode):
    Version: str
    Mode: str


class VolumePayload(TypedDict):
    Volume: NotRequired[int]
    Delta: NotRequired[int]
    Muted: NotRequired[bool]


class VolumeOpcode(Opcode):
    Channel: str
    Data: VolumePayload
