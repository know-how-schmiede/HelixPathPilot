from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Fusion_addin'))
from HelixPathPilot.core.cleanup import cleanup_created


class CleanupTests(unittest.TestCase):
    def test_success_returns_and_deletes_in_reverse_order(self):
        order = []
        first, second = Mock(), Mock()
        first.deleteMe.side_effect = lambda: order.append('first')
        second.deleteMe.side_effect = lambda: order.append('second')
        cleanup_created([('first', first), ('second', second)], ValueError('original'))
        self.assertEqual(order, ['second', 'first'])

    def test_failed_cleanup_preserves_cause_and_continues(self):
        first, second = Mock(), Mock()
        first.deleteMe.return_value = False
        second.deleteMe.side_effect = RuntimeError('locked')
        original = ValueError('sweep failed')
        with self.assertRaises(RuntimeError) as raised:
            cleanup_created([('plane', first), ('profile', second)], original)
        self.assertIs(raised.exception.__cause__, original)
        for text in ('sweep failed', 'plane', 'profile', 'locked'):
            self.assertIn(text, str(raised.exception))
        first.deleteMe.assert_called_once()

    def test_empty_cleanup_keeps_original_failure(self):
        self.assertIsNone(cleanup_created([], ValueError('original')))
