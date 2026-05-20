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

# RAPL 2-sample power measurement (~1s)
s1=$(rapl-read 2>/dev/null)
sleep 1
s2=$(rapl-read 2>/dev/null)

set -- $s1; pkg1=$1; core1=$2; unc1=$3
set -- $s2; pkg2=$1; core2=$2; unc2=$3

awk -v uv="$uv" -v ua="$ua" \
    -v pkg1="$pkg1" -v core1="$core1" -v unc1="$unc1" \
    -v pkg2="$pkg2" -v core2="$core2" -v unc2="$unc2" '
BEGIN {
    v      = uv / 1e6;
    a_max  = ua / 1e6;
    w_max  = v * a_max;
    pkg_w  = (pkg2  - pkg1)  / 1e6;
    core_w = (core2 - core1) / 1e6;
    unc_w  = (unc2  - unc1)  / 1e6;

    printf "{\"text\":\" %.1fW\",", pkg_w;
    printf "\"tooltip\":\"USB-C 給電\\n電圧: %.0f V\\nPDO 上限: %.0f V / %.1f A / %.0f W\\n\\nシステム消費 (RAPL)\\nPackage : %.1f W\\nCore    : %.1f W\\nUncore  : %.1f W\",", v, v, a_max, w_max, pkg_w, core_w, unc_w;
    printf "\"class\":\"connected\"}\n";
}'
