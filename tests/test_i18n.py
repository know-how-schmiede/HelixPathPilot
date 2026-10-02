"""Language resolution, translation integrity and portable data regressions."""

import ast
import importlib.util
import json
from pathlib import Path
from string import Formatter
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ADDIN = Path(__file__).resolve().parents[1] / 'Fusion_addin/HelixPathPilot'
sys.path.insert(0, str(ADDIN.parent))

from HelixPathPilot import i18n
from HelixPathPilot.core.helix_segments import HelixSegment, SegmentedHelix
from HelixPathPilot.core.presets import HelixPreset
from HelixPathPilot.core.variable_helix import segmented_points


def fields(text):
    return sorted((key, spec, conversion) for _, key, spec, conversion
                  in Formatter().parse(text) if key is not None)


class TranslationTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(i18n.set_language, i18n.get_language())
        self.addCleanup(i18n._catalog.cache_clear)
        i18n.set_language('en')
        i18n._catalog.cache_clear()

    def test_default_and_normalized_language_codes(self):
        self.assertEqual(i18n.tr('Settings'), 'Settings')
        for code, expected in [('DE-de', 'de'), ('fr_FR', 'fr'), ('es', 'es'),
                               ('pl-PL', 'pl'), ('ja', 'en'), (None, 'en')]:
            self.assertEqual(i18n.set_language(code), expected)

    def test_fusion_enum_mapping_and_unsupported_language(self):
        adsk = types.ModuleType('adsk')
        adsk.core = types.ModuleType('adsk.core')
        # Intentionally different values from today's SDK: use symbolic members.
        adsk.core.UserLanguages = types.SimpleNamespace(
            EnglishLanguage=100, GermanLanguage=101, FrenchLanguage=102,
            SpanishLanguage=103, PolishLanguage=104)
        general = types.SimpleNamespace(userLanguage=None)
        app = types.SimpleNamespace(preferences=types.SimpleNamespace(generalPreferences=general))
        with patch.dict(sys.modules, {'adsk': adsk, 'adsk.core': adsk.core}):
            for value, expected in [(100, 'en'), (101, 'de'), (102, 'fr'),
                                    (103, 'es'), (104, 'pl'), (999, 'en')]:
                general.userLanguage = value
                self.assertEqual(i18n.configure_from_fusion(app), expected)
                self.assertEqual(general.userLanguage, value)
            del adsk.core.UserLanguages.PolishLanguage
            general.userLanguage = 104
            self.assertEqual(i18n.configure_from_fusion(app), 'en')
            i18n.set_language('de')
            self.assertEqual(i18n.configure_from_fusion(object()), 'en')

    def test_all_catalogs_are_complete_and_preserve_formatting(self):
        english = json.loads((ADDIN / 'locales/en.json').read_text(encoding='utf-8'))
        self.assertEqual(set(english), set(english.values()))
        for language in i18n.SUPPORTED_LANGUAGES:
            catalog = json.loads((ADDIN / f'locales/{language}.json').read_text(encoding='utf-8'))
            self.assertEqual(set(catalog), set(english), language)
            i18n.set_language(language)
            for source, translated in catalog.items():
                with self.subTest(language=language, source=source):
                    self.assertTrue(translated.strip())
                    self.assertEqual(fields(source), fields(translated))
                    values = {key: 1.25 if spec else 'test' for key, spec, _ in fields(source)}
                    self.assertEqual(i18n.tr(source, **values), translated.format(**values))
                    # Links must keep the same destinations in every language.
                    import re
                    self.assertEqual(re.findall(r'href="([^"]+)"', source),
                                     re.findall(r'href="([^"]+)"', translated))

    def test_source_messages_are_cataloged_and_not_translated_on_import(self):
        english = json.loads((ADDIN / 'locales/en.json').read_text(encoding='utf-8'))
        for path in list((ADDIN / 'core').glob('*.py')) + list((ADDIN / 'commands').rglob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'tr':
                    if isinstance(node.args[0], ast.Constant):
                        self.assertIn(node.args[0].value, english, str(path))
            for statement in tree.body:
                if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                    self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                                         and node.func.id == 'tr' for node in ast.walk(statement)), str(path))

    def test_missing_broken_and_incompatible_translations_fall_back(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(i18n, '_LOCALES', Path(folder)):
            i18n.set_language('fr')
            self.assertEqual(i18n.tr('Hello {name}', name='Ada'), 'Hello Ada')
            for content in ['{', '[]', '{"Settings": null}',
                            '{"Hello {name}": "Bonjour {wrong}"}',
                            '{"Hello {name}": "Bonjour {"}',
                            '{"Hello {name}": ""}']:
                (Path(folder) / 'fr.json').write_text(content, encoding='utf-8')
                i18n._catalog.cache_clear()
                self.assertEqual(i18n.tr('Hello {name}', name='Ada'), 'Hello Ada')
                self.assertEqual(i18n.tr('Settings'), 'Settings')

    def test_user_values_are_not_translated_or_formatted_twice(self):
        i18n.set_language('pl')
        name = 'Settings {p0} – Żółć / 中文'
        self.assertEqual(i18n.tr('Saved: {p0}.', p0=name), f'Zapisano: {name}.')

    def test_presets_and_geometry_are_identical_across_languages(self):
        model = SegmentedHelix((HelixSegment.constant(5, 2, .5),))
        preset = HelixPreset('Zwei variable Abschnitte {custom}', model)
        data = preset.to_json()
        points = segmented_points(model)
        for language in i18n.SUPPORTED_LANGUAGES:
            i18n.set_language(language)
            self.assertEqual(preset.to_json(), data)
            self.assertEqual(HelixPreset.from_json(data), preset)
            self.assertEqual(segmented_points(model), points)

    def test_builtin_display_names_do_not_change_portable_names(self):
        spec = importlib.util.spec_from_file_location(
            'HelixPathPilot.commands.presetManager.catalog', ADDIN / 'commands/presetManager/catalog.py')
        catalog = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(catalog)
        presets, errors = catalog.builtin_presets()
        self.assertFalse(errors)
        original = [preset.to_json() for preset in presets]
        for language in i18n.SUPPORTED_LANGUAGES:
            i18n.set_language(language)
            for preset in presets:
                self.assertEqual(catalog.preset_display_name(preset), preset.name)
                self.assertTrue(catalog.preset_display_name(preset, builtin=True))
            self.assertEqual([preset.to_json() for preset in presets], original)
        i18n.set_language('en')
        self.assertEqual(catalog.preset_display_name(presets[0], builtin=True), 'Basic helix 20 × 50 mm')


if __name__ == '__main__':
    unittest.main()
