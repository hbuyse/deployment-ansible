import re


def _os_id(host):
    return host.check_output(". /etc/os-release && echo $ID").strip()


def test_ppa_on_ubuntu(host):
    """Ubuntu uses the LibreOffice PPA."""
    if _os_id(host) == "arch":
        return
    source = host.file("/etc/apt/sources.list.d/libreoffice.sources")
    assert source.is_file
    assert "ppa.launchpadcontent.net/libreoffice/ppa/ubuntu" in source.content_string
    assert "launchpadcontent.net" in host.check_output("apt-cache policy libreoffice")


def test_libreoffice_package(host):
    """LibreOffice is installed (the fresh branch on Arch)."""
    assert host.package("libreoffice-fresh" if _os_id(host) == "arch" else "libreoffice").is_installed


def test_libreoffice_runs(host):
    """soffice reports its version."""
    cmd = host.run("soffice --version")
    assert cmd.rc == 0, cmd.stderr
    assert re.search(r"LibreOffice \d+\.\d+", cmd.stdout)
