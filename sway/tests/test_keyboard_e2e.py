"""Pure event helpers only: no uinput, windows, or live session access."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/keyboard-e2e-test.py'
spec = importlib.util.spec_from_file_location('keyboard_e2e', SCRIPT)
e2e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e2e)


def wev_event(sym, pressed):
    return (f'[ 16: wl_keyboard] key: serial: 98433; time: 54051604; key: 108; '
            f'state: {int(pressed)} ({"pressed" if pressed else "released"})\n'
            f"                      sym: {sym}        (65514), utf8: ''\n")


class KeyboardE2eTests(unittest.TestCase):
    def test_wev_parser(self):
        text = 'unrelated output\n' + wev_event('Alt_R', True) + wev_event('Alt_R', False)
        self.assertEqual(e2e.parse_wev(text), [('Alt_R', True), ('Alt_R', False)])

    def test_partial_or_unrelated_lines(self):
        self.assertEqual(e2e.parse_wev('sym: e\n[ 16: wl_keyboard] key: state: 1\n'), [])
        self.assertEqual(e2e.parse_wev('[ 16: wl_keyboard] keymap: foo\nsym: e\n'), [])

    def test_held_set(self):
        events = [('Alt_L', True), ('Alt_L', False), ('Control_R', True), ('t', True),
                  ('t', False), ('Control_R', False)]
        self.assertEqual(e2e.held_at_press(events, 't'), {'Control_R'})
        self.assertIsNone(e2e.held_at_press(events, 'e'))
        self.assertEqual(e2e.held_at_press([('e', True)], 'e'), set())

    def test_swap_regression_visible(self):
        events = e2e.parse_wev(wev_event('Alt_R', True) + wev_event('t', True))
        held = e2e.held_at_press(events, 't')
        self.assertIn('Alt_R', held)
        self.assertFalse(held & {'Control_L', 'Control_R'})

    def test_press_then_release_required(self):
        self.assertTrue(e2e.pressed_and_released([('e', True), ('e', False)], 'e'))
        for events in ([], [('e', True)], [('e', False)], [('e', False), ('e', True)]):
            self.assertFalse(e2e.pressed_and_released(events, 'e'))

    def test_hex_bytes(self):
        self.assertEqual(e2e.parse_hex('03\n65\n'), b'\x03e')
        self.assertEqual(e2e.parse_hex(''), b'')
        self.assertEqual(e2e.parse_hex('1b 5b 43'), b'\x1b[C')
        with self.assertRaises(ValueError):
            e2e.parse_hex('not hex')


if __name__ == '__main__':
    unittest.main()
