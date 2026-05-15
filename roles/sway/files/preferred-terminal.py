#! /usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys

TERMINALS = [
    {
        "name": os.getenv("TERMINAL", default="unknown-terminal"),
    },
    {
        "name": "ghostty",
        "env": {
            "GTK_IM_MODULE": "simple",
        },
        "run_cmd_args": "-e",
    },
    {
        "name": "alacritty",
        "run_cmd_args": "-e",
    },
    {
        "name": "foot"
        if os.getenv("XDG_SESSION_TYPE") == "wayland"
        else "unknown-terminal",
        "run_cmd_args": "",
    },
    {
        "name": "x-terminal-emulator",
    },
    {
        "name": "terminator",
        "run_cmd_args": "-e",
    },
    {
        "name": "xfce4-terminal",
        "run_cmd_args": "-e",
    },
    {
        "name": "urxvt",
        "run_cmd_args": "-e",
    },
    {
        "name": "xterm",
        "run_cmd_args": "-e",
    },
]


def find_terminal():
    for term in TERMINALS:
        cmd = shutil.which(term["name"])

        if cmd:
            term["cmd"] = cmd
            return term

    return None


def notify_missing_terminal(env):
    match f"{env['XDG_SESSION_TYPE']}-{env['XDG_SESSION_DESKTOP']}":
        case "wayland-sway" | "wayland-sway-systemd":
            cmd = [
                "swaynag",
                "-m",
                f"{os.path.basename(sys.argv[0])} could not find a terminal emulator. Please install one.",
            ]
        case "x11-i3":
            cmd = [
                "swaynag",
                "-m",
                f"{os.path.basename(sys.argv[0])} could not find a terminal emulator. Please install one.",
            ]
        case _:
            cmd = [
                "notify-send",
                "-a",
                "sway",
                f"Unknown XDG_SESSION_TYPE-XDG_SESSION_DESKTOP ({env['XDG_SESSION_TYPE']}-{env['XDG_SESSION_DESKTOP']})",
            ]

    subprocess.Popen(cmd)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e", "--command", type=str, help="command to execute", required=False
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
        required=False,
    )
    return parser.parse_args()


if __name__ == "__main__":
    # Get the environment variables
    env = dict(os.environ)
    cmd = ""

    args = parse_args()

    term = find_terminal()
    if not term:
        notify_missing_terminal(env)
        sys.exit(1)

    if "env" in term:
        env.update(term["env"])

    cmdline = [term["cmd"]]
    if args.command:
        cmdline += [term["run_cmd_args"], args.command]

    print(f"Running {cmdline}")
    subprocess.Popen(cmdline, env=env)
