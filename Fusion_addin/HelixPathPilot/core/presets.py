"""Versioned portable preset data. Lengths are cm, angles radians.

Entity selections are deliberately not serialized. Surface limits depending on
the selected face are checked when applying the preset to that face.
"""

from ..i18n import tr

from dataclasses import asdict, dataclass
import json

from .helix_segments import HelixSegment, SegmentedHelix, _finite, _positive
from .variable_helix import MAX_SEGMENTS, sampling_plan

PRESET_EXTENSION = '.helixpilot.json'
MAX_JSON_BYTES = 128 * 1024


def _boolean(value, label):
    if type(value) is not bool:
        raise ValueError(tr('{p0} must be a boolean value.', p0=label))


def _keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(tr('Preset contains missing or unknown fields.'))


@dataclass(frozen=True)
class SurfaceSettings:
    pitch_start: float = 0.5
    pitch_end: float = 0.5
    offset: float = 0.0
    start_angle: float = 0.0
    right_handed: bool = True
    reverse: bool = False

    def __post_init__(self):
        _positive(self.pitch_start, tr('Start pitch'))
        _positive(self.pitch_end, tr('End pitch'))
        _finite(self.offset, tr('Surface offset'))
        _finite(self.start_angle, tr('Start angle'))
        _boolean(self.right_handed, tr('Handedness'))
        _boolean(self.reverse, tr('Switch boundaries'))


@dataclass(frozen=True)
class HelixPreset:
    name: str
    parameters: object
    reverse_axis: bool = False
    tangent_joins: bool = True

    def __post_init__(self):
        if (not isinstance(self.name, str) or not self.name.strip()
                or len(self.name) > 100 or any(ord(c) < 32 for c in self.name)):
            raise ValueError(tr('Preset name must contain 1 to 100 characters without control characters.'))
        _boolean(self.reverse_axis, tr('Axis direction'))
        _boolean(self.tangent_joins, tr('Tangent joins'))
        if isinstance(self.parameters, SegmentedHelix):
            sampling_plan(self.parameters)
        elif isinstance(self.parameters, SurfaceSettings):
            if self.reverse_axis:
                raise ValueError(tr('Surface presets use boundary switching instead of axis direction.'))
        else:
            raise ValueError(tr('Invalid preset parameters.'))

    @property
    def mode(self):
        return 'surface' if isinstance(self.parameters, SurfaceSettings) else 'parametric'

    def to_dict(self):
        parameters = asdict(self.parameters)
        if self.mode == 'parametric':
            parameters['segments'] = list(parameters['segments'])
        return dict(schema_version=1, name=self.name, mode=self.mode,
                    length_unit='cm', angle_unit='rad', parameters=parameters,
                    reverse_axis=self.reverse_axis, tangent_joins=self.tangent_joins)

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, allow_nan=False, indent=2) + '\n'

    @classmethod
    def from_dict(cls, data):
        _keys(data, ('schema_version', 'name', 'mode', 'length_unit', 'angle_unit',
                     'parameters', 'reverse_axis', 'tangent_joins'))
        if type(data['schema_version']) is not int or data['schema_version'] != 1:
            raise ValueError(tr('Unsupported preset schema version.'))
        if data['length_unit'] != 'cm' or data['angle_unit'] != 'rad':
            raise ValueError(tr('Preset units must be cm and rad.'))
        values = data['parameters']
        if data['mode'] == 'parametric':
            _keys(values, ('segments', 'start_angle', 'right_handed'))
            rows = values['segments']
            if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_SEGMENTS:
                raise ValueError(tr('Preset requires 1 to {p0} sections.', p0=MAX_SEGMENTS))
            segments = []
            for row in rows:
                _keys(row, HelixSegment.__dataclass_fields__)
                segments.append(HelixSegment(**row))
            parameters = SegmentedHelix(segments, values['start_angle'], values['right_handed'])
        elif data['mode'] == 'surface':
            _keys(values, SurfaceSettings.__dataclass_fields__)
            parameters = SurfaceSettings(**values)
        else:
            raise ValueError(tr('Unknown preset mode.'))
        return cls(data['name'], parameters, data['reverse_axis'], data['tangent_joins'])

    @classmethod
    def from_json(cls, text):
        if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_JSON_BYTES:
            raise ValueError(tr('Preset must be JSON text no larger than 128 KiB.'))

        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(tr('Duplicate JSON field: {p0}', p0=key))
                result[key] = value
            return result

        def invalid_constant(value):
            raise ValueError(tr('Invalid JSON number: {p0}', p0=value))

        try:
            data = json.loads(text, object_pairs_hook=unique_object,
                              parse_constant=invalid_constant)
            return cls.from_dict(data)
        except (TypeError, OverflowError, RecursionError, ValueError) as error:
            raise ValueError(tr('Invalid preset: {p0}', p0=error)) from error
