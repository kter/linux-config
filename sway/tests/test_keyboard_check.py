"""Regression guards use fixture text, never import the live Toshy config."""
import importlib.util
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/keyboard-check.py'
spec = importlib.util.spec_from_file_location('keyboard_check', SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

GOOD = '''input type:keyboard {
    xkb_options caps:ctrl_modifier
}
exec_always --no-startup-id ~/.config/sway/scripts/toshy-restart.sh
bindsym $mod+Shift+Return exec foot --app-id=foot-floating
'''
TOSHY = '''term_regex = r"^(foot|foot-floating|local\\.quickmemo)$"
cursor_exclude_regex = r"^(foot|foot-floating|local\\.quickmemo)$"
'''


class KeyboardCheckTests(unittest.TestCase):
    def test_good(self):
        self.assertEqual(checker.check_config(GOOD, TOSHY), [])

    def test_xkb_allowlist(self):
        bad = GOOD.replace('caps:ctrl_modifier', 'caps:ctrl_modifier,ctrl:swap_ralt_rctl')
        errors = checker.check_config(bad, TOSHY)
        self.assertTrue(any('ctrl:swap_ralt_rctl' in error and 'virtual keyboard' in error for error in errors))
        self.assertEqual(checker.check_config(GOOD.replace('caps:ctrl_modifier', 'ctrl:nocaps'), TOSHY), [])

    def test_terminal_missing_and_present(self):
        errors = checker.check_config(GOOD, TOSHY.replace('foot|foot-floating', 'foot', 1))
        self.assertTrue(any('foot-floating' in e and 'sway/config' in e and 'term_regex' in e for e in errors))
        self.assertEqual(checker.check_config(GOOD, TOSHY), [])

    def test_all_explicit_id_forms(self):
        for command, option in [('foot', '--app-id=X'), ('foot', '--app-id "X"'),
                                ('foot', '-a X'), ('footclient', '-aX'),
                                ('ghostty', '--class=X'), ('ghostty', '--class "X"'),
                                ('kitty', '--class=X'), ('alacritty', '--class X'),
                                ('wezterm', '--class=X')]:
            with self.subTest(command=command, option=option):
                self.assertEqual(checker.terminal_ids(f'{command} {option}'), ['X'])

    def test_shell_command_boundaries(self):
        self.assertEqual(checker.terminal_ids('foot --app-id=X; ghostty --class=Y'), ['X', 'Y'])

    def test_quickmemo_and_local_variable(self):
        for script in ('ghostty --class=local.quickmemo',
                       'APP_ID=local.quickmemo\nghostty --class="$APP_ID" -e nvim'):
            self.assertEqual(checker.terminal_ids(script), ['local.quickmemo'])
            errors = checker.check_config(GOOD, TOSHY.replace('|local\\.quickmemo', ''), {'sway/scripts/memo.sh': script})
            self.assertTrue(any('local.quickmemo' in e and 'sway/scripts/memo.sh' in e for e in errors))

    def test_fullmatch_and_both_patterns(self):
        errors = checker.check_config(GOOD, 'term_regex = "foot"\ncursor_exclude_regex = "foot"')
        self.assertEqual(len(errors), 2)
        self.assertTrue(any('cursor_exclude_regex' in e for e in errors))

    def test_missing_invalid_and_nested_regex(self):
        for text in ('', 'if True:\n    term_regex = "foo"', 'term_regex = "["'):
            self.assertTrue(checker.check_config(GOOD, text))

    def test_no_toshy_import(self):
        self.assertEqual(checker.check_config(GOOD, 'import nonexistent_module\n' + TOSHY), [])

    def test_raw_restart_and_start(self):
        for verb in ('start', 'restart'):
            errors = checker.check_config(GOOD + f'\nexec_always systemctl --user {verb} toshy-wlroots-dbus.service toshy-config.service', TOSHY)
            self.assertTrue(any('raw Toshy' in e for e in errors))
        self.assertEqual(checker.check_config(GOOD.replace('~/', '$HOME/'), TOSHY), [])
        self.assertTrue(checker.check_config('xkb_options ctrl:nocaps', TOSHY))

    def test_raw_restart_argument_orders_and_verbs(self):
        for arguments in ('--user --no-block restart', 'restart --user',
                          '--user try-restart', '--user reload-or-restart',
                          '--user try-reload-or-restart'):
            with self.subTest(arguments=arguments):
                errors = checker.check_config(
                    GOOD + f'\nexec_always systemctl {arguments} toshy-config.service', TOSHY)
                self.assertTrue(any('raw Toshy' in error for error in errors))

    def test_systemctl_status_passes(self):
        self.assertEqual(checker.check_config(
            GOOD + '\nexec systemctl --user status toshy-config.service', TOSHY), [])

    def test_restart_command_boundaries_and_unit_words(self):
        for command in ('systemctl --user status toshy-config.service; echo restart',
                        'systemctl --user restart other.service && echo toshy-config.service',
                        'systemctl --user restart other-toshy-config.service'):
            with self.subTest(command=command):
                self.assertEqual(checker.check_config(GOOD + '\nexec ' + command, TOSHY), [])
        self.assertTrue(any('raw Toshy' in error for error in checker.check_config(
            GOOD + '\nexec echo ready; systemctl restart toshy-config --user', TOSHY)))

    def test_comments_and_continuations(self):
        comments = '\n  # xkb_options bad\n# systemctl --user restart toshy-config.service\n# foot -a bad\n'
        self.assertEqual(checker.check_config(GOOD + comments, TOSHY), [])
        self.assertEqual(checker.terminal_ids('foot \\\n --app-id=X'), ['X'])

    def test_local_preferences(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'prefs.sqlite'
            self.assertIn('Local check needs', checker.check_local(path)[0])
            with closing(sqlite3.connect(path)) as db:
                db.execute('CREATE TABLE config_preferences(name TEXT, value TEXT)')
                db.execute("INSERT INTO config_preferences VALUES ('multi_lang', 'True')")
                db.commit()
            self.assertEqual(checker.check_local(path), [])
            with closing(sqlite3.connect(path)) as db:
                db.execute("UPDATE config_preferences SET value = 'False'")
                db.commit()
            self.assertIn('multi_lang', checker.check_local(path)[0])

    def test_default_does_not_touch_sqlite(self):
        with patch.object(checker.sqlite3, 'connect', side_effect=AssertionError('sqlite touched')):
            self.assertEqual(checker.main([]), 0)

    def test_real_repo(self):
        self.assertEqual(checker.check_repo(), [])


if __name__ == '__main__':
    unittest.main()
