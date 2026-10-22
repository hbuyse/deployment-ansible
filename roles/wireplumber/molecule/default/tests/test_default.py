from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]
SYSTEMCTL = "XDG_RUNTIME_DIR=/run/user/2000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/2000/bus systemctl --user"
CONFIG = "/home/tester/.config/wireplumber"


PACKAGES = {
    "debian": ["pipewire", "wireplumber", "pipewire-audio-client-libraries", "pulseaudio-utils"],
    "ubuntu": ["pipewire", "wireplumber", "pipewire-audio-client-libraries", "pulseaudio-utils"],
    "arch": ["pipewire", "pipewire-pulse", "pipewire-alsa", "pipewire-jack", "wireplumber"],
    "fedora": ["pipewire", "pipewire-pulseaudio", "pipewire-utils", "pulseaudio-utils", "wireplumber"],
}


def test_packages(host):
    """The PipeWire and WirePlumber packages of the distribution are installed."""
    os_id = host.check_output(". /etc/os-release && echo $ID").strip()
    for name in PACKAGES[os_id]:
        assert host.package(name).is_installed, name


def test_pipewire_media_session_is_removed(host):
    """The old session manager is not installed."""
    assert not host.package("pipewire-media-session").is_installed


def test_configuration_files(host):
    """Every configuration file of the role is deployed in ~/.config/wireplumber."""
    files = [path for path in (ROLE_DIR / "files").rglob("*") if path.is_file()]
    assert files
    for source in files:
        deployed = host.file(f"{CONFIG}/{source.relative_to(ROLE_DIR / 'files')}")
        assert deployed.is_file, source
        assert deployed.content_string == source.read_text(), source


def test_services_are_enabled_and_running(host):
    """The PipeWire services are enabled and started for the user."""
    for name in ("pipewire", "pipewire-pulse", "wireplumber"):
        cmd = host.run(f"{SYSTEMCTL} is-enabled {name}")
        assert cmd.stdout.strip() in ("enabled", "static", "alias"), (name, cmd.stdout, cmd.stderr)
        assert host.run(f"{SYSTEMCTL} is-active {name}").stdout.strip() == "active", name
