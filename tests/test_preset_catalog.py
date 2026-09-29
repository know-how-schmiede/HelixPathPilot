"""Bad packaged files must not prevent opening the helix command."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ADDIN = Path(__file__).resolve().parents[1] / 'Fusion_addin/HelixPathPilot'
sys.path.insert(0, str(ADDIN.parent))
spec = importlib.util.spec_from_file_location(
    'HelixPathPilot.commands.presetManager.catalog', ADDIN / 'commands/presetManager/catalog.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def test_bad_files_are_reported_while_valid_examples_remain_available(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'valid.helixpilot.json').write_bytes(
                (ADDIN / 'presets/builtin/basic.helixpilot.json').read_bytes())
            (root / 'broken.helixpilot.json').write_text('{', encoding='utf-8')
            (root / 'encoding.helixpilot.json').write_bytes(b'\xff')
            (root / 'huge.helixpilot.json').write_bytes(b' ' * 131073)
            presets, errors = catalog.builtin_presets(root)
            self.assertEqual(len(presets), 1)
            self.assertEqual(len(errors), 3)
            self.assertTrue(any('broken.helixpilot.json' in error for error in errors))

    def test_missing_catalog(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(catalog.builtin_presets(Path(folder) / 'missing'), ([], []))
