def test_repository(host):
    """The Spotify apt repository is configured with its signing key."""
    source = host.file("/etc/apt/sources.list.d/spotify.sources")
    assert source.is_file
    assert "URIs: https://repository.spotify.com" in source.content_string
    assert "Components: non-free" in source.content_string
    assert "Signed-By:" in source.content_string


def test_spotify_package(host):
    """spotify-client is installed from that repository."""
    assert host.package("spotify-client").is_installed
    assert "repository.spotify.com" in host.check_output("apt-cache policy spotify-client")


def test_spotify_command(host):
    """The spotify command is installed."""
    assert host.exists("spotify")
