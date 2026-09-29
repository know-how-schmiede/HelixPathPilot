import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

ADDIN = Path(__file__).resolve().parents[1] / 'Fusion_addin/HelixPathPilot'
sys.path.insert(0, str(ADDIN.parent))


class LoggingTests(unittest.TestCase):
    def setUp(self):
        adsk = types.ModuleType('adsk')
        adsk.core = types.ModuleType('adsk.core')
        adsk.core.Application = Mock()
        adsk.core.LogLevels = types.SimpleNamespace(InfoLogLevel=0, ErrorLogLevel=1)
        adsk.core.LogTypes = types.SimpleNamespace(FileLogType=0, ConsoleLogType=1)
        modules = patch.dict(sys.modules, {'adsk': adsk, 'adsk.core': adsk.core})
        modules.start()
        self.addCleanup(modules.stop)
        spec = importlib.util.spec_from_file_location(
            'HelixPathPilot.lib.fusionAddInUtils.general_utils',
            ADDIN / 'lib/fusionAddInUtils/general_utils.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.module.DEBUG = False
        self.app = adsk.core.Application.get.return_value
        printer = patch('builtins.print')
        self.printer = printer.start()
        self.addCleanup(printer.stop)

    def test_error_is_one_entry_with_version_timestamp_and_traceback(self):
        from HelixPathPilot.version import VERSION
        try:
            raise ValueError('original failure')
        except ValueError:
            self.module.handle_error('Sweep')
        self.app.log.assert_called_once()
        message, level, target = self.app.log.call_args.args
        for text in (VERSION, 'Sweep', 'ValueError: original failure', 'Traceback'):
            self.assertIn(text, message)
        self.assertRegex(message, r'^\[\d{4}-\d{2}-\d{2}T.*\+00:00\]')
        self.assertEqual((level, target), (1, 0))

    def test_broken_sinks_do_not_escape_error_handler(self):
        self.printer.side_effect = OSError('stdout closed')
        self.app.log.side_effect = RuntimeError('Fusion logging unavailable')
        self.app.userInterface.messageBox.side_effect = RuntimeError('UI unavailable')
        self.module.DEBUG = True
        try:
            raise ValueError('original')
        except ValueError:
            self.module.handle_error('Create', show_message_box=True)
        self.assertEqual(self.app.log.call_count, 2)

    def test_normal_info_does_not_write_fusion_file_or_console(self):
        self.module.log('started')
        self.app.log.assert_not_called()
        self.printer.assert_called_once()

    def test_force_console_remains_available(self):
        self.module.log('diagnostic', force_console=True)
        self.assertEqual(self.app.log.call_args.args[1:], (0, 1))
