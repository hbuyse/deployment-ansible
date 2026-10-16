def test_npm_package_is_installed(host):
    """The npm package of the role is installed globally.

    It is a library and provides no command: the role does not give a language server that can be started.
    """
    assert "vscode-markdown-languageserver@" in host.check_output("npm ls -g --depth=0")
