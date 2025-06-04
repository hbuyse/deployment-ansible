#! /usr/bin/env python3

import json
import socket
import sys


def send(cmd: str = None):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect("/run/user/1000/ncspot/ncspot.sock")
        if cmd:
            s.send(cmd.encode())

        data = s.recv(4096)

    # # Exit early (we need to receive data in order for ncspot to change the status)
    # if cmd:
    #     return

    data = json.loads(data.decode().strip())
    artists = data["playable"]["artists"][0]
    mode = "unknown"

    if "Playing" in data["mode"]:
        mode = "play"
    elif "Paused" in data["mode"]:
        mode = "pause"
    elif "Stopped" in data["mode"]:
        mode = "stop"

    tooltip = [
        "<b>Title:</b>   " + data["playable"]["title"],
        "<b>Artists:</b> " + artists,
        "<b>Album:</b>   " + data["playable"]["album"],
    ]

    output = {
        "text": f"{artists} / {data['playable']['title']}".replace("&", "&amp;"),
        "class": mode,
        "alt": mode,
        "tooltip": "\n".join(tooltip).replace("&", "&amp;"),
    }

    print(json.dumps(output, ensure_ascii=True))


if __name__ == "__main__":
    if len(sys.argv) != 1:
        send(sys.argv[1] + "\n")  # Add newline to force the data reception by ncspot
    else:
        send()
