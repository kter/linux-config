#!/bin/sh
# swayidle の timeout から呼ばれ、AC 電源に繋がっていないときだけサスペンドする。
# 判定は idle 到達の瞬間のみ。AC 接続中に timeout を迎えてから抜いても、
# 一度操作して再び無操作になるまではサスペンドしない。
for ps in /sys/class/power_supply/*; do
    [ "$(cat "$ps/type" 2>/dev/null)" = Mains ] || continue
    [ "$(cat "$ps/online" 2>/dev/null)" = 1 ] && exit 0
done

exec systemctl suspend
