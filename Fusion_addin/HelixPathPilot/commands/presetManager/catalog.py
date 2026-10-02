"""Read packaged presets without depending on Fusion."""

from ...i18n import tr

from pathlib import Path

from ...core.presets import HelixPreset, MAX_JSON_BYTES, PRESET_EXTENSION


def builtin_presets(folder=None):
    folder = Path(folder) if folder is not None else Path(__file__).resolve().parents[2] / 'presets/builtin'
    presets, errors = [], []
    try:
        paths = sorted(folder.glob('*' + PRESET_EXTENSION))
    except OSError as error:
        return [], [str(error)]
    for path in paths:
        try:
            with path.open('rb') as stream:
                data = stream.read(MAX_JSON_BYTES + 1)
            if len(data) > MAX_JSON_BYTES:
                raise ValueError(tr('File exceeds 128 KiB.'))
            presets.append(HelixPreset.from_json(data.decode('utf-8-sig')))
        except (OSError, UnicodeError, ValueError) as error:
            errors.append(f'{path.name}: {error}')
    return presets, errors


# Match only packaged names, at the display boundary. Portable JSON and user
# names retain their original spelling even if they match one of these names.
_BUILTIN_NAMES = {
    'Basishelix 20 × 50 mm': 'Basic helix 20 × 50 mm',
    'Surface 5 → 10 mm': 'Surface 5 → 10 mm',
    'Zwei variable Abschnitte': 'Two variable sections',
}


def preset_display_name(preset, *, builtin=False):
    if builtin:
        return tr(_BUILTIN_NAMES.get(preset.name, preset.name))
    return preset.name
