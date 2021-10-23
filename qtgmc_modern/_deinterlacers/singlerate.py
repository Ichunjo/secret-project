
from abc import ABC, abstractmethod
from typing import Any, Dict

import vapoursynth as vs

from .abstract import Deinterlacer

core = vs.core


class SingleRater(Deinterlacer, ABC):
    def __init__(self, tff: bool, **kwargs: Any) -> None:
        super().__init__(tff, **kwargs)


class NNEDI3(SingleRater):
    """Neural Network Edge Directed Interpolation 3rd gen"""
    def __call__(self, clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
        return core.nnedi3.nnedi3(clip, self.field, **self.params | kwargs)


class NNEDI3CL(SingleRater):
    def __call__(self, clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
        return core.nnedi3cl.NNEDI3CL(clip, self.field, **self.params | kwargs)


class ZNEDI3(SingleRater):
    def __call__(self, clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
        return core.znedi3.nnedi3(clip, self.field, **self.params | kwargs)


class EEDI2(SingleRater):
    def __call__(self, clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
        return core.eedi2.EEDI2(clip, self.field, **self.params | kwargs)


class ThirdGenEEDI(SingleRater, ABC):
    ...


class EEDI3(ThirdGenEEDI):
    def __call__(self, clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
        return core.eedi3.eedi3(clip, self.field, **self.params | kwargs)


class EEDI3m(ThirdGenEEDI):
    def __call__(self, clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
        return core.eedi3m.EEDI3(clip, self.field, **self.params | kwargs)


class EEDI3mCL(ThirdGenEEDI):
    def __call__(self, clip: vs.VideoNode, **kwargs: Any) -> vs.VideoNode:
        return core.eedi3m.EEDI3CL(clip, self.field, **self.params | kwargs)
