
"""
Implements the interface in static typing and at runtime plus some enumerations.
"""

__all__ = [
    'CoreParam', 'CoreSettings',
    'VSCallableD',
    'InterpolationSettings',
    'MotionAnalysisSettings',
    'SharpnessSettings',
    'SourceMatchSettings',
    'NoiseSettings',

    'Settings',

    'SearchPre', 'SubPel', 'SubPelInter', 'Search', 'PLevel',
    'InputType'
]

from enum import IntEnum
from typing import TYPE_CHECKING, Any, Dict, Optional, TypedDict

from ._abstract import LoggedSettings

if TYPE_CHECKING:
    # Features / Settings dicts
    class VSCallableD(TypedDict):
        """
        VapourSynth Callable Deinterlacer.\n
        Must map a Deinterlacer.
        """
        name: str
        """
        Deinterlacer name. Must map a name in /filers/_conv/DEINTERLACERS
        """
        args: Optional[Dict[str, Any]]
        """
        Additional keywords arguments
        """


    class CoreParam(TypedDict):
        """
        Couple of Temporal Radius and Repair values
        """
        tr: int
        """
        Temporal binomial/linear smoothing radius used.
        """
        rep: int
        """
        Repair value (0=off)
        """


    class CoreSettings(TypedDict):
        """
        Main core settings for motion analysis
        """
        motion_search: CoreParam
        """
        Made of a temporal binomial smoothing radius used to create motion search clip
        and a repair motion search value.\n
        Old "TR0" and "Rep0".
        """
        initial_output: CoreParam
        """
        Made of a temporal binomial smoothing radius used on interpolated clip
        for inital output and a repair initial output value.\n
        Old "TR1" and "Rep1".
        """
        final_output: CoreParam
        """
        Made of a temporal linear smoothing radius used
        for final stablization / denoising and a repair final output value.\n
        Old "TR2" and "Rep2".
        """


    class InterpolationSettings(TypedDict):
        """
        Interpolation settings
        """
        deint: VSCallableD
        """
        Main deinterlacer.\n
        Supported string names are in /filers/_conv/DEINTERLACERS are supported.
        Old "EdiMode" ("NNSize", "NNeurons", "EdiQual", "EdiMaxD", "EdiThreads").
        """
        deint_chroma: Optional[VSCallableD]
        """
        Optional deinterlacer for chroma planes.\n
        Supported string names are in /filers/_conv/DEINTERLACERS are supported.
        Old "ChromaEdi".
        """
        ref: Optional[bool]
        """
        Boolean used to check if a reference clip has been passed to the main class QTGMC.
        Old "EdiExt", kinda.
        """


    class MotionAnalysisSettings(TypedDict):
        """
        Motion analysis settings used in mvtools
        """
        searchpre: int
        """
        Pre-filtering for motion search clip. See `SearchPre`.
        Old "SrchClipPP".
        """
        subpel: int
        """
        Sub-pixel accuracy for motion analysis. See `SubPel`.
        Old "SubPel".
        """
        subpel_inter: int
        """
        Interpolation used for sub-pixel motion analysis. See `SubPelInter`
        Old "SubPelInterp".
        """
        blocksize: int
        """
        Size of blocks that are matched during motion analysis.
        Old "Blocksize".
        """
        overlap: int
        """
        How much to overlap motion analysis blocks
        (requires more blocks, but essential to smooth block edges in motion compenstion)
        Old "Overlap".
        """
        search: int
        """
        Search method used for matching motion blocks - see MVTools2 documentation for available algorithms.
        See `Search`.
        Old "Search".
        """
        search_param: int
        """
        Parameter for search method chosen. See `Search`.
        Old "SearchParam".
        """
        pelsearch: int
        """
        Search parameter (as above) for the finest sub-pixel level. See `SubPel`.
        Old "PelSearch".
        """
        chroma_motion: bool
        """
        Whether to consider chroma when analyzing motion.
        Setting to false gives good speed-up, but may very occasionally make incorrect motion decision.
        Old "ChromaMotion".
        """
        truemotion: bool
        """
        Whether to use the 'truemotion' defaults from MAnalyse
        Old "TrueMotion".
        """
        lambda_: Optional[int]
        """
        Motion vector field coherence - how much the motion analysis favors similar motion vectors
        for neighboring blocks. Should be scaled by blocksize * blocksize / 64.
        Old "Lambda".
        """
        lsad: Optional[int]
        """
        How much to reduce need for vector coherence (i.e. lambda_ above) if prediction of motion vector
        from neighbors is poor, typically in areas of complex motion.
        This value is scaled in MVTools (unlike lambda_).
        Old "LSAD".
        """
        pnew: Optional[int]
        """
        Penalty for choosing a new motion vector for a block over an existing one -
        avoids chosing new vectors for minor gain.
        Old "PNew".
        """
        plevel: Optional[int]
        """
        Mode for scaling lambda across different sub-pixel levels - see MVTools2 documentation for choices.
        See `PLevel`.
        Old "PLevel".
        """
        globalmotion: bool
        """
        Whether to estimate camera motion to assist in selecting block motion vectors.
        Old "GlobalMotion".
        """
        dct: int
        """
        Modes to use DCT (frequency analysis) or SATD as part of the block matching process -
        see MVTools2 documentation for choices.
        Old "DCT".
        """
        thsad_initial_output: int
        """
        SAD threshold for block match on shimmer-removing temporal smooth (initial_output tr).
        Increase to reduce bob-shimmer more (may smear/blur).
        Old "ThSAD1".
        """
        thsad_final_output: int
        """
        SAD threshold for block match on final denoising temporal smooth (final_output tr).
        Increase to strengthen final smooth (may smear/blur).
        Old "ThSAD2".
        """
        thscd1: int
        """
        Scene change detection parameter 1 - see MVTools documentation.
        Old "ThSCD1".
        """
        thscd2: int
        """
        Scene change detection parameter 2 - see MVTools documentation.
        Old "ThSCD2".
        """
        prog_sad_mask: float
        """
        Only applies to InputType=2 or 3.
        If prog_sad_mask > 0.0 then blend InputType modes 1 and 2/3 based on block motion SAD.
        Higher values help recover more detail, but repair less artefacts.
        Reasonable range about 2.0 to 20.0, or 0.0 for no blending.
        Old "ProgSADMask".
        """


    class SharpnessSettings(TypedDict):
        """"""
        strength: float
        """
        How much to resharpen the temporally blurred clip.
        Old "Sharpness".
        """
        mode: int
        """
        Resharpening mode. See `SharpnessMode`.
        Old "SMode".
        """
        lmode: int
        """
        Sharpness limiting. See `SharpnessLimitMode`.
        Old "SLMode".
        """
        lrad: int
        """
        Temporal or spatial radius used with sharpness limiting (depends on SLMode).
        Temporal radius can only be 0, 1 or 3
        Old "SLRad".
        """
        ovs: int
        """
        Amount of overshoot allowed with temporal sharpness limiting (SLMode = 2,4),
        i.e. allow some oversharpening
        Old "SOvs".
        """
        vthin: float
        """
        How much to thin down 1-pixel wide lines that have been widened due to interpolation
        into neighboring field lines
        Old "SVThin".
        """
        bb: int
        """
        Back blend (blurred) difference between pre & post sharpened clip (minor fidelity improvement).
        See `SharpnessBackBlend`.
        Old "Sbb".
        """


    class SourceMatchSettings(TypedDict):
        match: int
        """
        Match mode, see `MatchMode`.
        Old "SourceMatch".
        """
        lossless: int
        """
        Adds some extra detail but:
        mode 1 gets shimmer / minor combing,
        mode 2 is more stable/tweakable but not exactly lossless.
        Old "Lossless".
        """
        basic_deint: VSCallableD
        """
        Override default interpolation method for basic source-match.
        Old "MatchEdi", kinda.
        """
        refined_deint: VSCallableD
        """
        Override interpolation method for refined source-match.
        Can be a good idea to pick MatchEdi2="Bob" for speed.
        Old "MatchEdi2", kinda.
        """
        refined_tr: int
        """
        Temporal radius for refined source-matching.
        Basic source-match doesn't need this setting as its temporal radius must match initial_output tr
        2=smoothness, 1=speed/sharper, 0=not recommended. Differences are very marginal.
        Old "MatchTR2".
        """
        enhance: float
        """
        Enhance the detail found by source-match modes 2 & 3.
        A slight cheat - will enhance noise if set too strong.
        Best set < 1.0.
        Old "MatchEnhance".
        """


    class NoiseSettings(TypedDict):
        """"""
        mode: int
        """
        Bypass mode:
        0 = disable,
        1 = denoise source & optionally restore some noise back at end of script [use for stronger denoising],
        2 = identify noise only & optionally restore some after QTGMC smoothing [for grain retention / light denoising]
        Old "NoiseProcess".
        """
        denoiser: VSCallableD
        """
        Select denoiser to use for noise bypass / denoising.
        Old "Denoiser".
        """
        use_mc: bool
        """
        Whether to provide a motion-compensated clip to the denoiser
        for better noise vs detail detection (will be a little slower).
        Old "DenoiseMC".
        """
        tr: int
        """
        Temporal radius used when analyzing clip for noise extraction.
        Higher values better identify noise vs detail but are slower.
        Old "NoiseTR".
        """
        strength: float
        """
        Amount of noise known to be in the source, sensible values vary by source and denoiser, so experiment.
        Old "Sigma".
        """
        chroma: bool
        """
        Whether to process chroma noise or not
        Old "ChromaNoise"
        """
        restore_before_final: float
        """
        How much removed noise/grain to restore before final temporal smooth.
        Retain "stable" grain and some detail (effect depends on final_output tr).
        Old "GrainRestore".
        """
        restore_after_final: float
        """
        How much removed noise/grain to restore after final temporal smooth.
        Retains any kind of noise.
        Old "NoiseRestore".
        """
        deint: VSCallableD
        """
        When noise is taken from interlaced source, how to 'deinterlace' it before restoring.
        Old "NoiseDeint".
        """
        stabilise: bool
        """
        Use motion compensation to limit shimmering and strengthen detail within the restored noise.
        Old "StabilizeNoise".
        """


    class Settings(TypedDict):
        core: CoreSettings
        motion_analysis: MotionAnalysisSettings
        interpolation: InterpolationSettings
        sharpness: SharpnessSettings
        source_match: SourceMatchSettings

        noise: Optional[NoiseSettings]
        # progressive
        # shutter speed motion blur framerate

else:
    class VSCallableD(LoggedSettings):
        ...


    class CoreParam(LoggedSettings):
        ...


    class CoreSettings(LoggedSettings):
        ...


    class InterpolationSettings(LoggedSettings):
        ...


    class MotionAnalysisSettings(LoggedSettings):
        ...


    class SharpnessSettings(LoggedSettings):
        ...


    class SourceMatchSettings(LoggedSettings):
        ...


    class NoiseSettings(LoggedSettings):
        ...


    class Settings(LoggedSettings):
        ...


# print(globals())

# class PresetSettings(TypedDict):
#     PLACEBO: Settings
#     VERY_SLOW: Settings
#     SLOWER: Settings
#     SLOW: Settings
#     MEDIUM: Settings
#     FAST: Settings
#     FASTER: Settings
#     VERY_FAST: Settings
#     SUPER_FAST: Settings
#     ULTRA_FAST: Settings
#     DRAFT: Settings


# Enums
# Motion Anal
class SearchPre(IntEnum):
    """Pre-filtering for motion search clip mode"""
    NONE = 0
    SIMPLE_BLUR = 1
    GAUSSIAN = 2
    GAUSSIAN_EDGE_SOFTEN = 3


class SubPel(IntEnum):
    """Sub-pixel accuracy for motion analysis"""
    ONE = 1
    HALF = 2
    QUARTER = 4


class SubPelInter(IntEnum):
    """Interpolation used for sub-pixel motion analysis"""
    BILINEAR = 0
    BICUBIC = 1
    WEINER = 2


class Search(IntEnum):
    ONETIME = 0
    NSTEP = 1
    LOGARITHMIC = 2
    EXHAUSTIVE = 3
    HEXAGON = 4
    UNEVEN_MULTI_HEXAGON = 5
    HORIZONTAL_EXHAUSTIVE = 6
    VERTICAL_EXHAUSTIVE = 7


class PLevel(IntEnum):
    """Penality factor lambda level scaling mode"""
    NO_SCALING = 0
    LINEAR = 1
    QUADRATIC = 2
    """Quadratic dependence from hierarchical level size"""


# Sharpness
class SharpnessMode(IntEnum):
    """0 = none, 1 = difference from 3x3 blur kernel, 2 = vertical max/min average + 3x3 kernel"""
    NONE = 0
    DIFF_3X3 = 1
    VERT_MAXMIN_AVG_3X3 = 2


class SharpnessLimitMode(IntEnum):
    """
    0 = off,
    [1 = spatial, 2 = temporal] : before final temporal smooth,
    [3 = spatial, 4 = temporal] : after final temporal smooth
    """
    OFF = 0
    BEFORE_FINAL_TEMP_SMOOTH_SPATIAL = 1
    BEFORE_FINAL_TEMP_SMOOTH_TEMPORAL = 2
    AFTER_FINAL_TEMP_SMOOTH_SPATIAL = 3
    AFTER_FINAL_TEMP_SMOOTH_TEMPORAL = 4


class SharpnessBackBlend(IntEnum):
    """0 = Off, 1 = before (1st) sharpness limiting, 2 = after (1st) sharpness limiting, 3 = both"""
    OFF = 0
    BEFORE_LIMIT = 1
    AFTER_LIMIT = 2
    BOTH = 3


# SourceMatch
class MatchMode(IntEnum):
    """0 = Source-matching off (standard algorithm), 1 = basic source-match, 2 = refined match, 3 = twice refined match"""
    OFF = 0
    BASIC = 1
    REFINED = 2
    TWICE_REFINED = 3


class LosslessMode(IntEnum):
    """
    Adds some extra detail but:
    mode 1 gets shimmer / minor combing,
    mode 2 is more stable/tweakable but not exactly lossless.
    """
    OFF = 0
    AFTER_FINAL_TEMPORAL_SMOOTH = 1
    BEFORE_RESHARPENING = 2


# InputType
class InputType(IntEnum):
    INTERLACED_ONLY = 0
    PROGRESSIVE_GENERIC = 1
    PROGRESSIVE_VERYBAD = 2
    PROGRESSIVE_VERYBAD_INV_FIELD = 3
