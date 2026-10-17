def test_perlnavigator_binary(host):
    """The binary is downloaded in ~/.local/bin and is executable."""
    binary = host.file("/root/.local/bin/perlnavigator")
    assert binary.is_file
    assert oct(binary.mode) == "0o755"


def test_perlnavigator_is_a_native_executable(host):
    """The file is an ELF executable, not an HTML error page."""
    magic = host.check_output("head -c 4 /root/.local/bin/perlnavigator | od -An -c | tr -d ' '")
    assert magic == "177ELF"


def test_temporary_directory_is_removed(host):
    """The handler removes the directory where the zip was unpacked."""
    assert host.check_output("ls -d /tmp/*perlnavigator* 2>/dev/null || true") == ""
