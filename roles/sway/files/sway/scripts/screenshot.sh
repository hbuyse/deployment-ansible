#! /usr/bin/env bash

SCREENSHOTS_DIR="${HOME}/Pictures/Screenshots"
SCREENSHOTS_ICON="/usr/share/icons/Papirus/symbolic/apps/accessories-screenshot-symbolic.svg"

check() {
    local missing=()
    for i in grim slurp jq; do
        if ! command -v "$i" > /dev/null; then
            missing+=("$i")
        fi
    done

    if [ "${XDG_CURRENT_DESKTOP}" = sway ]; then
        if ! command -v "swaymsg" > /dev/null; then
            missing+=("swaymsg")
        fi
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        notify-send --urgency=critical --app-name="Screenshots" --icon="${SCREENSHOTS_ICON}" \
            "Screenshots" "Missing programs: ${missing[*]}"
        exit 1
    fi
}

check

# Create the folder
mkdir -p "${SCREENSHOTS_DIR}"
filepath="${SCREENSHOTS_DIR}/$(date +'%Y%m%d_%H%M%S').png"

case "$1" in
"all")
    grim "${filepath}"
    ;;
"screen")
    if ! slurp -o | grim -g - "${filepath}"; then
        exit 0 # Cancelled
    fi
    ;;
"window")
    swaymsg -t get_tree | jq -r '.. | (.nodes? // empty)[] | select(.focused) | "\(.rect.x),\(.rect.y) \(.rect.width)x\(.rect.height)"' | grim -g - "${filepath}"
    ;;
"area")
    if ! slurp | grim -g - "${filepath}"; then
        exit 0 # Cancelled
    fi
    ;;
*)
    notify-send --urgency=critical --app-name="Screenshots" --icon="${SCREENSHOTS_ICON}" \
        "Screenshots" "Unknown command: '$1'"
    exit 2
    ;;
esac

notify-send --app-name="Screenshots" --icon="${SCREENSHOTS_ICON}" \
    "Screenshots" "Stored at ${filepath}"
