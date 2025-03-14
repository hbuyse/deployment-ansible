#!/bin/bash

# TODO: error handling

# From: https://people.debian.org/~mpitt/systemd.conf-2016-graphical-session.pdf

# robustness: if the previous graphical session left some failed units,
# reset them so that they don't break this startup
for unit in $(systemctl --user --no-legend --state=failed --plain list-units | cut -f1 -d' '); do
    partof="$(systemctl --user show -p PartOf --value "$unit")"
    for target in sway-session.target wayland-session.target graphical-session.target; do
        if [ "$partof" = "$target" ]; then
            systemctl --user reset-failed "$unit"
            break
        fi
    done
done

# /etc/profile contains a lot of important environment variables
source /etc/profile

export XDG_CURRENT_DESKTOP=sway

# save environment variables that will be added to systemd
new_env=$(systemctl --user show-environment | cut -d'=' -f 1 | sort | comm -13 - <(env | cut -d'=' -f 1 | sort))

# import environment variables from the login manager
systemctl --user import-environment $new_env

# then start the service
if grep -qE "nvidia|fglrx" /proc/modules; then
    export WLR_NO_HARDWARE_CURSORS=1
    systemctl --wait --user start sway-unsupported-gpu.service
else
    systemctl --wait --user start sway.service
fi

# cleanup environment
systemctl --user unset-environment $new_env
