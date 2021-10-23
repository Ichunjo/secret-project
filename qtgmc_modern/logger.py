from __future__ import annotations

from typing import Any, Sequence

from vapoursynth import MESSAGE_TYPE_INFORMATION, MessageType, core


def add_logger() -> None:
    def _log(msgtype: MessageType, msg: str) -> None:
        if msgtype == MESSAGE_TYPE_INFORMATION and msg.startswith('QTGMC-Modern'):
            print(msg)
    core.add_log_handler(_log)
    # globals()['QTGMC-Modern_USE_LOGGER'] = True


def log_update(root: str | Sequence[str], val: Any) -> None:
    # if not globals()['QTGMC-Modern_USE_LOGGER']:
    #     return
    root = '.'.join(root) if isinstance(root, Sequence) else root
    core.log_message(
        MESSAGE_TYPE_INFORMATION,
        f'QTGMC-Modern: "{root}" updated to "{str(val)}"'
    )
