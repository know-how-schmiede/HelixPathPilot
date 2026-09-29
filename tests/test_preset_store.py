"""Persistent user presets, names, corrupt files and write failures."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Fusion_addin'))
from HelixPathPilot.core.preset_store import PresetStore
from HelixPathPilot.core.presets import HelixPreset, SurfaceSettings, PRESET_EXTENSION


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / 'presets'
        self.store = PresetStore(self.folder)

    def test_persistence_unicode_names_and_delete(self):
        preset = HelixPreset('Feder ä / : ..', SurfaceSettings(offset=-0.2))
        key = self.store.save(preset)
        reopened = PresetStore(self.folder)
        self.assertEqual(reopened.load(key), preset)
        self.assertEqual(reopened.list(), ([(key, preset)], []))
        self.assertEqual(len(list(self.folder.iterdir())), 1)
        reopened.delete(key)
        self.assertEqual(reopened.list(), ([], []))

    def test_duplicate_name_never_overwrites(self):
        key = self.store.save(HelixPreset(' Äpfel ', SurfaceSettings()))
        before = self.store.load(key)
        with self.assertRaises(ValueError):
            self.store.save(HelixPreset('äPFEL', SurfaceSettings(offset=2)))
        self.assertEqual(self.store.load(key), before)

    def test_missing_folder_is_not_created_by_listing(self):
        self.assertEqual(self.store.list(), ([], []))
        self.assertFalse(self.folder.exists())

    def test_invalid_keys_and_corrupt_file(self):
        for key in ('../outside', '', 'A'*64):
            with self.assertRaises(ValueError):
                self.store.delete(key)
        key = self.store.save(HelixPreset('Valid', SurfaceSettings()))
        (self.folder / ('a'*64 + PRESET_EXTENSION)).write_text('{', encoding='utf-8')
        entries, errors = self.store.list()
        self.assertEqual(entries[0][0], key)
        self.assertEqual(len(errors), 1)

    def test_failed_write_removes_incomplete_file(self):
        with patch('HelixPathPilot.core.preset_store.os.fsync', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.store.save(HelixPreset('Failure', SurfaceSettings()))
        self.assertEqual(list(self.folder.iterdir()), [])
