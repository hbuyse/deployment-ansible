import json


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_prettier_runs(host):
    """prettier reports its version."""
    cmd = host.run("prettier --version")
    assert cmd.rc == 0, cmd.stderr
    assert cmd.stdout.strip()[0].isdigit()


def test_prettier_formats_json(host):
    """prettier reformats a compact JSON document."""
    cmd = host.run("echo '{\"a\":[1,2]}' | prettier --parser json")
    assert cmd.rc == 0, cmd.stderr
    assert json.loads(cmd.stdout) == {"a": [1, 2]}
    assert cmd.stdout.strip() == '{ "a": [1, 2] }'


def test_installation_method(host):
    """Arch uses the package, the others the npm packages of the role."""
    if _os_id(host) == "arch":
        assert host.package("prettier").is_installed
    else:
        out = host.check_output("npm ls -g --depth=0")
        assert "prettier@" in out
        assert "prettier-plugin-toml@" in out
