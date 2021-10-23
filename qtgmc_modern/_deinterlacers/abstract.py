
from abc import ABC, abstractmethod
from typing import Any, Dict

import vapoursynth as vs

core = vs.core


class Deinterlacer(ABC):
    field: int
    params: Dict[str, Any]

    def __init__(self, field: int, **kwargs: Any) -> None:
        self.field = field
        self.params = kwargs
        super().__init__()

    @abstractmethod
    def __call__(self, clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
        raise NotImplementedError
