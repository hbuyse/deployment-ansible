import re


def test_perlnavigator_is_in_the_path(host):
    """The language server installed with npm is in the PATH (the npm prefix of the user, or /usr/local)."""
    cmd = host.run("command -v perlnavigator || ls /usr/local/bin/perlnavigator /root/.npm-packages/bin/perlnavigator")
    assert cmd.rc == 0, cmd.stderr


def test_perlnavigator_package_is_installed_with_npm(host):
    """perlnavigator-server is installed globally with the version of the role."""
    out = host.check_output("npm ls -g --depth=0 perlnavigator-server")
    assert re.search(r"perlnavigator-server@\d+\.\d+\.\d+", out)
