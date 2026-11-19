#!/bin/sh
# Restart Toshy and clear modifier/key state left behind in Sway.
status=0
systemctl --user restart toshy-wlroots-dbus.service toshy-config.service || status=1
ready=0
i=0
while [ "$i" -lt 10 ]; do
    if systemctl --user is-active --quiet toshy-config.service &&
        swaymsg -t get_inputs | jq -e 'any(.[]; .type == "keyboard" and (.identifier | contains("XWayKeyz")))' >/dev/null; then
        ready=1
        break
    fi
    sleep 1
    i=$((i + 1))
done
if [ "$ready" -eq 1 ]; then
    echo 'Toshy active; waiting for the keyboard grab to settle' >&2
    sleep 1
else
    echo 'Toshy did not become ready within 10 seconds; attempting key reset anyway' >&2
    status=1
fi
# JSON escaping also protects quotes/backslashes inside Sway input identifiers.
commands=$(swaymsg -t get_inputs | jq -er '.[] | select(.type == "keyboard") | select(.identifier | startswith("0:0:wlr_virtual_keyboard") | not) | "input \(.identifier | tojson) events"') || status=1
while IFS= read -r command; do
    [ -n "$command" ] || continue
    echo "Resetting keyboard: $command" >&2
    swaymsg "$command disabled" >/dev/null || status=1
    attempt=1
    while ! swaymsg "$command enabled" >/dev/null 2>&1; do
        if [ "$attempt" -eq 3 ]; then
            echo "Failed to re-enable keyboard after 3 attempts: $command" >&2
            status=1
            break
        fi
        sleep 0.2
        attempt=$((attempt + 1))
    done
done <<EOF
$commands
EOF
exit "$status"
