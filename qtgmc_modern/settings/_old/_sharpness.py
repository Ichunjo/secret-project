from __future__ import annotations

from typing import Literal, TypedDict


class SharpnessSettings(TypedDict):
    strength: float
    mode: Literal[0, 1, 2]
    lmode: Literal[0, 1, 2, 3, 4]
    lrad: int | Literal[0, 1, 3]
    ovs: int
    vthin: float
    bb: Literal[0, 1, 2, 3]
