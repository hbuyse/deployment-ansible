def test_wlprop_script(host):
    """The wlprop script is downloaded in ~/.local/bin, executable, and is a shell script."""
    script = host.file("/root/.local/bin/wlprop")
    assert script.is_file
    assert oct(script.mode) == "0o755"
    assert script.content_string.startswith("#!")
