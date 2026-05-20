#!/bin/sh
psy=$(ls -d /sys/class/power_supply/ucsi-source-psy-* 2>/dev/null | head -n1)

disconnected() {
    printf '{"text":" —","tooltip":"USB-C: 未接続","class":"disconnected"}\n'
    exit 0
}

[ -n "$psy" ] || disconnected
online=$(cat "$psy/online" 2>/dev/null)
uv=$(cat "$psy/voltage_now" 2>/dev/null)
ua=$(cat "$psy/current_now" 2>/dev/null)
[ "$online" = "1" ] && [ -n "$uv" ] && [ "$uv" != "0" ] || disconnected

awk -v uv="$uv" -v ua="$ua" 'BEGIN {
    v = uv / 1e6; a = ua / 1e6; w = v * a;
    printf "{\"text\":\" %.1fV %.2fA %.0fW\",", v, a, w;
    printf "\"tooltip\":\"USB-C 給電\\n電圧: %.2f V\\n電流: %.2f A\\n電力: %.1f W\",", v, a, w;
    printf "\"class\":\"connected\"}\n";
}'
