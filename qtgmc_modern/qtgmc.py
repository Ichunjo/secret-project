
from __future__ import annotations

from abc import ABC
from functools import partial
from types import MappingProxyType
from typing import (Any, Callable, Dict, Literal, NamedTuple, Optional,
                    Sequence, Tuple)

import vapoursynth as vs
from vsutil import Range, get_y, iterate, scale_value
from vsutil.info import get_depth

from .deinterlacers import Deinterlacer, class2dict, dict2class
from .helper import clamp_value, merge_chroma
from .logger import add_logger, log_update
from .presets import CoreParam, Preset, Settings, load_preset

# from .settings import CoreSettings, Preset, Settings

core = vs.core


# class QTGMCSettings(MutableMapping[str, Any], ABC):
#     __default: Dict[str, Any]
#     _settings: Dict[str, Any]

#     def __init__(self, **kwargs: Any) -> None:
#         self.__default = kwargs
#         self._settings = kwargs
#         super().__init__()

#     def __getitem__(self, k: str) -> Any:
#         return self._settings[k]

#     def __setitem__(self, k: str, v: Any) -> None:
#         if k in self._settings:
#             self._settings[k] = v
#         else:
#             raise ValueError

#     def __delitem__(self, v: str) -> None:
#         self._settings[v] = self.__default[v]

#     def __iter__(self) -> Iterator[str]:
#         yield from self.__default

#     def __len__(self) -> int:
#         return self.__default.__len__()


# class CoreSettings(QTGMCSettings):
#     def __init__(self, tr0: int, tr1: int, tr2: int) -> None:
#         super().__init__(**kwargs)


# class _Interpolater(NamedTuple):
#     deint: Deinterlacer


class _TrueMotionVals(NamedTuple):
    name: str
    truemotion: float
    not_truemotion: float


# _Sections = Literal['core', 'interpolation', 'motion_analysis', 'sharpness', 'source_match']


class QTGMC:
    _pclip: vs.VideoNode
    tff: bool
    _settings: Settings

    # _core: None
    show_info: bool
    deint: Optional[Deinterlacer]
    deint_chroma: Optional[Deinterlacer]
    ref_deint: Optional[vs.VideoNode]

    def __init__(self, clip: vs.VideoNode, preset: Preset = Preset.SLOWER, tff: bool = True, show_info: bool = True) -> None:
        self._pclip = clip
        self.tff = tff
        self._settings = load_preset(preset)
        self.deint = None
        self.deint_chroma = None
        self.ref_deint = None
        self.show_info = show_info
        if show_info:
            add_logger()

    @property
    def core(self) -> MappingProxyType[str, Any]:
        return MappingProxyType(self._settings['core'])

    @property
    def interpolation(self) -> MappingProxyType[str, Any]:
        return MappingProxyType(self._settings['interpolation'])

    @property
    def motion_analysis(self) -> MappingProxyType[str, Any]:
        return MappingProxyType(self._settings['motion_analysis'])

    @property
    def sharpness(self) -> MappingProxyType[str, Any]:
        return MappingProxyType(self._settings['sharpness'])

    @property
    def source_match(self) -> MappingProxyType[str, Any]:
        return MappingProxyType(self._settings['source_match'])

    @property
    def clip(self) -> vs.VideoNode:
        return self._pclip

    def set_core(
        self,
        motion_search: Optional[CoreParam] = None,
        initial_output: Optional[CoreParam] = None,
        final_output: Optional[CoreParam] = None
    ) -> None:
        root = 'core'
        qtgmc_core = self._settings[root]
        if motion_search is not None:
            qtgmc_core['motion_search'] |= motion_search
        if initial_output is not None:
            qtgmc_core['initial_output'] |= initial_output
        if final_output is not None:
            qtgmc_core['final_output'] |= final_output

    def set_interpolation(
        self,
        deint: Optional[Deinterlacer] = None,
        deint_chroma: Optional[Deinterlacer] = None,
        ref: Optional[vs.VideoNode] = None
    ) -> None:
        root = 'interpolation'
        inter = self._settings[root]
        if deint is not None:
            inter['deint'] = class2dict(deint)
            self.deint = deint
        if deint_chroma is not None:
            inter['deint_chroma'] = class2dict(deint_chroma)
            self.deint_chroma = deint_chroma
        if ref is not None:
            inter['ref'] = True
            self.ref_deint = ref

    def set_motion_analysis(self, **kwargs: Any) -> None:
        ma = self._settings['motion_analysis']
        ma.update(kwargs)  # type: ignore

        tmvals = [
            _TrueMotionVals('lambda_', 1000 * ma['blocksize'] ** 2 // 64, 100 * ma['blocksize'] ** 2 // 64),
            _TrueMotionVals('lsad', 1200, 400),
            _TrueMotionVals('pnew', 50, 25),
            _TrueMotionVals('plevel', 1, 0),
        ]
        for v in tmvals:
            if ma[v.name] is None:
                ma[v.name] = v.truemotion if ma['truemotion'] else v.not_truemotion

    def set_sharpness(self, **kwargs: Any) -> None:
        self._settings['sharpness'].update(kwargs)  # type: ignore

    def set_source_match(
        self,
        match: Optional[int] = None,
        lossless: Optional[int] = None,
        basic_deint: Optional[Deinterlacer] = None,
        refined_deint: Optional[Deinterlacer] = None,
        refined_tr: Optional[int] = None,
        enhance: Optional[float] = None
    ) -> None:
        root = 'source_match'
        sm = self._settings[root]
        if match is not None:
            sm['match'] = match
            if match > 0:
                if self._settings['core']['final_output']['tr'] <= 0:
                    self._settings['core']['final_output']['tr'] = 1
        if lossless is not None:
            sm['lossless'] = lossless
        if basic_deint is not None:
            sm['basic_deint'] = class2dict(basic_deint)
        if refined_deint is not None:
            sm['refined_deint'] = class2dict(refined_deint)
        if refined_tr is not None:
            sm['refined_tr'] = refined_tr
        if enhance is not None:
            sm['enhance'] = enhance


def interpolate(clip: vs.VideoNode, tff: bool, deint: Deinterlacer,
                deint_chroma: Optional[Deinterlacer] = None, **kwargs: Any) -> vs.VideoNode:
    field = 3 if tff else 2

    if deint_chroma:
        luma = deint(get_y(clip), field, planes=0, **kwargs)
        chroma = deint_chroma(clip, field, planes=[1, 2], **kwargs)
        return merge_chroma(luma, chroma)

    return deint(clip, field, **kwargs)


def bob_shimmer_fix(clip: vs.VideoNode, ref: vs.VideoNode, rep: int, chroma: bool = True) -> vs.VideoNode:
    # rep range(0, 6)
    # Only support integer
    """
    # Helper function: Compare processed clip with reference clip: only allow thin, horizontal areas of difference, i.e. bob shimmer fixes
    # Rough algorithm: Get difference, deflate vertically by a couple of pixels or so, then inflate again. Thin regions will be removed
    #                  by this process. Restore remaining areas of difference back to as they were in reference clip
    """

    pclip = get_y(clip) if not chroma else clip

    # ed is the erosion distance - how much to deflate then reflate to remove thin areas of interest: 0 = minimum to 6 = maximum
    # od is over-dilation level  - extra inflation to ensure areas to restore back are fully caught:  0 = none to 3 = one full pixel
    erosion = clamp_value(rep, 0, 6)
    # overdilatation = clamp_value(rep, 0, 3)
    # If Rep < 10, then ed = Rep and od = 0, otherwise ed = 10s digit and od = 1s digit 
    # (nasty method, but kept for compatibility with original TGMC)
    overdilatation = 0

    diff = core.std.MakeDiff(ref, pclip)

    coord = dict(coordinates=[0, 1, 0, 0, 0, 0, 1, 0])
    _FuncTuple = Tuple[Callable[..., vs.VideoNode], Callable[..., vs.VideoNode]]

    def _process(_imum_func: _FuncTuple, _flate_func: _FuncTuple) -> vs.VideoNode:
        imum1, imum2 = _imum_func
        flate1, flate2 = _flate_func

        # Areas of positive/negative difference
        choke = imum1(diff, **coord)
        if erosion > 2:
            choke = imum1(choke, **coord)
        if erosion > 5:
            choke = imum1(choke, **coord)
        if erosion % 3 != 0:
            choke = flate1(choke)
        if erosion in {2, 5}:
            choke = core.std.Median(choke)
        choke = imum2(choke, **coord)
        if erosion > 1:
            choke = imum2(choke, **coord)
        if erosion > 4:
            choke = imum2(choke, **coord)

        # Over-dilation - extra reflation up to about 1 pixel
        if overdilatation == 1:
            choke = flate2(choke)
        elif overdilatation == 2:
            choke = flate2(flate2(choke))
        elif overdilatation == 3:
            choke = imum2(choke)
        return choke

    choke1 = _process((core.std.Minimum, core.std.Maximum), (core.std.Deflate, core.std.Inflate))
    choke2 = _process((core.std.Maximum, core.std.Minimum), (core.std.Inflate, core.std.Deflate))

    # Combine above areas to find those areas of difference to restore
    def _scale(x: int) -> int | float:
        return scale_value(x, 8, get_depth(clip), Range.FULL, Range.FULL)
    neutral = 1 << (get_depth(clip) - 1)  # if clip.format.sample_type == vs.INTEGER else 0.5

    restore = core.std.Expr([diff, choke1], f'x {_scale(129)} < x y {neutral} < {neutral} y ? ?')
    restore = core.std.Expr([restore, choke2], f'x {_scale(127)} > x y {neutral} > {neutral} y ? ?')
    mergediff = core.std.MergeDiff(clip, restore)
    return mergediff if chroma else merge_chroma(mergediff, clip)


def extract_noise(clip: vs.VideoNode, interleaved_clip: vs.VideoNode, chroma: bool = False, tff: bool = True) -> vs.VideoNode:
    """
    Given noise extracted from an interlaced source (i.e. the noise is interlaced),
    generate "progressive" noise with a new "field" of noise injected.
    The new noise is centered on a weighted local average and uses the difference
    between local min & max as an estimate of local variance
    """
    planes = [0, 1, 2] if chroma else [0]

    noise = clip.std.SeparateFields(tff)
    noisemax = noise.std.Maximum(planes).std.Maximum(planes, coordinates=[0, 0, 0, 1, 1, 0, 0, 0])
    noisemin = noise.std.Minimum(planes).std.Minimum(planes, coordinates=[0, 0, 0, 1, 1, 0, 0, 0])

    neutral = 1 << (get_depth(clip) - 1)
    randomnoise = interleaved_clip.std.SeparateFields(tff).std.BlankClip(
        color=[neutral] * clip.format.num_planes
    ).grain.Add(1800, 1800)

    diffnoise = core.std.MakeDiff(noisemax, noisemin, planes)

    def _scale(x: int) -> int | float:
        return scale_value(x, 8, get_depth(clip), Range.FULL, Range.FULL)
    varrandom = core.std.Expr([diffnoise, randomnoise], f'x {neutral} - y * {_scale(256)} / {neutral} +')
    newnoise = core.std.MergeDiff(noisemin, varrandom, planes)

    return single_weave(core.std.Interleave([noise, newnoise]), tff)


def single_weave(clip: vs.VideoNode, tff: bool = True) -> vs.VideoNode:
    return clip.std.DoubleWeave(tff)[::2]
