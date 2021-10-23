from typing import TYPE_CHECKING, List, Type

import yaml
from pkg_resources import resource_filename

from ._abstract import LoggedSettings
from ._interface import (CoreParam, CoreSettings, DeinterlacerD,
                         InterpolationSettings, MotionAnalysisSettings,
                         NoiseSettings, Settings, SharpnessSettings,
                         SourceMatchSettings)
from ._presets import Preset


def load_preset(p: Preset) -> Settings:
    try:
        with open('D:/Documents/secret-project/qtgmc_modern/presets/' + p.name + '.yml', 'r', encoding='utf-8') as f:
        # with open(resource_filename('qtgmc_modern', p.value + '.yml'), 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.CLoader)
    except FileNotFoundError as file_err:
        raise ValueError from file_err

    if not TYPE_CHECKING:
        keys: List[str] = [
            'core',
            'interpolation',
            'motion_analysis',
            'sharpness',
            'source_match'
        ]
        classes: List[Type[LoggedSettings]] = [
            CoreSettings,
            InterpolationSettings,
            MotionAnalysisSettings,
            SharpnessSettings,
            SourceMatchSettings
        ]
        for key, classe in zip(keys, classes):
            config[key] = classe(**config[key])
        config['core']['motion_search'] = CoreParam(**config['core']['motion_search'])
        config['core']['initial_output'] = CoreParam(**config['core']['initial_output'])
        config['core']['final_output'] = CoreParam(**config['core']['final_output'])

    return config


# class _Settings(LoggedSettings):
#     ...


# def _convert_dict(d: Dict[str, Any]) -> _Settings:
#     for k, v in d.items():
#         if isinstance(v, dict):
#             rv = _convert_dict(v)
#             d[k] = rv
#     return _Settings(d)
