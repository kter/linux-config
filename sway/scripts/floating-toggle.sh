#!/bin/sh
# floating toggle の代わり。Wine（Bottles版LINE, class=steam_proton）はタイル時のリサイズ指示を無視するので、
# フロートに戻した直後に sway の枠を Wine 側の実サイズに合わせ、右端・下端が切れるのを防ぐ。
# 引数に con_id を渡すとそのウィンドウを対象にする（省略時はフォーカス中）。
CRITERIA=${1:+"[con_id=$1] "}
swaymsg "${CRITERIA}floating toggle" >/dev/null
sleep 0.1

swaymsg -t get_tree | jq -r --arg id "${1:-}" '
    .. | objects | select(.type? == "floating_con")
    | select(if $id == "" then .focused else (.id | tostring) == $id end)
    | select(.window_properties.class? == "steam_proton")
    | "\(.id) \(.geometry.width) \(.geometry.height)"' |
while read -r id w h; do
    swaymsg "[con_id=$id] resize set $w px $h px" >/dev/null
    # 戻した直後は描画バッファの高さがずれて表示が崩れるので描き直させる
    ~/.config/sway/scripts/line-refresh.sh
done
