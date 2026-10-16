def test_codespell_package(host):
    """codespell is installed from the package manager."""
    assert host.package("codespell").is_installed


def test_codespell_runs(host):
    """codespell reports its version."""
    cmd = host.run("codespell --version")
    assert cmd.rc == 0, cmd.stderr


def test_codespell_finds_a_typo(host):
    """codespell reports a misspelled word and exits with a non-zero code."""
    typo = "occ" + "ured"  # not written in one piece, the codespell hook of this repository would flag it
    host.run(f"printf '{typo} word\\n' > /tmp/typo.txt")
    cmd = host.run("codespell /tmp/typo.txt")
    assert cmd.rc != 0
    assert f"{typo} ==> occurred" in cmd.stdout
