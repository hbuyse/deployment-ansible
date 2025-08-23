#! /usr/bin/env bash

function enable {
    swaync-client --dnd-on
    systemctl --user stop swayidle
}

function disable {
    swaync-client --dnd-off
    systemctl --user start swayidle
}

case $1 in
enable)
    enable
    ;;
disable)
    disable
    ;;
*) ;;
esac
