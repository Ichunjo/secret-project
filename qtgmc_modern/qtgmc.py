
from __future__ import annotations

from types import MappingProxyType
from typing import Any, Callable, NamedTuple, Optional, Tuple

import vapoursynth as vs

from .better_vsutil import get_depth, get_neutral, get_y, scale_value_full
from .filters import (Deinterlacer, Denoiser, NoiseDeint, deintd2class,
                      dend2class, noisedeintd2class)
from .helper import clamp_value, merge_chroma
from .logger import add_logger
from .settings import (CoreParam, InputType, NoisePreset, NoiseSettings,
                       Preset, Settings, load_preset)

core = vs.core


class QTGMC:
    _pclip: vs.VideoNode
    _tff: bool
    _input_type: InputType
    _preset: Preset
    _settings: Settings

    log_info: bool
    deint: Optional[Deinterlacer]
    deint_chroma: Optional[Deinterlacer]
    ref_deint: Optional[vs.VideoNode]

    denoiser: Optional[Denoiser]
    noise_deint: Optional[NoiseDeint]

    def __init__(
        self, clip: vs.VideoNode,
        preset: Preset = Preset.SLOWER, tff: bool = True,
        input_type: InputType = InputType.INTERLACED_ONLY,
        log_info: bool = True
    ) -> None:
        self._pclip = clip
        self._tff = tff
        self._input_type = input_type
        self._preset = preset
        self._settings = load_preset(preset)

        self.deint = None
        self.deint_chroma = None
        self.ref_deint = None
        self.denoiser = None
        self.noise_deint = None

        self.log_info = log_info
        if log_info:
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
    def noise(self) -> Optional[MappingProxyType[str, Any]]:
        if (noise := self._settings['noise']) is None:
            return None
        return MappingProxyType(noise)

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

        # Clamping core values
        qtgmc_core['motion_search']['tr'] = clamp_value(qtgmc_core['motion_search']['tr'], 1, 2)
        qtgmc_core['initial_output']['tr'] = clamp_value(qtgmc_core['initial_output']['tr'], 1, 2)
        qtgmc_core['final_output']['tr'] = clamp_value(qtgmc_core['final_output']['tr'], 0, 3)
        qtgmc_core['motion_search']['rep'] = clamp_value(qtgmc_core['motion_search']['rep'], 0, None)

        # Core defaults
        if self._settings['source_match']['match'] > 0:
            if self._settings['core']['final_output']['tr'] <= 0:
                # TR2 defaults always at least 1 when using source-match
                self._settings['core']['final_output']['tr'] = 1

    def set_interpolation(
        self,
        deint: Optional[Deinterlacer] = None,
        deint_chroma: Optional[Deinterlacer] = None,
        ref: Optional[vs.VideoNode] = None
    ) -> None:
        root = 'interpolation'
        inter = self._settings[root]
        if deint is not None:
            inter['deint'] = deint.to_dict()
            self.deint = deint
        if deint_chroma is not None:
            inter['deint_chroma'] = deint_chroma.to_dict()
            self.deint_chroma = deint_chroma
        if ref is not None:
            inter['ref'] = True
            self.ref_deint = ref

    def set_motion_analysis(self, **kwargs: Any) -> None:
        ma = self._settings['motion_analysis']
        ma.update(kwargs)  # type: ignore

        # Defaults values

        class _TrueMotionVals(NamedTuple):
            name: str
            truemotion: float
            not_truemotion: float

        tmvals = [
            _TrueMotionVals('lambda_', 1000 * ma['blocksize'] ** 2 // 64, 100 * ma['blocksize'] ** 2 // 64),
            _TrueMotionVals('lsad', 1200, 400),
            _TrueMotionVals('pnew', 50, 25),
            _TrueMotionVals('plevel', 1, 0),
        ]
        for v in tmvals:
            if ma[v.name] is None:
                ma[v.name] = v.truemotion if ma['truemotion'] else v.not_truemotion

        # Clamping motion anal values
        ma['searchpre'] = clamp_value(ma['searchpre'], 0, 3)
        ma['subpel'] = clamp_value(ma['subpel'], 1, 4)
        ma['subpel_inter'] = clamp_value(ma['subpel_inter'], 0, 2)
        ma['blocksize'] = clamp_value(ma['blocksize'], 4, 32)
        ma['overlap'] = clamp_value(ma['overlap'], 2, 16)
        ma['search'] = clamp_value(ma['search'], 0, 7)
        ma['search_param'] = clamp_value(ma['search_param'], 0, 7)
        ma['pelsearch'] = clamp_value(ma['pelsearch'], 1, 4)
        ma['lambda_'] = clamp_value(ma['lambda_'], 0, None)
        ma['plevel'] = clamp_value(ma['plevel'], 0, 2)
        ma['dct'] = clamp_value(ma['dct'], 0, 10)
        ma['prog_sad_mask'] = clamp_value(ma['prog_sad_mask'], 0., None)


    def set_sharpness(self, **kwargs: Any) -> None:
        sharp = self._settings['sharpness']
        sharp.update(kwargs)  # type: ignore

        # Sharpness defaults
        if sharp['mode'] <= 0:
            sharp['strength'] = 0.0
        if self._settings['source_match']['match'] > 1:
            # Default sharpness is 1.0, or 0.2 if using source-match
            sharp['strength'] *= 0.2

        # Clamping values
        sharp['strength'] = clamp_value(sharp['strength'], 0., None)
        sharp['mode'] = clamp_value(sharp['mode'], 0, 2)
        sharp['lmode'] = clamp_value(sharp['lmode'], 0, 4)
        sharp['lrad'] = clamp_value(sharp['lrad'], 0, None)
        sharp['ovs'] = clamp_value(sharp['ovs'], 0, 255)
        sharp['vthin'] = clamp_value(sharp['vthin'], 0., None)
        sharp['bb'] = clamp_value(sharp['bb'], 0, 3)

        # spatial_l = sharp['lmode'] in {1, 3}
        # temporal_l = sharp['lmode'] in {2, 4}
        # mul = 2 if temporal_l else 1.5 if spatial_l else 1

        # ovs = scale_value_full(sharp['ovs'], 8, peak)

        # strength_adj = (
        #     sharp['strength'] * (
        #         mul * (
        #             0.2
        #             + self._settings['core']['initial_output']['tr'] * 0.15
        #             + self._settings['core']['final_output']['tr'] * 0.25
        #         ) + (0.1 if sharp['mode'] == 1 else 0)
        #     )
        # )

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
        if lossless is not None:
            sm['lossless'] = lossless
        if basic_deint is not None:
            sm['basic_deint'] = basic_deint.to_dict()
        if refined_deint is not None:
            sm['refined_deint'] = refined_deint.to_dict()
        if refined_tr is not None:
            sm['refined_tr'] = refined_tr
        if enhance is not None:
            sm['enhance'] = enhance

        # Clamping values
        sm['match'] = clamp_value(sm['match'], 0, 3)
        sm['lossless'] = clamp_value(sm['lossless'], 0, 2)
        sm['refined_tr'] = clamp_value(sm['refined_tr'], 0, 2)
        sm['enhance'] = clamp_value(sm['enhance'], 0., None)

    def set_noise(
        self,
        preset: NoisePreset = NoisePreset.FAST,
        mode: Optional[int] = None,
        denoiser: Optional[Denoiser] = None,
        use_mc: Optional[bool] = None,
        tr: Optional[int] = None,
        strength: Optional[float] = None,
        chroma: Optional[bool] = None,
        restore_before_final: Optional[float] = None,
        restore_after_final: Optional[float] = None,
        deint: Optional[NoiseDeint] = None,
        stabilise: Optional[bool] = None
    ) -> None:
        noise = self._settings['noise']
        if not noise:
            noise = NoiseSettings(
                mode=0, strength=2.0, chroma=False,
                restore_before_final=0.3 if self._preset.i <= 1 else 0.,
                restore_after_final=0.1 if self._preset.i <= 1 else 0.,
                **NoisePreset.FAST
            )
            self.denoiser = None
            self.noise_deint = None
        if preset is not None:
            noise.update(preset)  # type: ignore
        if mode is not None:
            noise['mode'] = mode
        if denoiser is not None:
            self.denoiser = denoiser
            noise['denoiser'] = denoiser.to_dict()
        if use_mc is not None:
            noise['use_mc'] = use_mc
        if tr is not None:
            noise['tr'] = tr
        if strength is not None:
            noise['strength'] = strength
        if chroma is not None:
            noise['chroma'] = chroma
        if restore_before_final is not None:
            noise['restore_before_final'] = restore_before_final
        if restore_after_final is not None:
            noise['restore_after_final'] = restore_after_final
        if deint is not None:
            self.noise_deint = deint
            noise['deint'] = deint.to_dict()
        if stabilise is not None:
            noise['stabilise'] = stabilise

        # Clamping values
        noise['mode'] = clamp_value(noise['mode'], 0, 2)
        noise['tr'] = clamp_value(noise['tr'], 0, 2)
        noise['strength'] = clamp_value(noise['strength'], 0., None)
        noise['restore_before_final'] = clamp_value(noise['restore_before_final'], 0., 1.0)
        noise['restore_after_final'] = clamp_value(noise['restore_after_final'], 0., 1.0)

        # Add default settings

    def process(self) -> None:
        sttg = self._settings
        ...

    def _pre_processing(self) -> None:
        ...

    def _processing(self) -> None:
        ...

    def _noise_processing(self) -> None:
        ...

    def _interpolation_processing(self) -> None:
        ...

    def _basic_output_processing(self) -> None:
        ...

    def _restore_processing(self) -> None:
        ...

    def _post_processing(self) -> None:
        ...



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
    Helper function: Compare processed clip with reference clip: only allow thin,
    horizontal areas of difference, i.e. bob shimmer fixes

    Rough algorithm: Get difference, deflate vertically by a couple of pixels or so, then inflate again.
    Thin regions will be removed by this process.
    Restore remaining areas of difference back to as they were in reference clip
    """

    pclip = get_y(clip) if not chroma else clip

    # ed is the erosion distance - how much to deflate then reflate to remove thin areas of interest:
    # 0 = minimum to 6 = maximum
    # od is over-dilation level  - extra inflation to ensure areas to restore back are fully caught:
    # 0 = none to 3 = one full pixel
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
        return scale_value_full(x, 8, get_depth(clip))
    neutral = get_neutral(clip)

    restore = core.std.Expr([diff, choke1], f'x {_scale(129)} < x y {neutral} < {neutral} y ? ?')
    restore = core.std.Expr([restore, choke2], f'x {_scale(127)} > x y {neutral} > {neutral} y ? ?')
    mergediff = core.std.MergeDiff(clip, restore)
    return mergediff if chroma else merge_chroma(mergediff, clip)


def make_lossless(clip: vs.VideoNode, src: vs.VideoNode, input_type: InputType, tff: bool = True) -> vs.VideoNode:
    """
    Insert the source lines into the result to create a true lossless output.
    However, the other lines in the result have had considerable processing
    and won't exactly match source lines.
    There will be some slight residual combing.
    Use vertical medians to clean a little of this away
    """

    # Weave the source fields and the "new" fields that have generated in the input
    if input_type == InputType.INTERLACED_ONLY:
        src_fields = src.std.SeparateFields(tff)
    elif input_type == InputType.PROGRESSIVE_GENERIC:
        raise ValueError('Lossless modes are incompatible with InputType=1')
    else:
        src_fields = src.std.SeparateFields(tff).std.SelectEvery(4, [0, 3])
    new_fields = clip.std.SeparateFields(tff).std.SelectEvery(4, [1, 2])
    processed = single_weave(
        core.std.Interleave([src_fields, new_fields]).std.SelectEvery(4, [0, 1, 3, 2]), tff
    )

    # Clean some of the artefacts caused by the above - creating a second version of the "new" fields
    vert_median = core.rgvs.VerticalCleaner(processed, 1)
    vert_med_diff = core.std.MakeDiff(processed, vert_median)
    vm_new_diff1 = vert_med_diff.std.SeparateFields(tff).std.SelectEvery(4, [1, 2])
    neutral = get_neutral(clip)
    vm_new_diff2 = core.std.Expr(
        [vm_new_diff1.rgvs.VerticalCleaner(1), vm_new_diff1],
        f'x {neutral} - y {neutral} - * 0 < {neutral} x {neutral} - abs y {neutral} - abs < x y ? ?'
    )
    vm_new_diff3 = core.rgvs.Repair(
        vm_new_diff2, vm_new_diff2.rgvs.RemoveGrain(2), 1
    )
    # Reweave final result
    return single_weave(
        core.std.Interleave(
            [src_fields, new_fields.std.MakeDiff(vm_new_diff3)]
        ).std.SelectEvery(4, [0, 1, 3, 2]), tff
    )


def apply_source_match():
    ...


def single_weave(clip: vs.VideoNode, tff: bool = True) -> vs.VideoNode:
    return clip.std.DoubleWeave(tff)[::2]
