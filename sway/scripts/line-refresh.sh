#!/bin/sh
# Bottles版LINE（Wine）の表示崩れを直す。X11 窓の高さを 1px 縮めて戻し（幅の変更では描き直されない）、Wine に全体を描き直させる。
for w in $(xdotool search --class steam_proton); do
    [ "$(xdotool getwindowname "$w")" = LINE ] || continue
    eval "$(xdotool getwindowgeometry --shell "$w")"
    xdotool windowsize "$w" "$WIDTH" $((HEIGHT - 1))
    sleep 0.1
    xdotool windowsize "$w" "$WIDTH" "$HEIGHT"
done
