
PACKAGES = {
    "debian": ["qemu-system-x86", "virt-manager", "virtinst", "libvirt-clients", "bridge-utils", "libvirt-daemon-system"],
    "ubuntu": ["qemu-system-x86", "virt-manager", "virtinst", "libvirt-clients", "bridge-utils", "libvirt-daemon-system"],
    "arch": ["libvirt", "virt-manager"],
    "fedora": ["qemu-kvm", "libvirt-daemon", "virt-install"],
}


def test_packages(host):
    """The virtualization packages of the distribution are installed."""
    os_id = host.check_output(". /etc/os-release && echo $ID").strip()
    for name in PACKAGES[os_id]:
        assert host.package(name).is_installed, name


def test_user_is_in_the_libvirt_group(host):
    """The user can manage the virtual machines."""
    assert "libvirt" in host.user("root").groups


def test_libvirtd_service(host):
    """libvirtd is enabled and running."""
    service = host.service("libvirtd")
    assert service.is_enabled
    assert service.is_running


def test_virsh_answers(host):
    """virsh reaches the daemon."""
    cmd = host.run("virsh --connect qemu:///system list --all")
    assert cmd.rc == 0, cmd.stderr
