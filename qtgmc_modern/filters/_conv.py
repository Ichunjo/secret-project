

__all__ = [
    'deintd2class',
    'dend2class',
    'noisedeintd2class'
]

from typing import Dict, Type

from ..settings import VSCallableD
from ._deinterlacers import (EEDI2, EEDI3, NNEDI3, NNEDI3CL, ZNEDI3, Bob,
                             BWDiF, Deinterlacer, EEDI3m, EEDI3mCL, NoiseBob,
                             NoiseDeint, NoiseDWeave, NoiseGenerate, SangNom2)
from ._denoisers import (FFT3D, Denoiser, DFTTest, KNLMeansCL, NeoDFTTest,
                         NeoFFT3D)

DEINTERLACERS: Dict[str, Type[Deinterlacer]] = dict(
    nnedi3=NNEDI3,
    nnedi3cl=NNEDI3CL,
    znedi3=ZNEDI3,
    eedi2=EEDI2,
    eedi3=EEDI3,
    eedi3m=EEDI3m,
    eedi3mcl=EEDI3mCL,
    sangnom2=SangNom2,
    bwdif=BWDiF,
    bob=Bob,

    NNEDI3=NNEDI3,
    NNEDI3CL=NNEDI3CL,
    ZNEDI3=ZNEDI3,
    EEDI2=EEDI2,
    EEDI3=EEDI3,
    EEDI3m=EEDI3m,
    EEDI3mCL=EEDI3mCL,
    SangNom2=SangNom2,
    BWDiF=BWDiF,
    Bob=Bob
)

NOISE_DEINTERLACERS: Dict[str, Type[NoiseDeint]] = dict(
    doubleweave=NoiseDWeave,
    bob=NoiseBob,
    generate=NoiseGenerate
)

DENOISERS: Dict[str, Type[Denoiser]] = dict(
    fft3d=FFT3D,
    dfttest=DFTTest,
    knlmeanscl=KNLMeansCL,
    neodfttest=NeoDFTTest,
    neofft3d=NeoFFT3D,

    FFT3D=FFT3D,
    DFTTest=DFTTest,
    KNLMeansCL=KNLMeansCL,
    NeoDFTTest=NeoDFTTest,
    NeoFFT3D=NeoFFT3D
)


def deintd2class(dico: VSCallableD) -> Deinterlacer:
    if (kwargs := dico['args']) is None:
        kwargs = {}

    try:
        clss = DEINTERLACERS[dico['name']]
    except KeyError as key_err:
        raise ValueError from key_err

    return clss(**kwargs)


def noisedeintd2class(dico: VSCallableD) -> NoiseDeint:
    if (kwargs := dico['args']) is None:
        kwargs = {}

    try:
        clss = NOISE_DEINTERLACERS[dico['name']]
    except KeyError as key_err:
        raise ValueError from key_err

    return clss(**kwargs)


def dend2class(dico: VSCallableD) -> Denoiser:
    if (kwargs := dico['args']) is None:
        kwargs = {}

    try:
        clss = DENOISERS[dico['name']]
    except KeyError as key_err:
        raise ValueError from key_err

    return clss(**kwargs)
