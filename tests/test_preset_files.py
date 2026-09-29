"""File exchange must preserve values and existing files on failure."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Fusion_addin'))
from HelixPathPilot.core.preset_files import read_preset_file, write_preset_file, export_path
from HelixPathPilot.core.presets import HelixPreset, SurfaceSettings
from HelixPathPilot.core.helix_segments import HelixSegment, SegmentedHelix


class FileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.preset = HelixPreset('Fläche ä', SurfaceSettings(0.5, 1, -0.2, 1, False, True))

    def test_roundtrip_both_modes_and_extension(self):
        for index, preset in enumerate((self.preset, HelixPreset('Feder', SegmentedHelix((
                HelixSegment(5, 2, 3, 0.5, 1), HelixSegment(2, 3, 2, 1, 0.5)))))):
            path = write_preset_file(self.root / str(index), preset)
            self.assertTrue(path.name.endswith('.helixpilot.json'))
            self.assertEqual(read_preset_file(path), preset)
            self.assertNotIn(b'\r\n', path.read_bytes())
        self.assertEqual(export_path('name.HELIXPILOT.JSON'), Path('name.HELIXPILOT.JSON'))

    def test_no_unapproved_overwrite(self):
        path = write_preset_file(self.root / 'test', self.preset)
        before = path.read_bytes()
        with self.assertRaises(FileExistsError):
            write_preset_file(path, HelixPreset('Other', SurfaceSettings()))
        self.assertEqual(path.read_bytes(), before)

    def test_failed_replacement_preserves_old_file_and_cleans_temporary(self):
        path = write_preset_file(self.root / 'test', self.preset)
        before = path.read_bytes()
        for operation in ('fsync', 'replace'):
            with patch('HelixPathPilot.core.preset_files.os.' + operation, side_effect=OSError('failure')):
                with self.assertRaises(OSError):
                    write_preset_file(path, HelixPreset('Other', SurfaceSettings()), overwrite=True)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(self.root.iterdir()), [path])
        replacement = HelixPreset('Other', SurfaceSettings())
        write_preset_file(path, replacement, overwrite=True)
        self.assertEqual(read_preset_file(path), replacement)

    def test_invalid_input_and_bom(self):
        path = self.root / 'source.json'
        for content in (b'{', b'\xff', b' ' * 131073, b'{"schema_version":99}'):
            path.write_bytes(content)
            with self.assertRaises((ValueError, UnicodeError)):
                read_preset_file(path)
        path.write_bytes(b'\xef\xbb\xbf' + self.preset.to_json().encode('utf-8'))
        self.assertEqual(read_preset_file(path), self.preset)

    def test_failed_new_export_removes_partial_file(self):
        with patch('HelixPathPilot.core.preset_files.os.fsync', side_effect=OSError('failure')):
            with self.assertRaises(OSError):
                write_preset_file(self.root / 'test', self.preset)
        self.assertEqual(list(self.root.iterdir()), [])
