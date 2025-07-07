#! /usr/bin/env python3

import argparse
import json
import shutil
from tabulate import tabulate

KiB = 1024
MiB = 1024 * KiB
GiB = 1024 * MiB


def main(args):
    tooltip: list[tuple[str, str, str | int]] = []
    for path in args.paths:
        disk_usage = shutil.disk_usage(path)
        percentage = int(disk_usage.used * 100 / disk_usage.total)
        tooltip.append(
            (
                f"{path}",
                f"{float(disk_usage.used / GiB):.1f} GiB used out of {float(disk_usage.total / GiB):.1f} GiB",
                f"{percentage}%",
            )
        )

    main_path = "/home"
    if args.main:
        main_path = args.main
    main = shutil.disk_usage(main_path)
    percentage = int(main.used * 100 / main.total)

    _class = "normal"
    if percentage >= 70:
        _class = "warning"
    if percentage >= 90:
        _class = "critical"

    return json.dumps(
        {
            "text": f"<span color='#83a598'>{main_path}</span>: {int(percentage)}%",
            "tooltip": tabulate(
                tooltip, tablefmt="outline", colalign=("left", "left", "right")
            ),
            "percentage": percentage,
            "class": _class,
        }
    )


def parse_args():
    parser = argparse.ArgumentParser(prog="disk_aio.py", usage="%(prog)s [options]")
    parser.add_argument("--main", help="Main path to display")
    parser.add_argument("paths", nargs="+", help="Paths to check")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    data = main(args)
    print(data)
