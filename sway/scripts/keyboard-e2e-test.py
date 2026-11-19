#!/usr/bin/env python3
"""Local Sway/Toshy injection check; run with Toshy's venv Python -I."""
from contextlib import closing
import errno
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time


def parse_wev(text):
    events = []
    pressed = None
    for line in text.splitlines():
        if 'wl_keyboard]' in line and 'key:' in line:
            match = re.search(r'\bstate:\s*([01])\b', line)
            pressed = bool(int(match[1])) if match else None
        elif pressed is not None:
            match = re.search(r'\bsym:\s*(\S+)', line)
            if match:
                events.append((match[1], pressed))
                pressed = None
    return events


def held_at_press(events, sym):
    """Return modifier/key state at the first press, or None if absent."""
    held = set()
    for name, pressed in events:
        if pressed:
            if name == sym:
                return held.copy()
            held.add(name)
        else:
            held.discard(name)
    return None


def pressed_and_released(events, sym):
    seen = False
    for name, pressed in events:
        if name == sym:
            if not pressed and seen:
                return True
            seen = seen or pressed
    return False


def parse_hex(text):
    return bytes.fromhex(text)


def sway(*args):
    result = subprocess.run(['swaymsg', *args], capture_output=True, text=True, timeout=3, check=True)
    return json.loads(result.stdout)


def nodes(tree):
    yield tree
    for child in tree.get('nodes', []) + tree.get('floating_nodes', []):
        yield from nodes(child)


def focused():
    return next((node for node in nodes(sway('-t', 'get_tree')) if node.get('focused')), {})


def wait_for(predicate, seconds, message):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.1)
    raise RuntimeError(message)


class Injector:
    def __init__(self, device, codes):
        self.device = device
        self.codes = codes
        self.held = set()
        self.pid = None

    def release_all(self):
        # Emergency releases must work even after focus leaves the test window.
        for key in list(self.held):
            self.device.write(self.codes.EV_KEY, key, 0)
            self.device.syn()
            self.held.discard(key)
            time.sleep(0.04)

    def event(self, key, pressed):
        if self.pid is None or focused().get('pid') != self.pid:
            self.release_all()
            raise RuntimeError('Focus left the test window; injection aborted')
        self.device.write(self.codes.EV_KEY, key, int(pressed))
        self.device.syn()
        if pressed:
            self.held.add(key)
        else:
            self.held.discard(key)
        time.sleep(0.04)

    def press(self, key):
        self.event(key, True)

    def release(self, key):
        self.event(key, False)

    def tap(self, key):
        self.press(key)
        self.release(key)

    def chord(self, mods, key):
        for mod in mods:
            self.press(mod)
        self.tap(key)
        for mod in reversed(mods):
            self.release(mod)

    def focus(self, process):
        wait_for(lambda: any(n.get('pid') == process.pid for n in nodes(sway('-t', 'get_tree'))),
                 5, 'Test window did not appear')
        sway(f'[pid={process.pid}] focus')
        time.sleep(0.5)
        self.pid = process.pid
        if focused().get('pid') != self.pid:
            raise RuntimeError('Could not focus the test window')


def preflight():
    for name in ('SWAYSOCK', 'WAYLAND_DISPLAY'):
        if not os.environ.get(name):
            raise RuntimeError(f'{name} must be set')
    for name in ('wev', 'foot', 'stdbuf', 'swaymsg', 'systemctl'):
        if not shutil.which(name):
            raise RuntimeError(f'{name} is required on PATH')
    if subprocess.run(['systemctl', '--user', 'is-active', '--quiet', 'toshy-config.service'],
                      capture_output=True, timeout=3).returncode:
        raise RuntimeError('toshy-config.service must be active')
    if not os.access('/dev/uinput', os.W_OK):
        raise RuntimeError('/dev/uinput must be writable')
    try:
        import evdev
    except ImportError:
        raise RuntimeError("evdev is required; use Toshy's venv Python") from None
    return evdev


TERMINAL_HELPER = '''import os, select, signal, sys, termios, time, tty
from pathlib import Path
output, ready = map(Path, sys.argv[1:])
fd = sys.stdin.fileno()
original = termios.tcgetattr(fd)
def terminate(signum, frame):
    raise SystemExit(0)
signal.signal(signal.SIGTERM, terminate)
try:
    tty.setraw(fd)
    ready.touch()
    deadline = time.monotonic() + 8
    with output.open('a', buffering=1) as stream:
        while time.monotonic() < deadline:
            if select.select([fd], [], [], 0.1)[0]:
                data = os.read(fd, 1024)
                if not data:
                    break
                stream.write(data.hex() + '\\n')
finally:
    termios.tcsetattr(fd, termios.TCSANOW, original)
'''


def stop(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)


def main():
    try:
        evdev = preflight()
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f'Preflight failed: {exc}')
        return 2
    print('WARNING: test steals focus for about 10–20 seconds. Keep hands off the keyboard.', flush=True)
    device = injector = None
    processes = []
    previous = None
    failed = False
    try:
        for count in (3, 2, 1):
            print(count, flush=True)
            time.sleep(1)
        previous = focused().get('id')
        codes = evdev.ecodes
        keys = [getattr(codes, 'KEY_' + key) for key in (
            'Q', 'W', 'E', 'R', 'T', 'Y', 'A', 'Z', 'C', 'SPACE', 'ENTER',
            'LEFTALT', 'RIGHTALT', 'LEFTCTRL', 'LEFTSHIFT', 'CAPSLOCK')]
        device = evdev.UInput({codes.EV_KEY: keys}, name='keyboard-e2e-test')
        injector = Injector(device, codes)
        if device.device is None:
            raise RuntimeError('Cannot open the test keyboard event node')

        def grabbed():
            with closing(evdev.InputDevice(device.device.path)) as probe:
                try:
                    probe.grab()
                except OSError as exc:
                    if exc.errno == errno.EBUSY:
                        return True
                    raise
                probe.ungrab()
            return False

        wait_for(grabbed, 10, 'Test keyboard was not grabbed by Toshy within 10 seconds')
        # Right after a Toshy restart, sway sends new windows an empty keymap until
        # some key event arrives (wev then crashes). A lone Shift tap is harmless.
        for value in (1, 0):
            device.write(codes.EV_KEY, codes.KEY_LEFTSHIFT, value)
            device.syn()
            time.sleep(0.05)
        time.sleep(0.3)
        with tempfile.TemporaryDirectory(prefix='keyboard-e2e-') as directory:
            root = Path(directory)
            log = root / 'wev.log'
            with log.open('w') as stream:
                gui = subprocess.Popen(['stdbuf', '-oL', 'wev', '-f', 'wl_keyboard:key'],
                                       stdout=stream, stderr=subprocess.DEVNULL)
                processes.append(gui)
                injector.focus(gui)

                def gui_case(label, inject, evaluate):
                    nonlocal failed
                    # Only parse events generated during this particular case.
                    start = len(log.read_text())
                    inject()
                    time.sleep(0.3)
                    events = parse_wev(log.read_text()[start:])
                    passed = evaluate(events)
                    print(f'{"PASS" if passed else "FAIL"}: {label}' +
                          ('' if passed else f'; observed key events: {events}'), flush=True)
                    failed |= not passed

                def gui_cmd(events):
                    held = held_at_press(events, 't')
                    return held is not None and bool(held & {'Control_L', 'Control_R'}) and not (
                        held & {'Alt_L', 'Alt_R'})

                gui_case('LEFTALT+T -> Ctrl+t', lambda: injector.chord([codes.KEY_LEFTALT], codes.KEY_T), gui_cmd)
                gui_case('RIGHTALT -> Alt_R press/release', lambda: injector.tap(codes.KEY_RIGHTALT),
                         lambda events: pressed_and_released(events, 'Alt_R'))
                gui_case('E -> e press/release', lambda: injector.tap(codes.KEY_E),
                         lambda events: pressed_and_released(events, 'e'))
            helper = root / 'terminal.py'
            helper.write_text(TERMINAL_HELPER)
            output, ready = root / 'bytes.hex', root / 'ready'
            terminal = subprocess.Popen(['foot', '--app-id=foot-floating', '-e', sys.executable, '-I',
                                         str(helper), str(output), str(ready)],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            processes.append(terminal)
            injector.focus(terminal)
            wait_for(ready.exists, 5, 'Terminal raw-mode reader did not become ready')
            for label, inject, expected in (
                ('CAPSLOCK+C -> 03', lambda: injector.chord([codes.KEY_CAPSLOCK], codes.KEY_C), b'\x03'),
                ('E -> 65', lambda: injector.tap(codes.KEY_E), b'e'),
            ):
                start = len(output.read_text()) if output.exists() else 0
                inject()
                time.sleep(0.3)
                observed = parse_hex(output.read_text()[start:]) if output.exists() else b''
                passed = observed == expected
                print(f'{"PASS" if passed else "FAIL"}: {label}' +
                      ('' if passed else f'; observed bytes: {observed.hex()}'), flush=True)
                failed |= not passed
    except KeyboardInterrupt:
        print('FAIL: interrupted')
        failed = True
    except RuntimeError as exc:
        print(f'FAIL: {exc}')
        failed = True
    except (OSError, ValueError, subprocess.SubprocessError):
        # Never echo subprocess output or arbitrary window content.
        print('FAIL: focus, device, or test-window operation failed; injection stopped')
        failed = True
    finally:
        # Keep cleanup independent so one failure cannot prevent the remaining steps.
        if injector:
            try:
                injector.release_all()
            except OSError:
                failed = True
                print('FAIL: could not release all injected keys')
        for process in reversed(processes):
            try:
                stop(process)
            except (OSError, subprocess.SubprocessError):
                failed = True
                print('FAIL: test-window cleanup failed')
        if device:
            try:
                device.close()
            except OSError:
                failed = True
                print('FAIL: test-keyboard cleanup failed')
        if previous is not None:
            try:
                sway(f'[con_id={previous}] focus')
            except (OSError, ValueError, subprocess.SubprocessError):
                failed = True
                print('FAIL: could not restore original focus')
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
