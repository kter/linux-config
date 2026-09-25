#!/bin/sh
# クイックメモ（macOS の Stickies 代わり）の表示/非表示を切り替える。
# ウィンドウが無ければ（初回や nvim を :q で閉じた後）起動してから表示する。
APP_ID=local.quickmemo
MEMO="$HOME/notes/memo.md"

exists() {
    swaymsg -t get_tree | jq -e --arg id "$APP_ID" '.. | objects | select(.app_id? == $id)' >/dev/null
}

if ! exists; then
    mkdir -p "$(dirname "$MEMO")"
    ghostty --class="$APP_ID" -e nvim "$MEMO" >/dev/null 2>&1 &
    # for_window で scratchpad へ送られるまで待つ（最大5秒）
    i=0
    until exists || [ "$i" -ge 50 ]; do sleep 0.1; i=$((i + 1)); done
fi

swaymsg "[app_id=\"$APP_ID\"] scratchpad show" >/dev/null
