#!/usr/bin/env sh

send_signal() {
    pkill -x -SIGRTMIN+6 'waybar'
}

case "$1" in
'off')
    systemctl --user stop wlsunset
    send_signal
    ;;
'on')
    systemctl --user start wlsunset
    send_signal
    ;;
'toggle')
    if systemctl --user is-active --quiet wlsunset.service; then
        systemctl --user stop wlsunset.service
    else
        systemctl --user start wlsunset.service
    fi
    send_signal
    ;;
'check')
    command -v wlsunset
    exit $?
    ;;
esac

#Returns a string for Waybar
if systemctl --user --quiet is-active wlsunset; then
    class="activated"
    text="Location-based gamma correction"
else
    class="deactivated"
    text="No gamma correction"
fi

printf '{"alt":"%s", "class": "%s", "tooltip":"%s"}\n' "$class" "$class" "$text"
