#! /usr/bin/env bash
HOSTNAME="$(hostname -s | tr '[:upper:]' '[:lower:]')"
CTL=pactl

if ! command -v ${CTL} > /dev/null; then
    echo "${CTL}: not found. Exiting..."
    exit 1
fi

# Sinks are outputs (audio goes there)
declare -A HEADPHONES_SINK_LIST=(
    ["alsa_output.usb-Kingston_HyperX_Virtual_Surround_Sound_00000000-00.analog-stereo"]="true,analog-output,"
    ["alsa_output.pci-0000_00_1f.3.analog-stereo"]="false,analog-output-headphones,mute"
)

# Sources are inputs (audio comes from there).
declare -A HEADPHONES_SOURCE_LIST=(
    ["alsa_input.usb-Kingston_HyperX_Virtual_Surround_Sound_00000000-00.analog-stereo"]="true,analog-input-headset-mic,,loopback"
    ["alsa_input.pci-0000_00_1f.3.analog-stereo"]="false,analog-input-headset-mic,mute,"
)

set_sinks() {
    local first_found=0

    for key in "${!HEADPHONES_SINK_LIST[@]}"; do
        # If not found, continue to next sink
        if ! pactl list sinks short | grep -q "$key"; then
            continue
        fi

        # Set the type of sink
        type=$(echo "${HEADPHONES_SINK_LIST[$key]}" | cut -d',' -f2)
        pactl set-sink-port "$key" "$type"

        # Set to mute if needed
        if [[ "$(echo "${HEADPHONES_SINK_LIST[$key]}" | cut -d',' -f3)" == "mute" ]]; then
            pactl set-sink-mute "$key" true
        fi

        if [ $first_found -eq 0 ]; then
            pactl set-default-sink "$key"
            first_found=1
        fi
    done
}

set_sources() {
    local first_found=0

    for key in "${!HEADPHONES_SOURCE_LIST[@]}"; do
        # If not found, continue to next source
        if ! pactl list sources short | grep -q "$key"; then
            continue
        fi

        if [ $first_found -eq 0 ] && [[ "$(echo "${HEADPHONES_SOURCE_LIST[$key]}" | cut -d',' -f1)" == "true" ]]; then
            pactl set-default-source "$key"
            first_found=1
        fi

        # Set the type of source
        type=$(echo "${HEADPHONES_SOURCE_LIST[$key]}" | cut -d',' -f2)
        pactl set-source-port "$key" "$type"

        # Set to mute if needed
        if [[ "$(echo "${HEADPHONES_SOURCE_LIST[$key]}" | cut -d',' -f3)" == "mute" ]]; then
            pactl set-source-mute "$key" true
        fi

    done
}

set_sinks
set_sources

# vim: set ts=4 sw=4 tw=0 et :
