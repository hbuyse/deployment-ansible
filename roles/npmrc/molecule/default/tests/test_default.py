def test_npmrc_file_created(host):
    """~/.npmrc is rendered with the correct mode."""
    npmrc = host.file("/root/.npmrc")
    assert npmrc.exists
    assert npmrc.is_file
    assert npmrc.mode == 0o644


def test_npmrc_prefix_content(host):
    """~/.npmrc points its prefix at ~/.npm-packages."""
    npmrc = host.file("/root/.npmrc")
    assert npmrc.content_string.strip() == 'prefix="/root/.npm-packages"'


def test_npm_packages_directory_created(host):
    """~/.npm-packages directory exists with the correct mode."""
    packages_dir = host.file("/root/.npm-packages")
    assert packages_dir.exists
    assert packages_dir.is_directory
    assert packages_dir.mode == 0o755
