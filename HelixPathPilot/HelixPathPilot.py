"""Fusion entry points, based on the supplied Autodesk add-in template."""

from . import commands
from .lib import fusionAddInUtils as futil
from .version import get_full_version_label


def run(context):
    try:
        commands.start()
        futil.log(f'{get_full_version_label()} started')
    except Exception:
        futil.handle_error('run', show_message_box=True)


def stop(context):
    try:
        commands.stop()
        futil.log(f'{get_full_version_label()} stopped')
    except Exception:
        futil.handle_error('stop', show_message_box=True)
    finally:
        futil.clear_handlers()
