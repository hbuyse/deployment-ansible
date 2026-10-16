import re

APPLICATIONS = "/root/.local/share/applications"


def test_chromium_package(host):
    """Chromium runs the web applications."""
    assert host.package("chromium").is_installed


def test_desktop_files(host):
    """One desktop file per web application, with its name, URL and categories."""
    expected = {
        "discord": ("Discord", "https://discord.com", "Network;InstantMessaging"),
        "spotify": ("Spotify", "https://open.spotify.com", "AudioVideo;Audio;Player"),
        "youtube": ("Youtube", "https://youtube.com", "AudioVideo;Audio;Video;Player"),
    }
    for key, (title, url, categories) in expected.items():
        desktop = host.file(f"{APPLICATIONS}/com.{key}.webapp.desktop")
        assert desktop.is_file, key
        assert oct(desktop.mode) == "0o644", key
        content = desktop.content_string
        assert f"Name={title} WebApp" in content
        assert f"Exec=chromium --app={url}" in content
        assert f"Categories={categories}" in content
        assert re.search(r"^Type=Application$", content, flags=re.MULTILINE)
