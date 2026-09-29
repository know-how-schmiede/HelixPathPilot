"""User presets stored outside the add-in installation; no Fusion dependency."""

from dataclasses import replace
import hashlib
import os
from pathlib import Path
import re
import sys
import unicodedata

from .presets import HelixPreset, MAX_JSON_BYTES, PRESET_EXTENSION


def user_preset_folder():
    if sys.platform == 'win32':
        base = Path(os.environ.get('APPDATA') or Path.home() / 'AppData/Roaming')
    elif sys.platform == 'darwin':
        base = Path.home() / 'Library/Application Support'
    else:
        base = Path(os.environ.get('XDG_DATA_HOME') or Path.home() / '.local/share')
    return base / 'HelixPathPilot/presets'


class PresetStore:
    def __init__(self, folder=None):
        self.folder = Path(folder) if folder is not None else user_preset_folder()

    def _path(self, key):
        if not isinstance(key, str) or not re.fullmatch(r'[0-9a-f]{64}', key):
            raise ValueError('Ungültige Vorlagenkennung.')
        path = self.folder / (key + PRESET_EXTENSION)
        if path.is_symlink():
            raise ValueError('Verknüpfte Vorlagendateien werden nicht unterstützt.')
        return path

    def load(self, key):
        with self._path(key).open('rb') as stream:
            data = stream.read(MAX_JSON_BYTES + 1)
        if len(data) > MAX_JSON_BYTES:
            raise ValueError('Vorlage überschreitet 128 KiB.')
        return HelixPreset.from_json(data.decode('utf-8-sig'))

    def list(self):
        entries, errors = [], []
        try:
            paths = sorted(self.folder.glob('*' + PRESET_EXTENSION))
        except OSError as error:
            return [], [str(error)]
        for path in paths:
            key = path.name[:-len(PRESET_EXTENSION)]
            try:
                entries.append((key, self.load(key)))
            except (OSError, UnicodeError, ValueError) as error:
                errors.append(f'{path.name}: {error}')
        entries.sort(key=lambda entry: entry[1].name.casefold())
        return entries, errors

    def save(self, preset):
        # A display name never becomes a path. Canonical names prevent duplicates.
        preset = replace(preset, name=unicodedata.normalize('NFC', preset.name.strip()))
        content = preset.to_json().encode('utf-8')
        if len(content) > MAX_JSON_BYTES:
            raise ValueError('Vorlage überschreitet 128 KiB.')
        key = hashlib.sha256(preset.name.casefold().encode('utf-8')).hexdigest()
        self.folder.mkdir(parents=True, exist_ok=True)
        path = self._path(key)
        try:
            stream = path.open('xb')
        except FileExistsError as error:
            raise ValueError('Eine eigene Vorlage mit diesem Namen existiert bereits. '
                             'Bitte einen anderen Namen wählen.') from error
        try:
            with stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        except Exception:
            path.unlink(missing_ok=True)
            raise
        return key

    def delete(self, key):
        self._path(key).unlink()
