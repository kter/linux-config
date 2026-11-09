"""Regression checks for the battery tooltip's history selection and chart."""
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'battery'
loader = importlib.machinery.SourceFileLoader('battery', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
battery = importlib.util.module_from_spec(spec)
loader.exec_module(battery)


class BatteryHistoryTests(unittest.TestCase):
    def test_current_sample_on_last_column_boundary_is_included(self):
        end = battery.HOURS * 3600
        slots = battery.charge_slots([(0, 70, 'discharging'), (end, 65, 'discharging')], 0)
        self.assertEqual(slots[-1][0], 65)

    def test_real_zero_charge_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'history-charge-model-70-1784.dat').write_text('100\t0\tdischarging\n')
            with patch.object(battery, 'UPOWER_HISTORY', root):
                self.assertEqual(battery.read_history('charge', 'model-70-1784', 0), [(100, 0, 'discharging')])

    def test_changed_upower_id_uses_recent_history_for_same_serial(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / 'history-charge-model-70-1784.dat'
            recent = root / 'history-charge-model-1784.dat'
            other = root / 'history-charge-mouse-9999.dat'
            for path, content, modified in (
                (old, '100\t29\tdischarging\n', 100),
                (recent, '200\t65\tdischarging\n', 200),
                (other, '300\t99\tdischarging\n', 300),
            ):
                path.write_text(content)
                os.utime(path, (modified, modified))
            with patch.object(battery, 'UPOWER_HISTORY', root):
                points = battery.read_history('charge', 'model-70-1784', 0)
                slots = battery.charge_slots(points, 200)
            self.assertEqual(slots[0][0], 65, 'chart must use current history, not stale exact-ID history')

    def test_real_current_history_is_not_superseded_by_stale_exact_id(self):
        bat = battery.find_battery()
        if bat is None:
            self.skipTest('no battery')
        identity = battery.history_id(bat)
        selected = battery.history_file('charge', identity)
        related = list(battery.UPOWER_HISTORY.glob(f'history-charge-*-{identity.rsplit("-", 1)[-1]}.dat')) if identity else []
        if not related:
            self.skipTest('no related history files')
        self.assertGreaterEqual(selected.stat().st_mtime, max(p.stat().st_mtime for p in related))

    def test_unknown_zero_marker_is_not_plotted_as_empty_battery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'history-charge-model-70-1784.dat').write_text(
                '100\t70\tdischarging\n200\t0\tunknown\n300\t65\tdischarging\n'
            )
            with patch.object(battery, 'UPOWER_HISTORY', root):
                points = battery.read_history('charge', 'model-70-1784', 0)
            self.assertEqual([p[1] for p in points], [70, 65])


if __name__ == '__main__':
    unittest.main()
