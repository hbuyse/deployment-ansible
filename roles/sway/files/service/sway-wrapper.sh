#!/bin/sh

# # robustness: if the previous graphical session left some failed units,
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

# Session
export XDG_SESSION_TYPE=wayland
export XDG_SESSION_DESKTOP=sway
export XDG_CURRENT_DESKTOP=sway

set -a

# Import openSUSEway environment variables
if [ -f /etc/sway/env ]; then
    . /etc/sway/env
fi

# Import environment.d variables by calling the systemd generator
if [ -f /usr/lib/systemd/user-environment-generators/30-systemd-environment-d-generator ]; then
    eval "$(/usr/lib/systemd/user-environment-generators/30-systemd-environment-d-generator)"
fi
set +a

# Set dependencies to run with proprietary drivers
if grep -qE "nvidia|fglrx" /proc/modules; then
    export WLR_NO_HARDWARE_CURSORS=1
    unsupported_gpu="--unsupported-gpu"
else
    unsupported_gpu=""
fi

# Start the Sway session
systemctl --user start sway-session.target

systemd-cat --identifier=sway sway $unsupported_gpu $@
