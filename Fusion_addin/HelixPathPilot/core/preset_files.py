"""Portable JSON file exchange, independent of the Fusion file dialog."""

import os
from pathlib import Path
import tempfile

from .presets import HelixPreset, MAX_JSON_BYTES, PRESET_EXTENSION


def read_preset_file(filename):
    with Path(filename).open('rb') as stream:
        data = stream.read(MAX_JSON_BYTES + 1)
    if len(data) > MAX_JSON_BYTES:
        raise ValueError('Vorlagendatei überschreitet 128 KiB.')
    return HelixPreset.from_json(data.decode('utf-8-sig'))


def export_path(filename):
    path = Path(filename)
    if not path.name.lower().endswith(PRESET_EXTENSION):
        path = path.with_name(path.name + PRESET_EXTENSION)
    return path


def write_preset_file(filename, preset, overwrite=False):
    path = export_path(filename)
    data = preset.to_json().encode('utf-8')
    if len(data) > MAX_JSON_BYTES:
        raise ValueError('Vorlagendatei überschreitet 128 KiB.')
    if not overwrite:
        # Exclusive creation protects files that appeared after the save dialog.
        stream = path.open('xb')
        try:
            with stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        except Exception:
            path.unlink(missing_ok=True)
            raise
    else:
        # Complete the write before replacing a previously existing file.
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.helixpilot-',
                                             suffix='.tmp', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    return path
