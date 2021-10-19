
__all__ = [
    'Kernel',

    'AbstractBicubic', 'AbstractWindowed', 'AbstractSpline',

    'ScaleIsCall'
]

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import vapoursynth as vs

core = vs.core


class Kernel(ABC):
    params: Dict[str, Any]

    def __init__(self, **kwargs: Any) -> None:
        self.params = kwargs
        super().__init__()

    @abstractmethod
    def __call__(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> vs.VideoNode:
        raise NotImplementedError

    @abstractmethod
    def scale(self, clip: vs.VideoNode, width: Optional[int], height: Optional[int], **kwargs: Any) -> vs.VideoNode:
        raise NotImplementedError

    @abstractmethod
    def descale(self, clip: vs.VideoNode, width: int, height: int, **kwargs: Any) -> vs.VideoNode:
        raise NotImplementedError


class AbstractBicubic(Kernel, ABC):
    b: float
    c: float

    def __init__(self, b: float = 0., c: float = 0.5, **kwargs: Any) -> None:
        self.b = b
        self.c = c
        super().__init__(**kwargs)


class AbstractWindowed(Kernel, ABC):
    taps: int

    def __init__(self, taps: int = 4, **kwargs: Any) -> None:
        self.taps = taps
        super().__init__(**kwargs)


class AbstractSpline(Kernel, ABC):
    sample_points: int

    def __init__(self, sample_points: int = 6, **kwargs: Any) -> None:
        self.sample_points = sample_points
        super().__init__(**kwargs)


class ScaleIsCall(Kernel, ABC):
    def scale(self, clip: vs.VideoNode, width: Optional[int], height: Optional[int], **kwargs: Any) -> vs.VideoNode:
        return self.__call__(clip, width, height, **kwargs)
