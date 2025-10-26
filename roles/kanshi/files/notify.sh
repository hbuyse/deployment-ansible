#! /usr/bin/env sh
#
# Send notification saying which profile we are using
PROFILE="${1}"

cmdexists() {
    command -v "${1}" > /dev/null 2>&1
    return $?
}

if cmdexists notify-send; then
    notify-send \
        --urgency=low \
        --app-name=kanshi \
        --icon=/usr/share/icons/Papirus/128x128/apps/preferences-desktop-display.svg \
        "Kanshi" "Using profile '${PROFILE}'"
fi
