from pathlib import Path

ROLE_DIR = Path(__file__).resolve().parents[3]


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_ppa_and_setuid_on_ubuntu(host):
    """Ubuntu uses the Wireshark PPA and lets non-privileged users capture."""
    if _os_id(host) == "arch":
        return
    assert "wireshark-dev/stable/ubuntu" in host.file("/etc/apt/sources.list.d/wireshark.sources").content_string
    assert "* wireshark-common/install-setuid: true" in host.check_output("debconf-show wireshark-common")


def test_packages(host):
    """Wireshark is installed."""
    names = ["wireshark-cli", "wireshark-qt"] if _os_id(host) == "arch" else ["wireshark"]
    for name in names:
        assert host.package(name).is_installed, name


def test_dumpcap_is_restricted_to_the_wireshark_group(host):
    """Capturing is allowed to the members of the wireshark group only (file capabilities cannot run in a container)."""
    dumpcap = host.file("/usr/bin/dumpcap")
    assert dumpcap.exists
    assert dumpcap.group == "wireshark"
    assert dumpcap.mode & 0o001 == 0


def test_user_is_in_the_wireshark_group(host):
    """The user can capture packets."""
    assert "wireshark" in host.user("root").groups


def test_preferences(host):
    """The preferences of the role are deployed."""
    preferences = host.file("/root/.config/wireshark/preferences")
    assert preferences.is_file
    assert preferences.content_string == (ROLE_DIR / "files" / "preferences").read_text()
