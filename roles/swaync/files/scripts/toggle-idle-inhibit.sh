#! /usr/bin/env bash

if [ -f "$XDG_RUNTIME_DIR/swaync-idle.pid" ] && kill -0 "$(cat "$XDG_RUNTIME_DIR/swaync-idle.pid")" 2> /dev/null; then
    kill "$(cat "$XDG_RUNTIME_DIR/swaync-idle.pid")"
    rm -f "$XDG_RUNTIME_DIR/swaync-idle.pid"
else
    systemd-inhibit --why="User request via swaync" --what=sleep:handle-lid-switch:idle sh -c "echo $$ > \"$XDG_RUNTIME_DIR/swaync-idle.pid\"; while true; do sleep 3600; done" &
fi
