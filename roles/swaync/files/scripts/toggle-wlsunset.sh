#! /usr/bin/env bash

if systemctl --user is-active -q wlsunset; then
    systemctl --user stop wlsunset
else
    systemctl --user start wlsunset
fi
