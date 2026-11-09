#!/bin/sh
# IMEが効かない瞬間の状態を記録する（LINE/Wine の Ctrl+Space 不具合の切り分け用）
log=~/.local/state/ime-snapshot.log
mkdir -p "${log%/*}"
{
  echo "===== $(date '+%F %T')"
  swaymsg -t get_tree | python3 -c '
import json,sys
def w(n):
    if n.get("focused"): print("focused:", n.get("app_id") or n.get("window_properties",{}).get("class"), "|", n.get("name"), "|", n.get("shell"))
    for c in n.get("nodes",[])+n.get("floating_nodes",[]): w(c)
w(json.load(sys.stdin))'
  echo "fcitx5-remote state: $(fcitx5-remote) / im: $(fcitx5-remote -n)"
  dbus-send --session --print-reply --dest=org.fcitx.Fcitx5 /controller org.fcitx.Fcitx.Controller1.DebugInfo
} >>"$log" 2>&1
notify-send -t 1500 "IME snapshot saved" 2>/dev/null
