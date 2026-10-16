import re

import pytest


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_golang_package(host):
    """The Go toolchain is installed from the package manager (go on Arch, golang elsewhere)."""
    name = "go" if _os_id(host) == "arch" else "golang"
    assert host.package(name).is_installed


def test_go_runs(host):
    """go reports its version."""
    cmd = host.run("go version")
    assert cmd.rc == 0, cmd.stderr
    assert re.match(r"go version go1\.\d+", cmd.stdout)


def test_go_compiles_a_program(host):
    """The toolchain is complete enough to build and run a program."""
    host.run("mkdir -p /tmp/hello")
    host.run(
        "printf 'package main\\nimport \"fmt\"\\nfunc main() { fmt.Println(\"hello\") }\\n' > /tmp/hello/main.go"
    )
    cmd = host.run("cd /tmp/hello && go run main.go")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.strip() == "hello"
