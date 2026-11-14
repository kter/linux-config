"""Shared helpers for the Wi-Fi and WWAN tooltips.

インターフェース単位で、ping・パケットロス・現在の送受信速度・累計転送量・
IP アドレス・ゲートウェイを集め、Pango マークアップの表にして返す。
速度は前回の実行時のカウンタとの差分で出すので、前回値を
$XDG_RUNTIME_DIR に保存する。初回は速度が "--" になる。
"""

from __future__ import annotations

import html
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

PING_TARGET = "1.1.1.1"
PING_COUNT = 3

LABEL = "#7f849c"
VALUE = "#cdd6f4"
ACCENT = "#a6e3a1"
RULE = "#45475a"

LABEL_WIDTH = 12
VALUE_WIDTH = 15
GUTTER = "   "


@dataclass
class Stats:
    ping_ms: float | None = None
    loss_pct: float | None = None
    rx_rate: float | None = None
    tx_rate: float | None = None
    rx_total: int | None = None
    tx_total: int | None = None
    ipv4: str | None = None
    gateway: str | None = None


def _run(*cmd: str, timeout: float = 3) -> str | None:
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None


def _ip_json(*args: str) -> list:
    out = _run("ip", "-j", *args)
    try:
        return json.loads(out) if out else []
    except json.JSONDecodeError:
        return []


def default_interface() -> str | None:
    routes = _ip_json("route", "show", "default")
    routes.sort(key=lambda r: r.get("metric", 0))
    return routes[0].get("dev") if routes else None


def ipv4(ifname: str) -> str | None:
    for link in _ip_json("-4", "addr", "show", "dev", ifname):
        for addr in link.get("addr_info", []):
            if addr.get("family") == "inet":
                return addr.get("local")
    return None


def gateway(ifname: str) -> str | None:
    for route in _ip_json("route", "show", "default", "dev", ifname):
        if route.get("gateway"):
            return route["gateway"]
    return None


def counters(ifname: str) -> tuple[int, int] | None:
    stats = Path("/sys/class/net") / ifname / "statistics"
    try:
        return int((stats / "rx_bytes").read_text()), int((stats / "tx_bytes").read_text())
    except (OSError, ValueError):
        return None


def parse_ping(out: str) -> tuple[float | None, float | None]:
    loss = re.search(r"([\d.]+)% packet loss", out)
    rtt = re.search(r"= [\d.]+/([\d.]+)/", out)
    return (
        float(rtt.group(1)) if rtt else None,
        float(loss.group(1)) if loss else None,
    )


def ping(ifname: str) -> tuple[float | None, float | None]:
    # -I でインターフェースを縛り、Wi-Fi と WWAN をそれぞれの経路で測る。
    out = _run(
        "ping", "-q", "-n", "-c", str(PING_COUNT), "-i", "0.2", "-W", "1",
        "-I", ifname, PING_TARGET,
        timeout=PING_COUNT + 2,
    )
    return parse_ping(out) if out else (None, None)


def rates(ifname: str, rx: int, tx: int, now: float | None = None) -> tuple[float | None, float | None]:
    now = time.time() if now is None else now
    runtime = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
    state = runtime / f"waybar-netinfo-{ifname}.json"
    prev = None
    try:
        prev = json.loads(state.read_text())
    except (OSError, json.JSONDecodeError):
        pass
    try:
        state.write_text(json.dumps({"t": now, "rx": rx, "tx": tx}))
    except OSError:
        pass
    if not prev:
        return None, None
    dt = now - prev.get("t", now)
    drx, dtx = rx - prev.get("rx", rx), tx - prev.get("tx", tx)
    # カウンタのリセット（再接続）や時計の巻き戻りは捨てる。
    if dt <= 0 or drx < 0 or dtx < 0:
        return None, None
    return drx / dt, dtx / dt


def collect(ifname: str, with_ping: bool = True) -> Stats:
    stats = Stats(ipv4=ipv4(ifname), gateway=gateway(ifname))
    counts = counters(ifname)
    if counts:
        stats.rx_total, stats.tx_total = counts
        stats.rx_rate, stats.tx_rate = rates(ifname, *counts)
    if with_ping:
        stats.ping_ms, stats.loss_pct = ping(ifname)
    return stats


def human_bytes(n: float | None, suffix: str = "") -> str:
    if n is None:
        return "--"
    size = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1000 or unit == "TB":
            text = f"{int(size)} {unit}" if unit == "B" else f"{size:.3g} {unit}"
            return text + suffix
        size /= 1000
    return f"{n} B"


def activity(stats: Stats) -> str:
    total = (stats.rx_rate or 0) + (stats.tx_rate or 0)
    if stats.rx_rate is None:
        return "LISTENING"
    if total >= 1_000_000:
        return "HAULING BYTES"
    if total >= 10_000:
        return "TRAFFIC FLOWING"
    if total >= 100:
        return "TRICKLING"
    return "IDLE"


def stat_rows(stats: Stats) -> list[tuple[str, str, str, str]]:
    def fmt(value, spec):
        return "--" if value is None else spec.format(value)

    return [
        ("Ping", fmt(stats.ping_ms, "{:.0f} ms"), "Packet Loss", fmt(stats.loss_pct, "{:.0f}%")),
        ("Receiving", human_bytes(stats.rx_rate, "/s"), "Sending", human_bytes(stats.tx_rate, "/s")),
        ("Downloaded", human_bytes(stats.rx_total), "Uploaded", human_bytes(stats.tx_total)),
        ("IP Address", stats.ipv4 or "--", "Gateway", stats.gateway or "--"),
    ]


def _cell(label: str, value: str) -> str:
    return (
        f'<span foreground="{LABEL}">{html.escape(label.ljust(LABEL_WIDTH))}</span>'
        f'<span foreground="{VALUE}">{html.escape(value.rjust(VALUE_WIDTH))}</span>'
    )


def render(icon: str, title: str, subtitle: str, rows: list[tuple[str, str, str, str]],
           footer: list[str] | None = None) -> str:
    width = 2 * (LABEL_WIDTH + VALUE_WIDTH) + len(GUTTER)
    lines = [
        f'<span size="x-large" foreground="{VALUE}">{html.escape(icon)}</span>  '
        f'<span size="large" weight="bold" foreground="{VALUE}">{html.escape(title)}</span>',
        f'<span font_family="monospace" size="small" letter_spacing="2048" '
        f'foreground="{ACCENT}">{html.escape(subtitle)}</span>',
        "",
    ]
    body = [_cell(a, b) + GUTTER + _cell(c, d) for a, b, c, d in rows]
    body.append(f'<span foreground="{RULE}">{"─" * width}</span>')
    for line in footer or []:
        body.append(f'<span foreground="{LABEL}">{html.escape(line)}</span>')
    lines.append('<span font_family="monospace">' + "\n".join(body) + "</span>")
    return "\n".join(lines)
