import re


def test_perlnavigator_is_linked_in_the_binary_directory(host):
    """~/.local/bin/perlnavigator points to the binary of the release."""
    link = host.file("/root/.local/bin/perlnavigator")
    assert link.is_symlink
    assert re.fullmatch(r"/root/\.local/share/perlnavigator/[^/]+/perlnavigator-linux-[^/]+/perlnavigator", link.linked_to)


def test_perlnavigator_binary(host):
    """The binary of the release is executable."""
    binary = host.file(host.file("/root/.local/bin/perlnavigator").linked_to)
    assert binary.is_file
    assert oct(binary.mode) == "0o755"


def test_perlnavigator_is_a_native_executable(host):
    """The file is an ELF executable, not an HTML error page."""
    magic = host.check_output("head -c 4 /root/.local/bin/perlnavigator | od -An -c | tr -d ' '")
    assert magic == "177ELF"
