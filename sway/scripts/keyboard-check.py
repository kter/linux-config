#!/usr/bin/env python3
"""Static guards for the Sway/Toshy keyboard boundary (no Toshy imports)."""
import argparse
import ast
from contextlib import closing
from pathlib import Path
import re
import shlex
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_OPTIONS = {'caps:ctrl_modifier', 'ctrl:nocaps'}
REGEX_NAMES = ('term_regex', 'cursor_exclude_regex')
TERMINALS = {'foot', 'footclient', 'ghostty', 'kitty', 'alacritty', 'wezterm'}


def active_lines(text):
    return [line for line in text.splitlines() if not line.lstrip().startswith('#')]


def terminal_ids(text):
    """Collect explicit IDs, including simple file-local shell variables."""
    variables = {}
    found = []
    for line in active_lines(text.replace('\\\n', ' ')):
        if not (re.search(r'(?<![\w-])(?:footclient|foot|ghostty|kitty|alacritty|wezterm)\s', line)
                or re.match(r'^\s*[A-Za-z_]\w*=', line)):
            continue
        # shlex.split retains words such as --class=$APP_ID as one token.
        lexer = shlex.shlex(line, posix=True, punctuation_chars=';|&')
        lexer.whitespace_split = True
        words = list(lexer)
        if len(words) == 1 and re.fullmatch(r'[A-Za-z_]\w*=.*', words[0]):
            name, value = words[0].split('=', 1)
            variables[name] = value
        for index, word in enumerate(words):
            terminal = Path(word).name
            if terminal not in TERMINALS:
                continue
            options = ('--app-id', '-a') if terminal in {'foot', 'footclient'} else ('--class',)
            for offset in range(index + 1, len(words)):
                arg = words[offset]
                if arg in {'-e', '--', ';', '&&', '|', '&'}:
                    break
                value = None
                for option in options:
                    if arg == option and offset + 1 < len(words):
                        value = words[offset + 1]
                    elif arg.startswith(option + '='):
                        value = arg[len(option) + 1:]
                    elif option == '-a' and arg.startswith('-a') and len(arg) > 2:
                        value = arg[2:]
                if value is not None:
                    value = re.sub(r'\$\{(\w+)\}|\$(\w+)',
                                   lambda m: variables.get(m[1] or m[2], m[0]), value)
                    found.append(value)
    return found


def check_config(sway_text, toshy_text, scripts=None):
    errors = []
    lines = active_lines(sway_text.replace('\\\n', ' '))
    for line in lines:
        for match in re.finditer(r'\bxkb_options\s+("[^"]*"|\x27[^\x27]*\x27|[^\s;}#]+)', line):
            for option in match[1].strip('\"\x27').split(','):
                if option not in ALLOWED_OPTIONS:
                    errors.append(f'xkb_options {option!r}: Toshy is the only layer allowed to remap '
                                  'modifiers; xkb only sees Toshy\'s virtual keyboard. See sway/README.md.')
    patterns = {}
    try:
        for node in ast.parse(toshy_text).body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in REGEX_NAMES:
                        patterns.pop(target.id, None)
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            patterns[target.id] = node.value.value
    except SyntaxError as exc:
        errors.append(f'toshy/toshy_config.py: invalid Python: {exc.msg}')
    compiled = {}
    for name in REGEX_NAMES:
        if name not in patterns:
            errors.append(f'toshy/toshy_config.py: missing module-level string assignment {name}')
        else:
            try:
                compiled[name] = re.compile(patterns[name])
            except re.error as exc:
                errors.append(f'{name}: invalid regex: {exc}')
    for filename, text in {'sway/config': sway_text, **(scripts or {})}.items():
        try:
            ids = terminal_ids(text)
        except ValueError as exc:
            errors.append(f'{filename}: cannot parse launch commands: {exc}')
            continue
        for app_id in ids:
            for name, pattern in compiled.items():
                if not pattern.fullmatch(app_id):
                    errors.append(f'{filename}: terminal ID {app_id!r} is missing from {name}')
    for line in lines:
        lexer = shlex.shlex(line, posix=True, punctuation_chars=';|&')
        lexer.whitespace_split = True
        try:
            words = list(lexer)
        except ValueError as exc:
            errors.append(f'sway/config: cannot parse restart commands: {exc}')
            continue
        command = []
        for word in words + [';']:
            if word and all(char in ';|&' for char in word):
                for index, token in enumerate(command):
                    if Path(token).name != 'systemctl':
                        continue
                    arguments = set(command[index + 1:])
                    if ('--user' in arguments
                            and arguments & {'start', 'restart', 'try-restart',
                                             'reload-or-restart', 'try-reload-or-restart'}
                            and arguments & {'toshy-config', 'toshy-config.service'}):
                        errors.append('sway/config: raw Toshy start/restart; use sway/scripts/toshy-restart.sh')
                command = []
            else:
                command.append(word)
    if not any(re.search(r'(?:~|\$HOME)/\.config/sway/scripts/toshy-restart\.sh\b', line) for line in lines):
        errors.append('sway/config: must reference ~/.config/sway/scripts/toshy-restart.sh')
    return errors


def check_local(path):
    path = Path(path)
    if not path.is_file():
        return [f'Local check needs {path} (Toshy preferences sqlite file)']
    try:
        with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as connection:
            row = connection.execute("SELECT value FROM config_preferences WHERE name = 'multi_lang'").fetchone()
        if row is None or row[0] != 'True':
            return ["Toshy multi_lang must be 'True' so physical Right Alt reaches apps as Alt_R"]
    except sqlite3.Error as exc:
        return [f'Cannot read Toshy preferences: {exc}']
    return []


def check_repo(root=ROOT):
    root = Path(root)
    return check_config((root / 'sway/config').read_text(),
                        (root / 'toshy/toshy_config.py').read_text(),
                        {str(p.relative_to(root)): p.read_text() for p in sorted((root / 'sway/scripts').glob('*.sh'))})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local', action='store_true', help='also check untracked Toshy preferences')
    args = parser.parse_args(argv)
    try:
        errors = check_repo()
        if args.local:
            errors += check_local(ROOT / 'toshy/toshy_user_preferences.sqlite')
    except OSError as exc:
        errors = [str(exc)]
    for error in errors:
        print(f'ERROR: {error}')
    if not errors:
        print('OK: keyboard config guards passed' + (' (including local preferences)' if args.local else ''))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
