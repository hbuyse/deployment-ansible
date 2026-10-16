import re


def test_jq_package(host):
    """jq is installed from the package manager."""
    assert host.package("jq").is_installed


def test_jq_runs(host):
    """jq reports its version."""
    cmd = host.run("jq --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.fullmatch(r"jq-\d+\.\d+(\.\d+)?", cmd.stdout.strip())


def test_jq_filters_json(host):
    """jq extracts a field from a JSON document."""
    assert host.check_output("echo '{\"name\": \"molecule\"}' | jq -r .name") == "molecule"
