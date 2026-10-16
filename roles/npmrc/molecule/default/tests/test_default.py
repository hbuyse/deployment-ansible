def test_npmrc_file(host):
    """~/.npmrc sets the prefix of the global npm packages, with no leftover Jinja."""
    npmrc = host.file("/root/.npmrc")
    assert npmrc.is_file
    assert oct(npmrc.mode) == "0o644"
    assert npmrc.content_string.strip() == 'prefix="/root/.npm-packages"'


def test_npm_packages_directory(host):
    """The global packages directory exists."""
    packages = host.file("/root/.npm-packages")
    assert packages.is_directory
    assert oct(packages.mode) == "0o755"
