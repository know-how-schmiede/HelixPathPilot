"""Portable preset schema, rejection and packaged examples."""

import copy
import json
from pathlib import Path
import sys
import unittest

ADDIN = Path(__file__).resolve().parents[1] / 'Fusion_addin/HelixPathPilot'
sys.path.insert(0, str(ADDIN.parent))
from HelixPathPilot.core.helix_segments import HelixSegment, SegmentedHelix
from HelixPathPilot.core.presets import HelixPreset, SurfaceSettings


class PresetTests(unittest.TestCase):
    def setUp(self):
        self.preset = HelixPreset('Feder ä', SegmentedHelix((
            HelixSegment(5, 2, 3, 0.5, 1), HelixSegment(2, 3, 2, 1, 0.5)),
            1.25, False), True, False)

    def test_parametric_roundtrip_and_snapshot(self):
        self.assertEqual(HelixPreset.from_json(self.preset.to_json()), self.preset)
        data = self.preset.to_dict()
        data['parameters']['segments'][0]['length'] = 99
        self.assertEqual(self.preset.parameters.segments[0].length, 5)

    def test_surface_roundtrip_preserves_negative_offset_and_reverse(self):
        preset = HelixPreset('Mantel', SurfaceSettings(1, 0.2, -0.5, 2, False, True))
        self.assertEqual(HelixPreset.from_json(preset.to_json()), preset)
        self.assertNotIn('segments', preset.to_dict()['parameters'])

    def test_rejects_schema_units_modes_and_unknown_fields(self):
        for key, value in (('schema_version', 2), ('schema_version', True),
                           ('length_unit', 'mm'), ('angle_unit', 'deg'),
                           ('mode', 'other'), ('extra', 1), ('reverse_axis', 1),
                           ('tangent_joins', 'true'), ('name', ' ')):
            data = self.preset.to_dict()
            data[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                HelixPreset.from_dict(data)
        for key in self.preset.to_dict():
            data = self.preset.to_dict()
            del data[key]
            with self.assertRaises(ValueError):
                HelixPreset.from_dict(data)

    def test_rejects_invalid_segments_and_limits(self):
        base = self.preset.to_dict()
        for rows in ([], [None], [dict(length=1)],
                     base['parameters']['segments'] * 17):
            data = copy.deepcopy(base)
            data['parameters']['segments'] = rows
            with self.assertRaises(ValueError):
                HelixPreset.from_dict(data)
        for field, value in (('pitch_start', 0), ('length', True),
                             ('diameter_end', 4), ('length', 10000)):
            data = copy.deepcopy(base)
            data['parameters']['segments'][0][field] = value
            with self.assertRaises(ValueError):
                HelixPreset.from_dict(data)

    def test_rejects_malformed_duplicate_nonfinite_and_large_json(self):
        for text in ('{', '[]', 'null', '{"a":1,"a":2}', '{"a":NaN}',
                     '{"a":Infinity}', '['*1100 + ']'*1100, ' '*131073):
            with self.subTest(text=text[:30]), self.assertRaises(ValueError):
                HelixPreset.from_json(text)
        data = self.preset.to_dict()
        data['parameters']['start_angle'] = float('inf')
        with self.assertRaises(ValueError):
            HelixPreset.from_json(json.dumps(data))

    def test_invalid_surface_fields(self):
        for kwargs in (dict(pitch_start=0), dict(pitch_end=-1), dict(offset=float('nan')),
                       dict(reverse=1), dict(start_angle=True), dict(right_handed='yes')):
            with self.assertRaises(ValueError):
                SurfaceSettings(**kwargs)
        with self.assertRaises(ValueError):
            HelixPreset('Surface', SurfaceSettings(), reverse_axis=True)

    def test_packaged_examples(self):
        files = sorted((ADDIN / 'presets/builtin').glob('*.helixpilot.json'))
        self.assertEqual(len(files), 3)
        presets = [HelixPreset.from_json(path.read_text(encoding='utf-8')) for path in files]
        self.assertEqual(len({p.name for p in presets}), 3)
        self.assertEqual({p.mode for p in presets}, {'surface', 'parametric'})
        for preset in presets:
            self.assertEqual(HelixPreset.from_json(preset.to_json()), preset)
