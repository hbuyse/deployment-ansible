# Arch installs the Perl scripts outside of the default PATH, /etc/profile.d adds them for login shells
PERL_PATH = "PATH=$PATH:/usr/bin/vendor_perl:/usr/bin/site_perl:/usr/bin/core_perl"


def test_perltidy_runs(host):
    """perltidy reports its version."""
    cmd = host.run(f"{PERL_PATH} perltidy --version")
    assert cmd.rc == 0, cmd.stderr
    assert "perltidy" in cmd.stdout.lower()


def test_perltidy_formats_perl(host):
    """perltidy adds the spaces and line breaks of the default style."""
    cmd = host.run(f"echo 'if($a){{print 1}}' | {PERL_PATH} perltidy")
    assert cmd.rc == 0, cmd.stderr
    assert "if ($a) {" in cmd.stdout
