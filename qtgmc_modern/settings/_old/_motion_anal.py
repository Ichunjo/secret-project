# from __future__ import annotations

# from enum import IntEnum
# from typing import Any, Dict, Literal, NamedTuple, Optional


# class SearchPre(IntEnum):
#     """Pre-filtering for motion search clip"""
#     NONE = 0
#     SIMPLE_BLUR = 1
#     GAUSSIAN = 2
#     GAUSSIAN_EDGE_SOFTEN = 3


# class SubPel(IntEnum):
#     """Sub-pixel accuracy for motion analysis"""
#     ONE = 1
#     HALF = 2
#     QUARTER = 4


# class SubPelInter(IntEnum):
#     """Interpolation used for sub-pixel motion analysis"""
#     BILINEAR = 0
#     BICUBIC = 1
#     WEINER = 2


# class Search(IntEnum):
#     ONETIME = 0
#     NSTEP = 1
#     LOGARITHMIC = 2
#     EXHAUSTIVE = 3
#     HEXAGON = 4
#     UNEVEN_MULTI_HEXAGON = 5
#     HORIZONTAL_EXHAUSTIVE = 6
#     VERTICAL_EXHAUSTIVE = 7


# class PLevel(IntEnum):
#     """Penality factor lambda level scaling mode"""
#     NO_SCALING = 0
#     LINEAR = 1
#     QUADRATIC = 2
#     """Quadratic dependence from hierarchical level size"""


# class MotionAnalysisSettings(NamedTuple):
#     searchpre: SearchPre
#     """Pre-filtering for motion search clip | SrchClipPP"""
#     subpel: SubPel | Literal[1, 2, 4]
#     subpel_inter: SubPelInter | Literal[0, 1, 2]
#     blocksize: Literal[4, 8, 16, 32]
#     overlap: int
#     search: Search | Literal[0, 1, 2, 3, 4, 5, 6, 7]
#     search_param: Search | Literal[0, 1, 2, 3, 4, 5, 6, 7]
#     pelsearch: SubPel | Literal[1, 2, 4]
#     chroma_motion: bool
#     truemotion: bool = False
#     lambda_: Optional[int] = None
#     lsad: Optional[int] = None
#     pnew: Optional[int] = None
#     plevel: Optional[int] = None
#     globalmotion: bool = True
#     dct: int = 0
#     thsad_initial_output: int = 640
#     thsad_final_output: int = 256
#     thscd1: int = 180
#     thscd2: int = 98

#     def fill_empty(self) -> MotionAnalysisSettings:
#         kwargs: Dict[str, Any] = {}
#         if self.lambda_ is None:
#             kwargs.update(lambda_=(1000 if self.truemotion else 100) * self.blocksize * self.blocksize // 64)
#         if self.lsad is None:
#             kwargs.update(lsad=1200 if self.truemotion else 400)
#         if self.pnew is None:
#             kwargs.update(pnew=50 if self.truemotion else 25)
#         if self.plevel is None:
#             kwargs.update(plevel=1 if self.truemotion else 0)
#         if kwargs:
#             return self._replace(**kwargs)
#         return self
